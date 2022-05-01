"""Execute programs in a tem-smart way."""

import argparse

from tem import run, TemDir
from tem.cli import common as cli
from argparse import ArgumentParser


def setup_parser(p: ArgumentParser):
    p.add_argument("script", help="script to run, relative to '.tem/'")
    p.add_argument(
        "arguments", nargs=argparse.REMAINDER, help="additional call arguments"
    )
    p.add_argument(
        "-T",
        "--temdir",
        help="alternate temdir where script should be looked up",
    )
    cli.add_general_options(p)


@cli.subcommand
def cmd(args):
    run.run(args.script, *args.arguments, temdir=TemDir(args.workspace))
