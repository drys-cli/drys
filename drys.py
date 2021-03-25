#!/usr/bin/env python3

path = '~/templates/'

import drys
from drys import common
from drys import add
from drys import ls

import argparse

# drys add <file>
# drys rm <file> --wipe
# drys cd <file|dir>
# drys where <file|dir>
# drys link <target file|dir> <symlink>     # alias ln
# drys ls                                   # alias list
# drys import 
# drys repo

def cmd_drys(parser, args):
    print('the root command was called')

parser = argparse.ArgumentParser()
common.add_common_options(parser)
parser.set_defaults(func=cmd_drys)

sub = parser.add_subparsers(title='commands', metavar='')

# Setup subcommand parsers
add.setup_parser(sub)
ls.setup_parser(sub)

# sub.add_parser('rm',    help='remove files or directories')
# sub.add_parser('open',  help='open a file')
# sub.add_parser('find',  help='find a file or directory')
# sub.add_parser('ln')

# Some sub-commands like 'ls' call system commands, passing any extra arguments
# to them. That is why we do not want an error when the user specifies arguments
# that are not defined in the sub-command's parser. For other commands, we want
# an error when the user specifies arguments that are unrecognized by the
# parser, so we let each call parser.parse_args if needed.
args = parser.parse_known_args()

args[0].func(parser, args[0])

