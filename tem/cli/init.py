"""tem init subcommand"""
import glob
import os
import subprocess

from tem.fs import TemDir
from tem.cli import common as cli
from tem import errors


def setup_parser(parser):
    """Set up argument parser for this subcommand."""
    cli.add_general_options(parser)

    parser.add_argument(
        "-H",
        "--example-hooks",
        action="store_true",
        help="generate documented example hooks",
    )
    parser.add_argument(
        "-n",
        "--example-env",
        action="store_true",
        help="generate documented example environment scripts",
    )
    parser.add_argument(
        "-r",
        "--as-repo",
        action="store_true",
        help="initialize current directory as a repository",
    )
    cli.add_edit_options(parser)
    parser.add_argument(
        "-f", "--force", action="store_true", help="do not fail if .tem exists"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="show the generated file tree",
    )
    # TODO a couple more options
    #  p.add_argument('-m', '--merge', action='store_true',
    #  help='merge with existing')


@cli.subcommand
def cmd(args):
    """Execute this subcommand."""
    TemDir.init(os.getcwd(), force=args.force)
    print("Initialization was successful.")
    if args.verbose:
        # If 'tree' command exists, show the generated tree
        try:
            p = subprocess.run(
                ["tree", "--noreport", "-F", ".tem/"],
                encoding="utf-8",
                stdout=subprocess.PIPE,
                check=False,
            )

            print("Generated tree:")
            print(p.stdout)
            print("Legend:\n\t/ directory\n\t* executable file")
        except FileNotFoundError:
            print("tem: info: install 'tree' for more verbose output")
    if args.edit or args.editor:
        files = [f for f in glob.iglob("**/*", recursive=True) if os.path.isfile(f)]
        p = cli.try_open_in_editor(files, override_editor=args.editor)
