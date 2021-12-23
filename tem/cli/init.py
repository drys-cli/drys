"""tem init subcommand"""
import glob
import os
import shutil as sh
import subprocess
import sys

from tem import __prefix__, errors
from tem.cli import common as cli


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

    # Make sure that .tem/ is valid before doing anything else
    if os.path.exists(".tem"):
        if args.force:
            if not os.path.isdir(".tem"):
                os.remove(".tem")  # Remove existing file
        else:  # Refuse to init if .tem exists
            raise errors.TemInitializedError(os.getcwd())

    files = []  # Keeps track of all files that have been copied
    # Copy the files
    try:
        SHARE_DIR = __prefix__ + "/share/tem/"
        os.mkdir(".tem")
        os.mkdir(".tem/path")
        os.mkdir(".tem/hooks")
        os.mkdir(".tem/env")
        # Create a list of files that will be copied
        files = [SHARE_DIR + file for file in ["config", "ignore"]]
        if args.as_repo:
            files.append(SHARE_DIR + "repo")
        if args.example_hooks:
            files += glob.glob(SHARE_DIR + "hooks/*")
        if args.example_env:
            files += glob.glob(SHARE_DIR + "env/*")
        # Copy files to .tem/
        for i, file in enumerate(files):
            dest = sh.copy(file, ".tem/" + file.replace(SHARE_DIR, ""))
            files[i] = dest
    except Exception as e:
        cli.print_error_from_exception(e)

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
        except Exception:
            pass
    if args.edit or args.editor:
        p = cli.try_open_in_editor(files, override_editor=args.editor)
