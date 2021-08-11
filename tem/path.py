from . import dot, cli

def setup_parser(subparsers):
    p = subparsers.add_parser('path', add_help=False,
                              help='run or modify the local path');

    dot.setup_common_parser(p)
    p.set_defaults(func=cmd)

@cli.subcommand_routine('path')
def cmd(args):
    dot.cmd_common(args, subdir='path')
