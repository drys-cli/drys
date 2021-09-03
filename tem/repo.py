"""Repository operations"""
import os

from . import config, util

#: List of lookup paths for tem repositories
repo_path = [
    line for line in os.environ.get("REPO_PATH", "").split("\n") if line
]


class RepoSpec:
    """An abstraction for various ways of specifying tem repositories

    Args:
        paths (str, list, optional): repository paths or other types of specs
        spec_type: type of spec. Values: `INCLUDE`, `EXCLUDE`,
            `FROM_LOOKUP_PATHS`

    The following types of specs are supported:

      - absolute or relative path to a repository
      - name of a repository
      - absolute or relative path to a repository that is to be excluded
      (when `spec_type` is `exclude`)
      - all repositories from `repo_path`

    You can obtain the list of usable repository paths by calling
    :func:`abspaths`.

    By default, ``pseudopaths`` will be included in the final list of
    repositories. If ``spec_type`` is :attr:`EXCLUDE` then ``pseudopaths`` are
    excluded from the final list. If ``spec_type`` is :attr:`FROM_LOOKUP_PATH`
    then all the paths from :data:`repo_path` are included in the spec. An
    empty spec is euivalent to a `FROM_LOOKUP_PATH` spec.
    """

    INCLUDE = 1
    EXCLUDE = 2
    FROM_LOOKUP_PATH = 4

    @staticmethod
    def of_type(spec_type):
        """
        Look at :func:`__init__` for the proper ways of specifying a spec type.
        """

        def func(specs=None):
            return RepoSpec(specs=specs, spec_type=spec_type)

        return func

    # Holds the paths/subspecs
    _data: list

    def __init__(self, specs=None, spec_type=None):
        """Initialize repo spec

        In the most basic form, ``specs`` is a string or list of strings
        representing repository paths or names. Specs can also contain other
        specs. ``spec_type`` is the type of spec and can be a single type or a
        tuple containing multiple types. If no `spec_type` is specified, the
        spec will be of the ``INCLUDE`` type.
        """
        if not spec_type and isinstance(specs, int):
            # Constructed with only spec_type as its argument
            spec_type = specs
            specs = None
        elif not spec_type:
            # Unspecified spec_type should fall back to INCLUDE
            spec_type = RepoSpec.INCLUDE

        # Error checking
        if not spec_type & (
            self.INCLUDE | self.EXCLUDE | self.FROM_LOOKUP_PATH
        ):
            raise ValueError("invalid spec type")
        if spec_type & RepoSpec.INCLUDE and spec_type & RepoSpec.EXCLUDE:
            raise ValueError(
                "spec_type cannot contain both INCLUDE and EXCLUDE"
            )
        if spec_type & RepoSpec.FROM_LOOKUP_PATH and specs is not None:
            raise ValueError("cannot specify specs with FROM_LOOKUP_PATH")

        self._data = []
        self.spec_type = spec_type
        if specs is not None:
            self.append(specs)

    def append(self, specs):
        """Append specs to the list."""
        err = ValueError("specs must be a string, spec, or list of specs")
        if isinstance(specs, str):
            self._data += [s for s in specs.split("\n") if s]
        elif isinstance(specs, RepoSpec):
            self._data.append(specs)
        elif isinstance(specs, list):
            # All items in specs must be strings or RepoSpecs
            if all(isinstance(spec, (str, RepoSpec)) for spec in specs):
                self._data += specs
            else:
                raise err
        else:
            raise err

    def _abspaths(self, included):
        """Get a list of paths that are included/excluded by this spec."""
        if (included and (self.spec_type & RepoSpec.EXCLUDE)) or (
            not included and not (self.spec_type & RepoSpec.EXCLUDE)
        ):
            # Only exclude-type specs can exclude paths, and only other-type
            # specs can include
            return []

        if not self._data:
            if included:
                return repo_path
            return []

        if self.spec_type & RepoSpec.FROM_LOOKUP_PATH:
            return repo_path

        result = repo_path.copy()
        # If at least one subspec is not EXCLUDE, initialize empty result
        for item in self._data:
            if isinstance(item, str) or (
                not item.spec_type & RepoSpec.EXCLUDE
            ):
                result = []
                break

        for item in self._data:
            if isinstance(item, str):
                result.append(resolve(item))
            elif isinstance(item, RepoSpec):
                if item.spec_type & RepoSpec.EXCLUDE:
                    result[:] = [
                        spec
                        for spec in result
                        if spec
                        not in item._abspaths(  # pylint: disable=protected-access disable=line-too-long
                            False
                        )
                    ]
                else:
                    result += item.abspaths()
            else:
                raise ValueError(
                    "Spec list contains invalid types. Please "
                    "report this as a bug."
                )

        return list(dict.fromkeys(result))  # Remove duplicates

    def abspaths(self):
        """Return absolute paths of repositores specified by this spec."""
        return self._abspaths(True)


def is_valid_name(name):
    """Test if ``name`` is a valid repository name."""
    return "/" not in name


def get_name(path):
    """
    Get the name of the repo at ``path`` from its configuration. If the
    repo has not configured a name, the base name of its directory is used.
    This works even if the repository does not exist on the filesystem.
    """
    # TODO put this entry in the local config file
    cfg = config.Parser(path + "/.tem/repo")
    name = cfg["general.name"]
    if name:
        return name
    return util.basename(path)


def named(name):
    """
    Return absolute path to the repository with the given name if it exists;
    otherwise return `name` unmodified.
    """
    # TODO decide how to handle ambiguity
    for repository in repo_path:
        if get_name(repository) == name:
            return repository

    return name  # Nothing found in REPO_PATH


def resolve(path_or_name):
    """Return the absolute path of the repo identified by ``path_or_name``.

    The following strategy is used:
    - If the argument is a valid repository name, find a repo in
      :data:`repo_path` with the given name
    - If the argument is a path or the previous step failed to find a repo,
      return the absolute path version of the input path
    """
    if not path_or_name:
        return ""

    if is_valid_name(path_or_name):
        return named(path_or_name)

    return util.abspath(path_or_name)


def find_template(template, repos, all_repos=False):
    """
    Return the absolute path of a template, looked up in ``repos``. If
    ``all_repos`` is ``True`` then a list of matching templates in each
    repository is returned. Otherwise, only the match in the first repository
    is returned (a list with one element). If there are no matches an empty
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
