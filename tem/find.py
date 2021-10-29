"""Find various tem-related stuff."""
import os


def find_parents_with_subdir(path, subdir):
    """
    Return parent absolute paths that contain a subdirectory tree `subdir`.
    """

    path = os.path.realpath(path)
    result_paths = []

    while True:
        if os.path.isdir(path + "/" + subdir):
            result_paths.append(path)
        path = os.path.dirname(path)
        if path == "/":
            break

    return result_paths
