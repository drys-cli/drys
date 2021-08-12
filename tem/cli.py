import sys, os, shutil
import re
import argparse

from . import util
from .util import print_cli_err, print_cli_warn

repo_path = []

cfg = util.ConfigParser()

XDG_CONFIG_HOME = os.environ.get('XDG_CONFIG_HOME')
TEM_CONFIG      = os.environ.get('TEM_CONFIG')

from . import __prefix__
system_config_paths = [__prefix__ + '/share/tem/config']

"""
All possible user configuration files sorted in the order they should be read.
"""
user_config_paths = [
    os.path.expanduser('~/.config/tem/config'),
    os.path.expanduser('~/.temconfig'),
    XDG_CONFIG_HOME + '/tem/config' if XDG_CONFIG_HOME else '',
    TEM_CONFIG if TEM_CONFIG else ''
]

def get_user_config_path():
    """
    Of all the possible paths for the user configuration, return the one with
    the highest priority.

    .. seealso:: user_config_paths
    """
    lst = [ user_config_paths[i] for i in [3,2,0,1] ]
    return next(path for path in lst if path)

def load_config(paths):
    """
    Load configuration from `paths`, in the specified order. If some of the
    files can't be read, print an error and exit.
    :returns: list of files that could not be read
    """
    if not paths: return

    global cfg, repo_path
    successful = cfg.read(paths)
    repo_path += repo_path_from_config(cfg)
    repo_path = list(dict.fromkeys(repo_path))              # Remove duplicates

    return set(paths) - set(successful)

def load_system_config():
    """
    Load configuration from ``system_config_paths``. If any of the files
    cannot be read, print an error and exit.
    """
    failed = load_config(system_config_paths)
    if failed:
        print_cli_err(
            "the following system configuration files could not be read:",
            *failed, sep='\n\t')
        exit(1)

def load_user_config():
    """
    Load configuration from ``user_config_paths``. If some of the files can't be
    read, print a warning.
    """
    failed = load_config(user_config_paths)
    if len(failed) == len(user_config_paths):
        print_cli_warn("no user configuration files could not be read:")
        print_cli_warn("The following files were tried:", *failed, sep='\n\t')

def load_config_from_args(args):
    """
    Load configuration files specified as command arguments in ``args``.
    If any of the files can't be read, print an error and exit."""
    failed = load_config(args.config)
    if failed:
        print_cli_err(
            "the following configuration files could not be read:",
            *failed, sep='\n\t')
        exit(1)


def add_general_options(parser, dummy=False):
    """
    Add options that are common among various commands. By default, when a
    subcommand is called, all options that are defined for the main command are
    valid but they must be specified before the subcommand name. By using this
    function with each subcommand, the option can be specified after the
    subcommand name.
    """
    # TODO remove this after a tryout period
    group = parser.add_argument_group('general options')
    group.add_argument('-h', '--help',
                       action=('store_true' if dummy else 'help'),
                       help='show this help message and exit')
    group.add_argument('-R', '--repo', action='append', default=[],
                        help='use the repository REPO')
    group.add_argument('-c', '--config', metavar='FILE',
                        action='append', default=[],
                        help='use configuration from FILE')

def add_edit_options(parser):
    """Add `--edit` and `--editor` options to ``parser``."""
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

def expand_alias(index, args):
    """
    Expand alias in ``args`` and return the modified argument list.
    :param index: the index of the argument that is to be expanded as an alias
        If the argument isn't aliased to anything, the list is returned
        unmodified.
    :param args: list of command arguments
    """
    alias = args[index]
    aliased = cfg['alias.%s' % alias]

    if not aliased:                                 # No alias found in config
        return args

    from . import ext
    expanded_alias = ext.shell_arglist(aliased)     # Expand alias into arg list
    if index == -1:
        args[-1:] = expanded_alias
    else:
        args[index:index+1] = expanded_alias

    return args
