import sys, os, shutil, re

def print_error_from_exception(e):
    print('tem: error:', re.sub(r'^\[Errno [0-9]*\] ', '', str(e)), file=sys.stderr)

def realpath(path):
    return os.path.realpath(os.path.expanduser(path))

def basename(path):
    return os.path.basename(realpath(path))

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

def fetch_name(repo_path):
    import configparser
    cfg = configparser.ConfigParser(default_section='general')
    cfg.read(repo_path + '/.tem/repo')
    name = cfg.get('general', 'name', fallback=None)
    if name:
        return name
    else:
        return basename(repo_path)

def repo_ids_equal(id1, id2):
    return id1 == id2 or \
        realpath(id1) == realpath(id2) or \
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
        from .common import default_repos
        lookup_repos = default_repos

    for repo in lookup_repos:
        if os.path.exists(repo) and fetch_name(repo) == repo_id:
            return realpath(repo)

    # If all else fails, try to find a repo whose basename is equal to `path`
    for repo in lookup_repos:
        if basename(repo) == repo_id:
            return repo

    # The `path` must be relative/absolute then
    return os.path.expanduser(repo_id)

