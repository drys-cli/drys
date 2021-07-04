from . import common, util
from .util import print_cli_err, print_cli_warn

def setup_parser_intermediate(subparsers, command, help):
    p = subparsers.add_parser(command, add_help=False, help=help)

    # Action options
    _action_opts = p.add_argument_group('action options')
    action_opts = _action_opts.add_mutually_exclusive_group()
    action_opts.add_argument('-x', '--exec', action='store_true',
                             help='execute files (default)')
    action_opts.add_argument('-n', '--new', action='store_true',
                             help='create a new empty file in the appropriate subdirectory')
    action_opts.add_argument('-a', '--add', action='store_true',
                             help='files will be copied to the appropriate .tem subdirectory')
    action_opts.add_argument('-D', '--delete', action='store_true',
                             help='matching files will be deleted')
    _action_opts.add_argument('-l', '--list', action='store_true',
                             help='list matching FILES')
    common.add_edit_options(action_opts)

    # Modifier options
    modifier_opts = p.add_argument_group('modifier options')
    modifier_opts.add_argument('-t', '--template', action='append',
                               help='use TEMPLATE as root directory')
    modifier_opts.add_argument('-v', '--verbose', action='store_true',
                               help='report successful and unsuccessful runs')
    modifier_opts.add_argument('-f', '--force', action='store_true',
                               help="perform action disregarding warnings")
    modifier_opts.add_argument('-r', '--recursive', action='store_true',
                               help='recurse up the directory tree')
    modifier_opts.add_argument('-I', '--ignore', metavar='FILE', default=[],
                               help='ignore FILE')
    # TODO rm from here [*]
    modifier_opts.add_argument('--subdir', metavar='SUB',
                       help='subdirectory under .tem/ to use')
    modifier_opts.add_argument('--root', metavar='SUB',
                       help='root directory override')


    p.add_argument('files', metavar='FILES', nargs='*', default=[],
                   help='files to operate on (default: all files in .tem/env/)')

    common.add_common_options(p)

    return p, modifier_opts

def setup_parser(subparsers):
    p, modifier_opts = setup_parser_intermediate(
        subparsers, 'dot', help='manipulate files in the .tem/ subdirectory'
    )

    # TODO place here [*]
    p.set_defaults(func=cmd)

@common.subcommand_routine('env')
def cmd(args):
    # TODO implement with reference to env.py
    if not (args.new or args.add or args.edit or args.editor or args.list):
        args.exec = True

    if args.template:
        repos = common.resolve_and_validate_repos(args.repo, cmd='')
