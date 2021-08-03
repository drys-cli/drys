import sys, os, shutil
import re
import argparse

from . import util
from .util import print_cli_err

repo_path = []

cfg = util.ConfigParser()

ENV_XDG_CONFIG_HOME = os.environ.get('XDG_CONFIG_HOME')
ENV_TEM_CONFIG     = os.environ.get('TEM_CONFIG')

# All possible user configuration files in the order in which they are loaded
user_config_paths = [
    os.path.expanduser('~/.config/tem/config'),
    os.path.expanduser('~/.temconfig'),
    ENV_XDG_CONFIG_HOME + '/tem/config' if ENV_XDG_CONFIG_HOME else '',
    ENV_TEM_CONFIG if ENV_TEM_CONFIG else ''
]

from . import __prefix__
default_config_paths = [__prefix__ + '/share/tem/config'] + user_config_paths

def get_user_config_path():
    lst = [ user_config_paths[i] for i in [3,2,0,1] ]
    return next(path for path in lst if path)

def load_config(paths=[], read_defaults=True):
    """
    Load configuration from `default_config_paths` (if `read_defaults==True`)
    and from `paths` in that order, together we shall call them `all_paths`. If
    there are files from `paths` that can't be read, the program exits with an
    error. Otherwise if `paths` is empty and none of the `default_config_paths`
    can be read, a warning is shown. In all other cases the function finishes
    succesfully, even if some of the files from `default_config_paths` can't be
    read.
    """
    global cfg

    paths = paths.copy()

    all_paths = []
    if read_defaults:
        all_paths =  default_config_paths
    all_paths += paths

    # No paths are left to read config from
    if not all_paths:
        return
    successful = cfg.read(all_paths)

    failed_from_options = set(paths) - set(successful)
    if failed_from_options:               # Some of the `paths` could not be read
        print_cli_err('the following of the specified configuration files could not be read:',
              *failed_from_options, sep='\n\t')
        quit(1)
    elif not successful:                # No config file could be read
        print('Warning: No configuration file on the system could be read.',
              'Please check if they exist or if their permissions are wrong.',
              file=sys.stderr, sep='\n')
    else:                               # No problems
        global repo_path
        repo_path = repo_path_from_config(cfg)

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
    group = parser.add_argument_group('general options')
    group.add_argument('-h', '--help', action='help',
                   help='show this help message and exit')
    group.add_argument('-R', '--repo', action='append', default=[],
                        help='use the repository REPO')
    group.add_argument('-c', '--config', metavar='FILE',
                        action='append', default=[],
                        help='use configuration from FILE')

def add_edit_options(parser):
    """Add '--edit' and '--editor' options to `parser`."""
    parser.add_argument('-e', '--edit', action='store_true',
                   help='open target files for editing')
    parser.add_argument('-E', '--editor',
                   help='same as -e but override editor with EDITOR')

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

# TODO change this concept later
def repo_path_from_config(config):
    if not config:
        return []
    return [ os.path.expanduser(repo) for repo in
            cfg['general.repo_path'].split('\n')
            if repo ]

def resolve_and_validate_repos(repo_args, cmd=None):
    """
    Form a list of repo IDs that shall be used in the currently running
    subcommand. Repos from `repo_args` are arguments to the `--repo` options
    passed to the subcommand. Every applicable repository is considered,
    including those from any applicable configuration files. A repo id can be a
    repo name, a path or a special character (see manpages).
    """
    global repo_path
    repo_ids = []

    # Parse arguments into a suitable list of entries
    if repo_args:                        # repos specified with -R/--repo option
        include_def_repos = False
        read_from_stdin = False
        for repo in repo_args:
            if repo == '/':             # '/' is a special indicator
                include_def_repos = True
            elif '\n' in repo:          # multiline text, each line is a repo id
                repo_ids += [ line for line in repo.split('\n') if line != '']
            elif repo == '-':           # Repos will be taken from stdin as well
                read_from_stdin = True
            else:                       # Regular repo id, just add it
                repo_ids.append(repo)
        if include_def_repos:           # Include default repos
            repo_ids += repo_path
        if read_from_stdin:
            try:
                while True:             # Read repos until empty line or EOF
                    line = input()
                    if line == '':
                        break
                    repo_ids.append(line)
            except EOFError:
                pass
    else:                               # No repos were specified by -R/--repo
        repo_ids = repo_path

    # Resolve the entries to valid file-like objects
    resolved_repos = []                 # this will be returned
    any_repo_valid = False              # indicates if any repo_ids are valid
    for repo in repo_ids:
        if os.path.exists(r := util.resolve_repo(repo)):
            any_repo_valid = True
            resolved_repos.append(r)
        else:
            print("tem: warning: repository '{}' not valid".format(repo),
                  file=sys.stderr)
    if not any_repo_valid:
        print('tem: error: no valid repositories', file=sys.stderr)
        exit(1)

    return resolved_repos

def get_editor(override=None, default='vim'):
    global cfg
    editors = [override,
               cfg['general.editor'],
               os.environ.get('EDITOR') if os.environ.get('EDITOR') else None,
               os.environ.get('VISUAL') if os.environ.get('VISUAL') else None,
               default]
    return next(ed for ed in editors if ed)

def try_open_in_editor(files, override_editor=None):
    """
    Open `files` in editor. If `override_editor` is specified then that is used.
    Otherwise, the editor is looked up in the configuration. The editor can be
    any string that the shell can parse into a list of arguments (e.g. 'vim -o'
    is valid). If the editor cannot be found, print an error and exit.
    """
    from . import ext
    import subprocess, shutil
    call_args = ext.parse_args(get_editor(override_editor)) + files

    if not shutil.which(call_args[0]):
        print("tem config: error: invalid editor: '" + call_args[0] + "'",
              file=sys.stderr)
        exit(1)
    try:
        p = subprocess.run(call_args)
        return p
    except Exception as e:
        util.print_error_from_exception(e)
        exit(1)

def run_hooks(trigger, src_dir, dest_dir='.', environment=None):
    """For reference look at tem-hooks(1) manpage."""
    import glob, subprocess

    src_dir = util.abspath(src_dir)

    # Setup environment variables that the hooks can use
    if environment != None:
        if 'TEM_TEMPLATEDIR' not in environment:
            environment['TEM_TEMPLATEDIR'] = src_dir
        environment['PATH'] = src_dir + '/.tem/path:' + os.environ['PATH']
        for var, value in environment.items():
            os.environ[var] = value

    os.makedirs(dest_dir, exist_ok=True)

    with util.chdir(dest_dir):
        # Execute matching hooks
        for file in glob.glob(src_dir + '/.tem/hooks/*.{}'.format(trigger)):
            subprocess.run([file] + sys.argv, cwd=os.path.dirname(file))

def subcommand_routine(subcommand_name):
    """Decorator for functions that implement subcommand functionality."""
    def decorator(function):
        def wrapper(*args, **kwargs):
            if subcommand_name:
                util._active_subcommand = 'tem ' + subcommand_name
            function(*args, **kwargs)
        return wrapper
    return decorator
