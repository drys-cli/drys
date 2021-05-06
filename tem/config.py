import argparse
import configparser
import os, sys
import shutil as sh

from . import common
from .common import cfg
from . import __prefix__

def setup_parser(subparsers):
    p = subparsers.add_parser('config', help='Get and set repository or global options')
    common.add_common_options(p)

    p.add_argument('-f', '--file', action='append', default=[],
                   help='configuration file that will be used (can be specified multiple times')
    p.add_argument('-g', '--global', dest='glob', action='store_true',
                   help='global configuration file will be used')
    p.add_argument('-s', '--system', action='store_true',
                   help='system configuration file will be used')
    p.add_argument('-l', '--local', action='store_true',
                   help='local repository configuration file will be used')
    p.add_argument('-e', '--edit', action='store_true',
                   help='edit the file(s) in $EDITOR')
    p.add_argument('-E', '--editor', help='editor to use instead of $EDITOR')
    p.add_argument('-i', '--instance', action='store_true',
                   help='print config options that are active in the running instance')
    p.add_argument('--user-init', action='store_true',
                   help='initialize config at ~/.config/tem')

    p.add_argument('option', nargs='?', help='configuration option to get or set')
    p.add_argument('value', nargs='*', help='value for the specified configuration option')

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

def get_section_and_name(full_name):
    split = full_name.split('.', maxsplit=1)
    option = split[-1]
    if len(split) == 1: section = 'general'
    else:               section = split[0]
    return section, option

# TODO add this to a class derived from ConfigParser
def set_option_carefree(cfg, section, option, value):
    """
    Convenience function. Same as cfg.set(section, option, value), but never
    throws an error. Missing sections are generated automatically and if the
    option already exists it will be overwritten.
    """
    if not cfg.has_section(section):
        cfg[section] = { option: value }
    else:
        cfg[section][option] = value

def user_init():
    dest = os.path.expanduser('~/.config/tem/config')
    if os.path.exists(dest):
        print("Warning: file '" + dest + "' already exists. Overwrite? [Y/n]")
        answer = input()
        if answer and answer.lower() != 'y':
            exit(1)
    sh.copy(__prefix__ + '/share/tem/config', dest)

def cmd(parser, args):
    files = determine_config_files_from_args(args)

    if args.user_init:
        user_init()
    elif args.edit:
        from .common import cfg
        editors = [args.editor,
                   cfg.get('general', 'editor', fallback=None),
                   os.environ.get('EDITOR') if os.environ.get('EDITOR') else None,
                   os.environ.get('VISUAL') if os.environ.get('VISUAL') else None,
                   'vim']
        # Get the first editor that is not None
        editor = next(ed for ed in editors if ed != None)
        from . import ext; import subprocess as sp;
        call_args = ext.parse_args(editor) + files
        # Check if the executable exists
        if not sh.which(editor):
            print("tem config: error: invalid editor: '" + call_args[0] + "'",
                  file=sys.stderr)
            exit(1)
        try:
            p = sp.run(call_args)
        except Exception as e:
            common.print_error_from_exception(e)
            exit(1)
        exit(p.returncode)
    elif args.option:                       # A config option was specified
        # Extract and separate section name and option name
        section, option = get_section_and_name(args.option)
        # Form value by concatenating arguments
        value = ' '.join(args.value) if args.value else ''
        # Write the configuration to all config files
        for file in files:
            # Parse the file's original contents
            cfg = configparser.ConfigParser()
            cfg.read(file)
            # Set the option's value to the one specified
            set_option_carefree(cfg, section, option, value)
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
                    cfg = configparser.ConfigParser()
                    cfg.read(file)
                else:
                    cfg = common.cfg
                print((file if file else 'INSTANCE') + ':')
                for sec in cfg.sections():
                    for item in cfg.items(sec):
                        print('    ', sec + '.' + item[0] + ' = ' + item[1], sep='')
