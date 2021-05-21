import sys, os, shutil, re

import configparser

class ConfigParser(configparser.ConfigParser):
    def __init__(self, files=None, **kwargs):
        super().__init__(**kwargs)
        # Allow reading files on construction
        if files:
            self.read(files)

    def set(self, section, option, value, *args, **kwargs):
        if not self.has_section(section):
            self.add_section(section)
        super().set(section, option, value, *args, **kwargs)

    def __getitem__(self, option):
        split = option.split('.', 1)
        if len(split) == 1:
            split.insert(0, 'general')
        return self.get(*split, fallback='')

    def __setitem__(self, option, value):
        split = option.split('.', 1)
        if len(split) == 1:
            split.insert(0, 'general')
        section, option = tuple(split)
        self.set(section, option, value)

def print_err(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def print_error_from_exception(e):
    print_err('tem: error:', re.sub(r'^\[Errno [0-9]*\] ', '', str(e)))

def abspath(path):
    return os.path.abspath(os.path.expanduser(path))

def basename(path):
    return os.path.basename(os.path.abspath(path))

def dirname(path):
    return os.path.dirname(os.path.abspath(path))

def copy(src, dest='.', ignore_nonexistent=False):
    _dirname = dirname(dest)
    if _dirname and not os.path.exists(_dirname):
        os.makedirs(_dirname, exist_ok=True)
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

def fetch_name(repo_path):
    cfg = ConfigParser(repo_path + '/.tem/repo')
    name = cfg['general.name']
    if name:
        return name
    else:
        return basename(repo_path)

def repo_ids_equal(id1, id2):
    return id1 == id2 or \
        abspath(id1) == abspath(id2) or \
        fetch_name(id1) == fetch_name(id2)

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
        from . import common
        lookup_repos = common.repo_path

    for repo in lookup_repos:
        if os.path.exists(repo) and fetch_name(repo) == repo_id:
            return abspath(repo)

    # If all else fails, try to find a repo whose basename is equal to `path`
    for repo in lookup_repos:
        if basename(repo) == repo_id:
            return repo

    # The `path` must be relative/absolute then
    return os.path.expanduser(repo_id)

