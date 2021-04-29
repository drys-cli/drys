import sys, os, shutil
import re
import argparse
import configparser

repos = [ os.path.expanduser('~/.local/share/drys/repo') ]

ENV_XDG_CONFIG_HOME = os.environ.get('XDG_CONFIG_HOME')
ENV_DRYS_CONFIG     = os.environ.get('DRYS_CONFIG')

default_config_paths = [
    '/usr/share/drys/config',
    os.path.expanduser('~/.config/drys/config'),
    os.path.expanduser('~/.drysconfig'),
    ENV_XDG_CONFIG_HOME + '/drys/config' if ENV_XDG_CONFIG_HOME else '',
    ENV_DRYS_CONFIG if ENV_DRYS_CONFIG else ''
]

aliases = {}

cfg = configparser.ConfigParser()

def print_error_from_exception(e):
    print('error:', re.sub(r'^\[Errno [0-9]*\] ', '', str(e)), file=sys.stderr)

def copy(src, dest='.'):
    dirname = os.path.dirname(dest)
    if dirname and not os.path.exists(dirname):
        os.makedirs(dirname, exist_ok=True)
    try:
        if os.path.isdir(src):
            return shutil.copytree(src, dest,
                            dirs_exist_ok=True, copy_function=shutil.copy)
        else:
            return shutil.copy(src, dest)
    except Exception as e:
        print_error_from_exception(e)
        exit(1)

def move(src, dest):
    try:
        return shutil.move(src, dest)
    except Exception as e:
        print_error_from_exception(e)
        exit(1)

# TODO remove this method
def add_common_options(parser, main_parser=False):
    """
    Add options that are common among various commands. By default, when a
    subcommand is called, all options that are defined for the main command are
    valid but they must be specified before the subcommand name. By using this
    function with each subcommand, the option can be specified after the
    subcommand name.
    """
    config_dest = 'config' if main_parser else '_config'
    parser.add_argument('-c', '--config', dest=config_dest, metavar='FILE',
                        action='append', default=[],
                        help='Use the specified configuration file')
    parser.add_argument('-R', '--repo', action='append', default=[],
                        help='use the repository REPO (can be used multiple times)')
    # A special None value indicates that all previous config paths should be
    # ignored
    parser.add_argument('--reconfigure', dest='config',
                        action='append_const', const=None,
                        help='Discard any configuration loaded before reading this option')

def load_config(paths=[], read_defaults=True):
    """
    Load configuration from `default_config_paths` (if `read_defaults==True`)
    and from `paths` in that order, together we shall call them `all_paths`. If
    there are files from `paths` that can't be read, the program exits with an
    error. Otherwise if `paths` is empty and none of the `default_config_paths`
    can be read, a warning is shown. In all other cases the function finishes
    succesfully, even if some of the files from `default_config_paths` can't be
    read.

    Note: A None item inside `paths` indicates that the '--reconfigure' option
    was specified. This will cause all paths up to that index to be ignored.
    """
    global cfg, aliases

    paths = paths.copy()
    reconfigured_at_least_once = False
    # Each ocurrence of None is an ocurrence of the '--reconfigure' option
    # Delete everything up to (and including) the last ocurrence of None
    for i in reversed(range(len(paths))):
        if paths[i] == None:
            del paths[0:i+1]
            reconfigured_at_least_once = True
            break

    all_paths = []
    if read_defaults and not reconfigured_at_least_once:
        all_paths =  default_config_paths
    all_paths += paths

    # No paths are left to read config from
    if not all_paths:
        return
    successful = cfg.read(all_paths)

    failed_from_paths = set(paths) - set(successful)
    if failed_from_paths:               # Some of the `paths` could not be read
        print("ERROR: The following configuration files could not be read:",
              end='\n\t', file=sys.stderr)
        print(*failed_from_paths, sep='\n\t', file=sys.stderr)
        quit(1)
    elif not successful:                # No config file could be read
        print('Warning: No configuration file on the system could be read.',
              'Please check if they exist or if their permissions are wrong.',
              file=sys.stderr, sep='\n')

def existing_file(path):
    """ Type check for ArgumentParser """
    if not os.path.exists(path):
        raise argparse.ArgumentTypeError(path + ' does not exist')
    else:
        return path

# TODO try to remember where I wanted to use this?
def explicit_path(path):
    """
    If the path is relative, prepend './'. If the path is a directory, append a
    '/'. In all other cases `path` is returned unmodified
    """
    if path and path != '.' and path[0] != '/' and path[0] != '~' \
        and (path[0] != '.' or path[1] != '/'):
        path = './' + path
    if os.path.isdir(path):
        # Append a '/' if it's not there already
        return re.sub(r'([^/])$', r'\1/', path)
    else:
        return path

def add_repo(repo):
    repos.append(repo)
