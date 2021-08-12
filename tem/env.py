import sys, os
import argparse

from . import cli, dot

def setup_parser(parser):
    dot.setup_common_parser(parser)
    parser.set_defaults(func=cmd)

def cmd(args):
    dot.cmd_common(args, 'env')
