from . import dot, cli

def setup_parser(parser):
    dot.setup_common_parser(parser)
    parser.set_defaults(func=cmd)

def cmd(args):
    dot.cmd_common(args, subdir='path')
