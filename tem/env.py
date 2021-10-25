"""Work with tem environments."""

import os


def find_temdirs_with_env(path):
    """
    Find all temdirs with a .tem/env directory, in the file hierachy of `path`
    """
    result = []
    while True:
        if os.path.isdir(path + '/.tem/env'):
            result.append(path)
        if path == '/':
            break
        path = os.path.dirname(path)
    return result
