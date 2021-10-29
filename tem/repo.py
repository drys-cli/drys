"""Repository operations"""
import os

from tem import config, util


class Repo:
    """A python representation of a repository."""

    def __init__(self, *args):
        if not args:
            self.path = ""
        if isinstance(args[0], str):
            self.path = args[0]
        elif isinstance(args[0], Repo):
            self.path = args[0].path

    def abspath(self):
        """Get the absolute path of the repo, preserving symlinks."""
        return util.abspath(self.path)

    def realpath(self):
        """Get the real path of the repo."""
        return os.path.realpath(self.path)

    def name(self):
        """Get the name of the repo at ``path`` from its configuration.

        If the repo has not configured a name, the base name of its directory
        is used. This works even if the repository does not exist on the
        filesystem.
        """

        # TODO put this entry in the local config file
        cfg = config.Parser(self.path + "/.tem/repo")
        name = cfg["general.name"]
        if name:
            return name
        return util.basename(self.path)

    def has_template(self, template):
        """Test if the repo contains `template`."""
        return os.path.exists(util.abspath(self.path + "/" + template))


#: List of lookup paths for tem repositories
lookup_path = [
    Repo(line) for line in os.environ.get("REPO_PATH", "").split("\n") if line
]


class RepoSpec:
    """An abstraction for various ways of specifying tem repositories

    The following types of specs are supported:

      - absolute or relative path to a repository
      - name of a repository
      - absolute or relative path to a repository that is to be excluded
        (when `spec_type` is :attr:`EXCLUDE`)
      - all repositories from :data:`path`

    You can obtain the list of repositories from a spec by calling
    :func:`repos`.

    If ``spec_type`` is :attr:`EXCLUDE` then ``pseudopaths`` are
    excluded from the final list. If ``spec_type`` is :attr:`FROM_LOOKUP_PATH`
    then all the paths from :data:`repo.lookup_path` are included in the spec.
    An empty spec is euivalent to a `FROM_LOOKUP_PATH` spec.

    Attributes
    ----------
    paths : str, list, optional
        Repository paths or other types of specs
    spec_type
        Values: `INCLUDE`, `EXCLUDE`, `FROM_LOOKUP_PATH` or a bitwise OR of
        these

    Constants
    ---------
    INCLUDE
        Specified repos or specs will be included in the final list of repos.
    EXCLUDE
        Specified specs will be excluded from the final list of repos.
    FROM_LOOKUP_PATH
        Repos from :data:`path` will be:

          - included if `INCLUDE` is set
          - excluded if `EXCLUDE` is set

    Methods
    -------
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
                return lookup_path
            return []

        if self.spec_type & RepoSpec.FROM_LOOKUP_PATH:
            return lookup_path

        result = lookup_path.copy()
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
                    result += item.repos()
            else:
                raise ValueError(
                    "Spec list contains invalid types. Please "
                    "report this as a bug."
                )

        return list(dict.fromkeys(result))  # Remove duplicates

    def repos(self):
        """Return absolute paths of repositores specified by this spec."""
        # return self._abspaths(True)
        return [Repo(path) for path in self._abspaths(True)]


def is_valid_name(name):
    """Test if ``name`` is a valid repository name."""
    return "/" not in name


def named(name):
    """
    Return absolute path to the repository with the given name if it exists;
    otherwise return `name` unmodified.
    """
    # TODO decide how to handle ambiguity
    for repo in lookup_path:
        repo = Repo(repo)
        if repo.name() == name:
            return repo

    return Repo(None)


def resolve(path_or_name):
    """Get the repo identified by ``path_or_name``.

    The following strategy is used:

      - If the argument is a valid repository name, find a repo in
        `repo.lookup_path` with the given name.
      - If the argument is a path or the previous step failed to find a repo,
        return the absolute path version of the input path.
    """
    if not path_or_name:
        return Repo()

    if is_valid_name(path_or_name):
        return named(path_or_name)

    return Repo(path_or_name)


def find_template(template: str, repos=None, at_most=-1):
    """Return the absolute path of a template, looked up in ``repos``.

    Parameters
    ----------
    template : str
        Path to template relative to the containing repo.
    repos : list[int]
        Repositories to look up. A None value will use :data:`path`.
    at_most : int
        Return no more than this number of repositories.

    Returns
    -------
    template_paths : list[str]
        List of absolute paths to templates under the given repos.

    Notes
    -----
      A template can be a directory tree, e.g. "a/b/c".
    """

    if repos is None:
        repos = lookup_path

    if at_most == 0:
        return []

    result_paths = []

    i = 0
    for repo in repos:
        if i >= at_most and at_most != -1:
            break
        template_abspath = repo.abspath() + "/" + template
        if os.path.exists(template_abspath):
            result_paths.append(template_abspath)

    return result_paths
