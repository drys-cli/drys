import sys, os, shutil
import re
import argparse
import configparser

from . import __prefix__

default_repos = []

ENV_XDG_CONFIG_HOME = os.environ.get('XDG_CONFIG_HOME')
ENV_DRYS_CONFIG     = os.environ.get('DRYS_CONFIG')

# All possible user configuration files in their lookup order
user_config_paths = [
    os.path.expanduser('~/.config/tem/config'),
    os.path.expanduser('~/.temconfig'),
    ENV_XDG_CONFIG_HOME + '/tem/config' if ENV_XDG_CONFIG_HOME else '',
    ENV_DRYS_CONFIG if ENV_DRYS_CONFIG else ''
]

def get_user_config_path():
    lst = [ user_config_paths[i] for i in [3,2,0,1] ]
    return next(path for path in lst if path)

default_config_paths = [__prefix__ + '/share/tem/config'] + user_config_paths

aliases = {}

cfg = configparser.ConfigParser()

def print_error_from_exception(e):
    print('tem: error:', re.sub(r'^\[Errno [0-9]*\] ', '', str(e)), file=sys.stderr)

def copy(src, dest='.', ignore_nonexistent=False):
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
        if not ignore_nonexistent:
            print_error_from_exception(e)
            exit(1)

def move(src, dest, ignore_nonexistent=False):
    try:
        return shutil.move(src, dest)
    except Exception as e:
        if not ignore_nonexistent:
            print_error_from_exception(e)
            exit(1)

def remove(path):
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
    except Exception as e:
        print_error_from_exception(e)
        exit(1)

# TODO remove this method (why did I want to remove it??)
def add_common_options(parser, main_parser=False):
    """
    Add options that are common among various commands. By default, when a
    subcommand is called, all options that are defined for the main command are
    valid but they must be specified before the subcommand name. By using this
    function with each subcommand, the option can be specified after the
    subcommand name.
    """
    # TODO remove this after a tryout period
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
    else:                               # No problems
        global default_repos
        default_repos = default_repos_from_config(cfg)

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

def resolve_repo(repo_id, lookup_repos=None):
    """
    Resolve a repo id (path, partial path or name) to the absolute path of a
    repo.
    """
    if not repo_id:
        return ''
    # Path is absolute or explicitly relative (starts with . or ..)
    if repo_id[0] == '/' or repo_id in ['.', '..'] or re.match(r'\.\.*/', repo_id):
        return repo_id

    # Otherwise try to find a repo whose name is `repo_id`
    if not lookup_repos:
        global default_repos
        lookup_repos = default_repos

    for repo in lookup_repos:
        if os.path.exists(repo) and fetch_name(repo) == repo_id:
            return os.path.abspath(repo)

    # If all else fails, try to find a repo whose basename is equal to `path`
    for repo in lookup_repos:
        if os.path.basename(repo) == repo_id:
            return repo

    # The `path` is so fabulously wrong, nothing can be done with it
    return repo_id

# TODO change this concept later
def default_repos_from_config(config):
    if not config:
        return []
    return [ os.path.expanduser(repo) for repo in
            cfg.get('general', 'default_repos', fallback='').split('\n') ]

def form_repo_list(repo_ids, cmd=None):
    # TODO command-specific default repos
    global default_repos
    repos = []

    if repo_ids:                        # repos specified with -R/--repo option
        include_def_repos = False
        read_from_stdin = False
        for repo in repo_ids:
            if repo == '/':             # '/' is a special indicator
                include_def_repos = True
            elif '\n' in repo:         # multiline text, each line is a repo
                repos += [ line for line in repo.split('\n') if line != '']
            elif repo == '-':           # Repos will be taken from stdin as well
                read_from_stdin = True
            else:                       # Regular repo id, just add it
                repos.append(repo)
        if include_def_repos:           # Include default repos
            repos += default_repos
        if read_from_stdin:
            try:
                while True:             # Read repos until empty line or EOF
                    line = input()
                    if line == '':
                        break
                    repos.append(line)
            except EOFError:
                pass
    else:                               # No repos were specified by -R/--repo
        repos = default_repos

    return repos

def fetch_name(repo_path):
    import configparser
    cfg = configparser.ConfigParser(default_section='general')
    cfg.read(repo_path + '/.tem/repo')
    name = cfg.get('general', 'name', fallback=None)
    if name:
        return name
    else:
        return os.path.basename(os.path.abspath(repo_path))

def resolve_and_validate_repos(repo_ids):
    resolved_repos = []         # this will be returned
    any_repo_valid = False      # indicates if any repo_ids are valid
    for repo in repo_ids:
        if os.path.exists(r := resolve_repo(repo)):
            any_repo_valid = True
            resolved_repos.append(r)
        else:
            print("tem: warning: repository '{}' not valid".format(repo),
                  file=sys.stderr)
    if not any_repo_valid:
        print('tem: error: no valid repositories', file=sys.stderr)
        exit(1)

    return resolved_repos
