"""Execute programs in a tem-smart way."""

import argparse
import subprocess

from tem import TemDir
from tem.cli import common as cli
from argparse import ArgumentParser

from tem.env import ExecPath
from tem.fs import Executable


def setup_parser(p: ArgumentParser):
    p.add_argument("script", help="script to run, relative to '.tem/path/'")
    p.add_argument(
        "arguments",
        nargs=argparse.REMAINDER,
        metavar="...",
        help="additional arguments passed to the script",
    )
    p.add_argument(
        "-f",
        "--find",
        action="store_true",
        help="find and print the executable without running it",
    )
    p.add_argument(
        "-T",
        "--temdir",
        metavar="DIR",
        help="alternate temdir where script should be looked up",
    )
    p.add_argument(
        "-n",
        "--no-tem",
        action="store_true",
        help="look up the script in the usual PATH, ignoring tem",
    )
    cli.add_general_options(p)


@cli.subcommand
def cmd(args):
    temdir = TemDir(args.temdir)
    if args.no_tem:
        if args.find:
            print(ExecPath()[ExecPath.NO_TEM][args.script].lookup())
        else:
            subprocess.run([args.script, *args], check=False)
    else:
        executable = Executable(temdir["path"] / args.script)
        if args.find:
            print(str(executable.absolute()))
        else:
            subprocess.run([str(executable.absolute()), *args], check=False)
