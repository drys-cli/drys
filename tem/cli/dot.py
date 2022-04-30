"""tem dot subcommand"""
import os
import select
import subprocess
import sys
from typing import List, Iterable

from tem import ext, util, env, errors
from tem.errors import TemError
from tem.util import fs as fs_util

from . import common as cli
from ..fs import AnyPath


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
        raise TemError("subdir must be non-empty")

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
        raise errors.NotADirError(rootdir)
    dotdir = rootdir + "/.tem/" + subdir

    # Validation
    if os.path.exists(dotdir) and not os.path.isdir(dotdir):
        # TODO
        raise errors.DirNotFoundError(dotdir).append(
            "\nTry running `tem init --force`. "
            "Please read the manual before doing that."
        )

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


def create_new_files(dotdir: AnyPath, file_names: Iterable[str], force):
    """Create files with names from ``file_names`` inside ``dotdir``."""
    # TODO This should only be used in some dot derivatives
    # (path, env, maybe others)
    dest_files = []

    # File contents are taken from stdin, if it has data
    contents = util.read_stdin() or ""

    for file in file_names:
        dest = dotdir + "/" + file

        try:
            with fs_util.create_file(dest, permissions=744, force=True) as f:
                f.write(contents)
        except errors.FileExistsError as e:
            raise e.append("\nTry running with --force.")

        dest_files.append(dest)

    return dest_files


def add_existing_files(
    dotdir: str, files: List[str], force: bool, create_symlinks: bool
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
    dest_files: List[str]
        Relative paths to the newly created files.
    """
    dest_files = []
    any_nonexistent = False
    any_conflicts = False
    for src in files:
        dest = dotdir + "/" + util.basename(src)
        if os.path.exists(src):
            if not os.path.exists(dest) or force:
                util.copy(src, dest, symlink=create_symlinks)
            else:
                cli.print_cli_warn(f"file '{dest}' already exists")
                any_conflicts = True
        else:
            cli.print_cli_warn(f"file '{src}' does not exist")
            any_nonexistent = True
        dest_files.append(dest)
    if any_nonexistent or any_conflicts:
        sys.exit(1)

    return dest_files


def execute_files(files, verbose):
    """
    Execute all ``files``.

    Parameters
    ----------
    files
        List of files to execute.
    verbose
        Print each successful file execution.
    """
    env.ExecPath().prepend(".tem/path").export()
    for file in files:
        if os.path.isdir(file):
            continue
        try:
            subprocess.run(file, check=False)
            if verbose:
                cli.print_cli_info(f"script '{file}' was run successfully")
        except Exception:
            cli.print_cli_err(f"script `{file}` could not be run")
            sys.exit(1)


def list_files(dotdir: str, file_names: List[str]):
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


def delete_files(dotdir: str, file_names: List[str]):
    """Delete files from ``file_names`` inside ``dotdir``."""
    any_problems = False
    for file in file_names:
        target_file = dotdir + "/" + file
        if os.path.isfile(target_file):
            os.remove(target_file)
        elif os.path.isdir(target_file):
            cli.print_cli_warn(f"'{target_file}' is a directory")
        else:
            cli.print_cli_warn(f"'{target_file}' does not exist")
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

    if not os.path.exists(dotdir):
        if args.new or args.add or args.symlink:
            os.makedirs(dotdir)
        else:
            return

    if args.new:  # --new
        if not args.files:
            cli.print_cli_err(
                "FILES must not be empty with the '--new' option"
            )
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
                raise TemError("no scripts found")
        elif args.exec:
            execute_files([dotdir + "/" + f for f in file_names], args.verbose)

    if dest_files and (args.edit or args.editor):  # --edit, --editor
        cli.edit_files(dest_files, args.editor)

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
