import argparse
import os, sys
import shutil as sh

from . import common, util
from .common import cfg
from . import __prefix__

def setup_parser(subparsers):
    p = subparsers.add_parser('config', add_help=False,
                              help='get and set repository or global options')
    common.add_common_options(p)

    p.add_argument('-f', '--file', action='append', default=[],
                   help='configuration file that will be used (can be specified multiple times')
    p.add_argument('-g', '--global', dest='glob', action='store_true',
                   help='global configuration file will be used')
    p.add_argument('-s', '--system', action='store_true',
                   help='system configuration file will be used')
    p.add_argument('-l', '--local', action='store_true',
                   help='local repository configuration file will be used')
    common.add_edit_options(p)
    p.add_argument('-i', '--instance', action='store_true',
                   help='print OPTIONs that are active in the running instance')
    p.add_argument('--user-init', action='store_true',
                   help='initialize config at ~/.config/tem')

    p.add_argument('option', metavar='OPTION', nargs='?',
                   help='configuration option to get or set')
    p.add_argument('value', metavar='VALUE', nargs='*',
                   help='value for the specified configuration OPTION')

    p.set_defaults(func=cmd)

def determine_config_files_from_args(args):
    files = []
    local_config = './.tem/config'
    if args.file:
        files += args.file
    if args.local or not (args.instance or args.glob or args.system or args.file):
        files.append(local_config)
    if args.glob:
        files.append(os.path.expanduser('~/.config/tem/config'))
    if args.system:
        files.append(__prefix__ + '/share/tem/config') # TODO
    return files

def user_init():
    dest = os.path.expanduser('~/.config/tem/config')
    if os.path.exists(dest):
        print("Warning: file '" + dest + "' already exists. Overwrite? [Y/n]")
        answer = input()
        if answer and answer.lower() != 'y':
            exit(1)
    util.copy(__prefix__ + '/share/tem/config', dest)

def cmd(args):
    files = determine_config_files_from_args(args)

    if args.user_init:              # --user-init
        user_init()
    elif args.edit or args.editor:
        p = common.try_open_in_editor(files, override_editor=args.editor)
        exit(p.returncode)
    elif args.option:                       # A config option was specified
        # Form value by concatenating arguments
        value = ' '.join(args.value) if args.value else ''
        # Write the configuration to all config files
        for file in files:
            # Parse the file's original contents
            cfg = util.ConfigParser(file)
            # Set the option's value to the one specified
            cfg[args.option] = value
            if not os.path.exists(os.path.dirname(file)):
                os.makedirs(os.path.dirname(file))
            # Write the changes
            with open(file, 'w') as file_object:
                cfg.write(file_object)
    else:                                   # No config options were specified
        # We add an imaginary file that contains all the configuration that has
        # been loaded into this instance of the program
        if args.instance:
            files.insert(0, None)
        for file in files:
            if file and not os.path.isfile(file):
                print('warning: file ' + file + ' does not exist',
                      file=sys.stderr)
            else:
                if file:
                    cfg = util.ConfigParser(file)
                else:
                    cfg = common.cfg
                fname = util.shortpath(file)
                print((fname if fname else 'INSTANCE') + ':')
                for sec in cfg.sections():
                    for item in cfg.items(sec):
                        print('    ', sec + '.' + item[0] + ' = ' + item[1], sep='')
