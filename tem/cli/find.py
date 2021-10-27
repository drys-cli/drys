import os

from .. import env, util, repo
from . import common as cli
from .common import print_cli_err, print_cli_warn

# TODO DOCUMENT IN MANPAGE


def setup_parser(parser):
    cli.add_general_options(parser)

    # TODO turn some of these into general options
    # TODO change the purpose of --root
    # (make it the directory that we are looking from)
    # but specify temdirs using another option
    parser.add_argument(
        "-r",  # TODO swap with "-R"
        "--root",
        action="append",
        metavar="DIR",
        help="find rootdir named DIR",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="print more details"
    )
    cli.add_edit_options(parser)
    parser.add_argument("templates", help="templates to find", nargs="*")


@cli.subcommand
def cmd(args):
    # TODO Add tests for this subcommand
    # TODO consider a way to make this work with coreutils 'find' or 'fd'
    # TODO Option '--verbose' unimplemented
    # TODO Rework: Do not use directory structure to obtain info, but
    # TODO Handle explicit paths differently
    # use the TEM_ENV environment variable (this variable is not yet used by
    # any commands)

    result_paths = []

    # No options given, print the closest tem rootdir (TODO document)
    if not args.root and not args.templates:
        if args.verbose:
            cli.print_err("Root directories:")  # TODO add coloring
        result_paths += util.get_parents_with_subdir(os.getcwd(), ".tem/env")

    if args.root:  # --root option
        if args.verbose:
            cli.print_err("Root directories:")  # TODO add coloring
        temdirs_with_env = util.get_parents_with_subdir(
            os.getcwd(), ".tem/env"
        )
        # Print all directories with basenames that match those given to
        # --root
        args.root[:] = list(dict.fromkeys(args.root))
        for directory in temdirs_with_env:
            for searched_directory in args.root:
                if os.path.basename(directory) == searched_directory:
                    result_paths.append(directory)

    if args.templates:  # templates specified as positional arguments
        for template in args.templates:
            paths = repo.find_template(template)
            result_paths += paths

    if args.edit or args.editor:
        cli.try_open_in_editor(result_paths)

    print(*result_paths, sep="\n")
