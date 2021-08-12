import sys, os
import argparse

from . import cli, util, dot
from .util import print_cli_err, print_cli_warn, print_err

def setup_parser(parser):
    dot.setup_common_parser(parser)
    parser.set_defaults(func=cmd)

@cli.subcommand
def cmd(args):
    dot.cmd_common(args, 'env')
