#!/usr/bin/env python3

path = '~/templates/'

import drys
from drys import common
from drys import add
from drys import ls
from drys import put

import argparse, sys

# drys rm <file> --wipe
# drys cd <file|dir>
# drys where <file|dir>
# drys link <target file|dir> <symlink>     # alias ln
# drys ls                                   # alias list
# drys put, ., here
# drys repo

def main():
    argv = sys.argv

    parser = argparse.ArgumentParser()

    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s version TODO')
    common.add_common_options(parser)
    parser.add_argument('--debug', action='store_true',
                        help='start python debugger')
    parser.set_defaults(func=None)

    # Setup subcommand parsers
    sub = parser.add_subparsers(title='commands', metavar='')
    add.setup_parser(sub)
    ls.setup_parser(sub)
    put.setup_parser(sub)

    # TODO figure out how to handle config loading to use aliases
    # Parse arguments before reading config. This allows us to process arguments
    # that can potentially terminate the program immediately (like '--help')
    args = parser.parse_args();

    if args.debug:
        import pudb; pu.db

    # Load configuration, both default and from arguments
    common.load_config(args.config if args.config else [])

    if args.func:
        args.func(parser, args)
