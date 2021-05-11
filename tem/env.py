import sys, os
import argparse

from . import common
from .util import print_err

def setup_parser(subparsers):
    p = subparsers.add_parser('env',
                              help='load environment for current directory')
    common.add_common_options(p)

    p.add_argument('-v', '--verbose', action='store_true',
                   help='report successful and unsuccessful runs')

    p.add_argument('-i', '--ignore', metavar='FILE', help='ignore specified')

    p.set_defaults(func=cmd)

def cmd(parser, args):
    # TODO determine what constitutes a failed run, and what is just a skip
    import subprocess
    if os.path.isdir('.tem/env'):
        ls = os.listdir('.tem/env')
        if not ls:
            print_err('tem: warning: no environment scripts found')
        for file in os.listdir('.tem/env'):
            try:
                subprocess.run('.tem/env/' + file)
                if args.verbose:
                    print_err("tem: info: script `{}` was run successfully"
                              .format(file))
            except:
                if args.verbose:
                    print_err("tem: warning: script `{}` could not be run"
                              .format(file))
    else:
        if os.path.exists('.tem/env'):
            print_err("tem: error: '.tem/env' is not a directory")
        else:
            print_err("tem: error: directory '.tem/env' not found")
        exit(1)
