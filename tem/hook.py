import sys, os
import argparse

from . import common

def setup_parser(subparsers):
    p = subparsers.add_parser('hook', add_help=False,
                              help='operations on command hooks')
    common.add_common_options(p)

    action_opts = p.add_mutually_exclusive_group()
    action_opts.add_argument('-x', '--exec', action='store_true',
                         help='execute HOOKS (default)')
    action_opts.add_argument('-n', '--new', action='store_true',
                         help='create new HOOKS')
    action_opts.add_argument('-a', '--add', action='store_true',
                   help='add specified files as hooks')
    action_opts.add_argument('-l', '--list', action='store_true',
                   help='list hooks')
    common.add_edit_options(p)
    p.add_argument('-f', '--force',
                   help="create .tem/ if it doesn't exist (only when adding hooks)")
    p.add_argument('hooks', metavar='HOOKS', nargs='?',
                   help='the hooks on which to operate')

    p.set_defaults(func=cmd)

@common.subcommand_routine('hook')
def cmd(args):
    # TODO this part is unusable
    # Create a common interface for env and hooks, and potentially other files
    # in the .tem/* subdirectories
    if not (args.new or args.add or args.edit or args.editor or args.list):
        args.exec = True
    if args.new:
        if os.path.exists('.tem'):
            open('.tem/hooks/')
    elif args.add:
        pass # TODO
    if args.list:
        import subprocess; from . import ext
        ls_args = ['ls', '-1']
        os.chdir(env_dir)
        # Without --new and --add options, only display files from `args.hooks`.
        # With --new or --add options, all files will be displayed.
        if not args.new and not args.add:
            ls_args += args.hooks
        p = ext.run(ls_args, encoding='utf-8')
        exit(p.returncode)