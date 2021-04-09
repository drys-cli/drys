#!/usr/bin/env python3

path = '~/templates/'

import drys
from drys import common
from drys import add
from drys import ls
from drys import put

import argparse, sys

# drys add <file>
# drys rm <file> --wipe
# drys cd <file|dir>
# drys where <file|dir>
# drys link <target file|dir> <symlink>     # alias ln
# drys ls                                   # alias list
# drys put, ., here
# drys repo

argv = sys.argv

parser = argparse.ArgumentParser()

parser.add_argument('-v', '--version', action='version',
                    version='%(prog)s version TODO')
common.add_common_options(parser)
parser.set_defaults(func=None)

# Setup subcommand parsers
sub = parser.add_subparsers(title='commands', metavar='')
add_parser  = add.setup_parser(sub)
ls_parser   = ls.setup_parser(sub)
put_parser  = put.setup_parser(sub)

# TODO figure out how to handle config loading to use aliases
# Parse arguments before reading config. This allows us to process arguments
# that can potentially terminate the program immediately (like '--help')
args = parser.parse_args();

# Load default configuration
if args:
    common.load_config(args.config)
else:
    common.load_config()
print(common.config['ls']['command'])

if args.func:
    args.func(parser, args)
