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
    parser.add_argument("templates", help="templates to find", nargs='*')


@cli.subcommand
def cmd(args):
    # TODO Add tests for this subcommand
    # TODO consider a way to make this work with coreutils 'find' or 'fd'
    # TODO Option '--verbose' unimplemented
    # TODO Rework: Do not use directory structure to obtain info, but
    # TODO Handle explicit paths differently
    # use the TEM_ENV environment variable (this variable is not yet used by
    # any commands)

    # No options given, print the closest tem rootdir (TODO document)
    if not args.root and not args.templates:
        if args.verbose:
            cli.print_err("Root directories:")  # TODO add coloring
        print(env.find_temdirs_with_env(os.getcwd())[0])

    if args.root:  # --root option
        if args.verbose:
            cli.print_err("Root directories:")  # TODO add coloring
        temdirs_with_env = env.find_temdirs_with_env(os.getcwd())
        args.root[:] = list(dict.fromkeys(args.root))
        # Print all directories with basenames that match those given to
        # --root
        for directory in temdirs_with_env:
            for searched_directory in args.root:
                if os.path.basename(directory) == searched_directory:
                    print(directory)

    if args.templates:
        for template in args.templates:
            paths = repo.find_template(template)
            for path in paths:
                print(path)
