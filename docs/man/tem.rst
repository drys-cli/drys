.. _man_tem:

===
tem
===

SYNOPSIS
========

.. code-block:: none

   tem [--version] [--help]
   tem [<options>] <command>

DESCRIPTION
===========

tem is a lightweight yet feature-packed template/snippet/environment manager for
the terminal. If you are using tem for the first time, we recommend you go
through :ref:`tem-tutorial(1)<tem_tutorial>` first.

OPTIONS
=======

`-v`\ , `--version`
   Prints the currently installed version of tem.

`-h`\ , `--help`
   Prints the synopsis, available subcommands and options.

`--init-config`
   Generate initial user configuration file at the path with the highest priority,
   usually `~/.config/tem/config`. (see :ref:`tem-config(1)<man_tem_config>`)

`--debug`
   Runs the command inside a python debugger (requires the python package
   `pudb <https://pypi.org/project/pudb>`_
   to be installed). This is meant for developers.

The following options are common to all subcommands:

`-h`\ , `--help`
   Prints the synopsis and list of options.

`-c \<FILE\>`\ , `--config \<FILE\>`
   Load the specified configuration file on top of the default configuration
   (see :ref:`tem-config(1)<man_tem_config>`).

`--reconfigure`
   Discard any configuration loaded before encountering this option.

   Example:

   #. ``tem <subcommand> --reconfigure``

      tem will use the default configuration.

   #. ``tem <subcommand> --config FILE1 --reconfigure --config FILE2``

      tem will be configured from FILE2, but FILE1 is ignored.

`-R \<REPO\>`\ , `--repo \<REPO\>`
   By default, the repositories that are used by subcommands are taken from the
   configuration key '`general.repo_path`'. Use this option to ditch those
   default repositories and use REPO, which is a repository pseudo-path (see
   :ref:`Locating repositories<locating_repositories>`). If specified multiple
   times, then all specified repositories are used.

SUBCOMMANDS
===========

add
---

Add a file or directory to a repository.

rm
--

put
---

ls
--

repo
----

config
------

.. _config:

REPOSITORY
==========

A repository is a directory that contains templates. Each subcommand takes a
`--repo` option that allows you to specify which repositories you want the
command to operate on. If no repositories are specified using this option, then
a default list of repositories is taken from the '`general.REPO_PATH`'
configuration option.

.. _locating_repositories:

Locating repositories
---------------------

Repositories can be located in multiple ways, which we call pseudo-paths. The
lookup order is as follows, from higher to lower priority:

#. Special value `/`

   Abbreviation for: "all default repositories".
   
   This is useful with the `--repo` option. Namely, if this option is specified
   to any subcommand, the default repositories are not taken into consideration.
   By specifying `--repo /`, the default repositories will be taken into
   consideration after all.

#. Special value `-`

   All repositories that can be read from stdin. The input must be formatted
   such that each line is a repository pseudo-path (the value `-` loses its
   special meaning in this case). The input is terminated by an empty line or
   EOF.

#. Repository name

   By default, the repository name is the basename of the repository absolute
   path. It can be overriden by the configuration option '`general.name`' in
   `path/to/repoX/.tem/repo`. The name can contain anything but the
   :guilabel:`/` character, but we recommend that you only use alphanumeric
   characters, :guilabel:`-` and :guilabel:`_` in the name (regex:
   ``[a-zA-Z-_]``).

   For this to work, the repository with the specified name must be in
   the list of default repositories.

   **Note:** The basename of a path `a/b/c` is its last component: `c`.

#. Absolute or relative path to repository

   Tip: If PWD contains a repository (e.g. directory `repoX`) and a repository
   with the name `repoX` exists in `REPO_PATH`, make it explicit that you want
   the local repository by using `./repoX`.
