import sys, os
import argparse

from . import cli, util, dot
from .util import print_cli_err, print_cli_warn, print_err

def setup_parser(subparsers):
    p = subparsers.add_parser('env', add_help=False,
                          help='run or modify local environments')
    dot.setup_common_parser(p)
    p.set_defaults(func=cmd)

def validate_file_arguments_as_script_names(files):
    any_invalid_files = False
    for file in files:
        if '/' in file:
            print_cli_err("file '{}' is invalid".format(file))
            any_invalid_files = True
    if any_invalid_files: exit(1)

@cli.subcommand_routine('env')
def cmd(args):
    dot.cmd_common(args, 'env')
