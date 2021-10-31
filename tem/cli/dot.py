"""tem dot subcommand"""
import os
import select
import shutil
import subprocess
import sys

from tem import ext, repo, util, env
from ..util import print_err
from . import common as cli


def setup_common_parser(parser):
    """
    Set up ``parser`` in a way that is common to all subcommands derived from
    `dot`.
    """
    parser.add_argument(
        "files",
        metavar="FILES",
        nargs="*",
        default=[],
        help="files to operate on",
    )

    # Action options
    action_opts = parser.add_argument_group("action options")
    action_opts_ex = action_opts.add_mutually_exclusive_group()
    action_opts_ex.add_argument(
        "-x", "--exec", action="store_true", help="execute FILES (default)"
    )
    action_opts_ex.add_argument(
        "-n", "--new", action="store_true", help="create new empty FILES"
    )
    action_opts_ex.add_argument(
        "-a", "--add", action="store_true", help="copy FILES"
    )
    action_opts_ex.add_argument(
        "-s",
        "--symlink",
        action="store_true",
        help="like --add but create a symbolic link",
    )
    action_opts_ex.add_argument(
        "-D", "--delete", action="store_true", help="delete FILES"
    )
    action_opts.add_argument(
        "-l", "--list", action="store_true", help="list matching FILES"
    )
    cli.add_edit_options(action_opts)

    # Modifier options
    modifier_opts = parser.add_argument_group("modifier options")
    modifier_opts.add_argument(
        "-T", "--template", help="use TEMPLATE as root directory"
    )
    modifier_opts.add_argument(
        "--root", metavar="DIR", help="override root directory with DIR"
    )
    modifier_opts.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="report successful and unsuccessful runs",
    )
    modifier_opts.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="perform action disregarding warnings",
    )
    modifier_opts.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="recurse up the directory tree",
    )
    modifier_opts.add_argument(
        "-I", "--ignore", metavar="FILE", default=[], help="ignore FILE"
    )

    cli.add_general_options(parser)

    return action_opts, modifier_opts


def setup_parser(parser):
    """Set up argument parser for this subcommand."""
    _, modifier_opts = setup_common_parser(parser)

    modifier_opts.add_argument(
        "--subdir", metavar="SUB", help="subdirectory under .tem/ to use"
    )


def validate_file_arguments_as_script_names(files):
    """
    Verify that ``files`` are base names, i.e. do not contain path delimiters.
    Otherwise, print an error and exit.
    """
    any_invalid_files = False
    for file in files:
        if "/" in file:
            cli.print_cli_err("'{}' is an invalid script name".format(file))
            any_invalid_files = True
    if any_invalid_files:
        sys.exit(1)


def validate_and_get_dotdir(subdir, rootdir=None, recursive=False):
    """
    Make sure that ``rootdir`` and ``subdir`` can form a valid dotdir, and then
    return them in a usable form. A dotdir is a path of the form
    `$rootdir/.tem/$subdir`.
    :param root: directory that contains the `.tem/` subdirectory of interest
    :param subdir: directory under `.tem/`
    :return: resolved ``(rootdir, subdir)`` pair
    .. note::

        If ``rootdir`` is ``None`` and ``recursive`` is ``True``, the
        filesystem is searched upwards until a directory containing
        `.tem/$subdir` is found. That directory will be taken as the rootdir.
        If ``recursive`` is ``False``, cwd will be used as ``rootdir``.
    """
    if not subdir:
        cli.print_cli_err("subdir must be non-empty")
        sys.exit(1)

    if rootdir is None:
        # We have to look upwards for a suitable rootdir
        if recursive:
            cwd = os.getcwd()
            # Find a parent directory with a subdirectory tree as in `subdir`
            while True:
                if os.path.isdir(cwd + "/.tem/" + subdir):
                    # subdir exists under `cwd`
                    rootdir = cwd
                    break
                if cwd == "/":  # dead end
                    cli.print_cli_err("a valid root directory could not found")
                    sys.exit(1)
                cwd = os.path.dirname(cwd)  # Go up one directory
        else:
            rootdir = "."
    elif not os.path.isdir(rootdir):  # rootdir doesn't exist
        cli.print_cli_err("'{}' is not a directory".format(rootdir))
        sys.exit(1)
    dotdir = rootdir + "/.tem/" + subdir

    # Validation
    if not os.path.isdir(dotdir):
        if os.path.exists(dotdir):
            # TODO
            cli.print_cli_err(
                "'{}' exists and is not a directory".format(
                    util.abspath(dotdir)
                )
            )
            print_err(
                "Try running `tem init --force`. "
                "Please read the manual before doing that."
            )
        else:
            cli.print_cli_err("directory '{}' not found".format(dotdir))
            print_err("Try running `tem init` first.")
            sys.exit(1)
        # TODO if args.exec or not args.force: sys.exit(1)

    return rootdir, subdir


def no_action(args):
    """Return True if no action options were specified."""
    return not (
        args.new
        or args.add
        or args.symlink
        or args.edit
        or args.editor
        or args.list
        or args.exec
    )


def create_new_files(dotdir, file_names, force):
    # TODO This should only be used in some dot derivatives
    # (path, env, maybe others)
    dest_files = []
    validate_file_arguments_as_script_names(file_names)
    any_conflicts = False

    # File contents are taken from stdin, if it has data
    contents = ""
    # NOTE: non-portable
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        contents = sys.stdin.read()

    for file in file_names:
        dest = dotdir + "/" + file

        if not os.path.exists(dest) or force:
            with open(dest, "w", encoding="utf-8") as f:
                f.write(contents)
            util.make_file_executable(dest)
        else:
            any_conflicts = True
            cli.print_cli_err("file '{}' already exists".format(dest))
        dest_files.append(dest)

    if any_conflicts:
        print_err("\nTry running with --force.")
        sys.exit(1)

    return dest_files


def add_existing_files(
    dotdir: str, files: list[str], force: bool, create_symlinks: bool
):
    """Copy existing `files` into `dotdir`.

    Parameters
    ----------
    force
        Overwrite existing files.
    create_symlinks
        If True, symlinks will be created instead of hard copies.
    Returns
    -------
    dest_files : list[str]
        Relative paths to the newly created files.
    """
    dest_files = []
    any_nonexisting = False
    any_conflicts = False
    for src in files:
        dest = dotdir + "/" + util.basename(src)
        if os.path.exists(src):
            if not os.path.exists(dest) or force:
                util.copy(src, dest, symlink=create_symlinks)
            else:
                cli.print_cli_warn("file '{}' already exists".format(dest))
                any_conflicts = True
        else:
            cli.print_cli_warn("file '{}' does not exist".format(src))
            any_nonexisting = True
        dest_files.append(dest)
    if any_nonexisting or any_conflicts:
        sys.exit(1)

    return dest_files


def execute_files(files, verbose):
    env.path_prepend_unique(".tem/path")
    for file in files:
        if os.path.isdir(file):
            continue
        try:
            subprocess.run(file, check=False)
            if verbose:
                cli.print_cli_info(
                    "script '{}' was run successfully".format(file)
                )
        except Exception:
            cli.print_cli_err("script `{}` could not be run".format(file))
            sys.exit(1)


def list_files(dotdir: str, file_names: list[str]):
    """
    Parameters
    ----------
    dotdir
        Path to the relevant dotdir.
    file_names
        List of base names of files under `dotdir` that should be listed.
        If empty, all files under `dotdir` will be listed.
    """
    with util.chdir(dotdir):
        ls_args = ["ls", "-1", *file_names]
        p = ext.run(ls_args, encoding="utf-8")
        sys.exit(p.returncode)


def delete_files(dotdir: str, file_names: list[str]):
    any_problems = False
    for file in file_names:
        target_file = dotdir + "/" + file
        if os.path.isfile(target_file):
            os.remove(target_file)
        elif os.path.isdir(target_file):
            cli.print_cli_warn("'{}' is a directory".format(target_file))
        else:
            cli.print_cli_warn("'{}' does not exist".format(target_file))
    if any_problems:
        sys.exit(1)


def cmd_common(args, subdir=None):
    """
    If this is called from a `dot` derivative subcommand, subdir and root
    must be specified as function arguments.
    """
    # TODO implement --template argument
    if subdir is None:
        subdir = args.subdir

    # TODO perhaps not very elegant, but will do for now
    if subdir is not None:
        cli.set_active_subcommand(subdir)

    rootdir, subdir = validate_and_get_dotdir(
        subdir, args.root, recursive=args.recursive
    )
    dotdir = rootdir + "/.tem/" + subdir

    # Exec is the default action if no other actions have been specified
    if no_action(args):
        args.exec = True

    dest_files = []

    if args.new:  # --new
        dest_files += create_new_files(dotdir, args.files, args.force)
    elif args.add or args.symlink:  # --add or --symlink
        add_existing_files(dotdir, args.files, args.force, args.symlink)
    elif args.delete:  # --delete
        delete_files(dotdir, args.files)
    else:
        file_names = args.files
        # If no files are passed as arguments, use all files from the dotdir
        if not file_names:
            file_names = [
                file for file in os.listdir(dotdir) if file not in args.ignore
            ]
        dest_files += [dotdir + "/" + f for f in file_names]
        if not file_names:
            if args.verbose:
                # TODO make this abstract
                cli.print_cli_err("no scripts found")
                sys.exit(1)
        elif args.exec:
            execute_files([dotdir + "/" + f for f in file_names], args.verbose)

    if dest_files and (args.edit or args.editor):  # --edit, --editor
        cli.try_open_in_editor(dest_files, args.editor)

    if args.list:  # --list
        # With --new or --add, all files should be displayed.
        if args.new or args.add:
            file_names = []
        list_files(dotdir, file_names)

    # TODO:
    # --add: handle multiple files with same name


@cli.subcommand
def cmd(*args, **kwargs):
    """Execute this subcommand."""
    return cmd_common(*args, **kwargs)


# TODO will probably be removed in favor of a more universal approach
def _paths_from_templates(args):

    template_paths = []
    for tmpl in args.template:
        template_paths += repo.find_template(tmpl, args.repo, at_most=1)
    if not template_paths:
        cli.print_cli_warn(
            "template '{}' cannot be found".format(args.template)
        )
    return template_paths
