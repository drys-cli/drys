"""Repository operations"""
import os

from . import util

# List of lookup paths for tem repositories
repo_path = [
    line for line in os.environ.get("REPO_PATH", "").split("\n") if line
]


def find_template(template, repos, all_repos=False):
    """
    Return the absolute path of a template, looked up in ``repos``. If
    ``all_repos`` is ``True`` then a list of matching templates in each
    repository is returned. Otherwise, only the match in the first repository
    is returned (a list with one element). If there are not matches an empty
    list is returned.
    .. note:: A template can be a directory tree.
    """
    result_paths = []

    for repository in repos:
        template_abspath = util.abspath(repository + "/" + template)
        if not os.path.exists(template_abspath):
            continue
        if not all_repos:
            return [template_abspath]
        result_paths.append(template_abspath)

    return result_paths
