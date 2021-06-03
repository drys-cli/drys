.. _man_tem:

===
tem
===

SYNOPSIS
========

.. raw:: html

   <center><pre><code class="no-decor">

|  tem [**--version**] [**--help**]
|  tem [*<OPTIONS>*] *<COMMAND>*

.. raw:: html

   </code></pre></center>

DESCRIPTION
===========

tem is a lightweight yet feature-packed template/snippet/environment manager for
the terminal. If you are using tem for the first time, we recommend you go
through :ref:`tem-tutorial(1)<tem_tutorial>` first.

You can use **tem** to:

   1. Organize template files and utilize them efficiently
   2. Create scripts to populate (specialize) those template files with dynamic data
   3. Manage environments (scripts, environment variables, hooks) local to specific
      directories
   4. Share useful workflow files with collaborators, while keeping them out of the
      main VCS branch

It is useful to know the basic terminology of **tem**:

   1. A *template file* is a file that can be reused in multiple similar projects
   2. A *tem repository* is a directory where template files/directories are stored

OPTIONS
=======

.. program:: tem

.. option:: -v, --version

   Prints the currently installed version of tem.

.. option:: -h, --help

   Prints the synopsis, available subcommands and options.

.. option:: --init-config

   Generate initial user configuration file at the path with the highest priority,
   usually `~/.config/tem/config`. (see :ref:`tem-config(1)<man_tem_config>`)

.. option:: --debug

   Runs the command inside a python debugger (requires the python package
   `pudb <https://pypi.org/project/pudb>`_
   to be installed). This is meant for developers.

The following options are common to all subcommands:

.. option:: -h, --help

   Prints the synopsis and list of options.

.. option:: -c <FILE>, --config=<FILE>

   Load the specified configuration file on top of the default configuration
   (see :ref:`tem-config(1)<man_tem_config>`).

.. option:: --reconfigure

   Discard any configuration loaded before parsing this option.

.. option:: -R <REPO>, --repo=<REPO>

   By default, the repositories that are used by subcommands are taken from the
   configuration key `general.repo_path`. Use this option to ditch those default
   repositories and use `<REPO>`, which is a repository pseudo-path (see
   :ref:`Locating repositories<locating_repositories>`). If specified multiple
   times, then all specified repositories are used.

SUBCOMMANDS
===========

add
---

Add a file or directory to a repository as a template. See :ref:`tem-add(1)<man_tem_add>`.

rm
--

Remove a template from a repository.

put
---

Copy a template from a repository to a specified destination.

ls
--

List the contents of repositories.

repo
----

List, add or remove repositories.

config
------

Get or set configuration options.

init
----

Initialize a directory with a `.tem` subdirectory.

env
---

Run or modify local environments.

.. _config:

REPOSITORY
==========

A repository is a dedicated directory that contains templates. Each subcommand
takes a :option:`tem --repo` option that allows you to specify which repositories
you want the command to operate on. If no repositories are specified with this
option, then a default list of repositories is taken from the
`general.repo_path` configuration option.

.. _locating_repositories:

Locating repositories
---------------------

Repositories can be located in multiple ways, which we call pseudo-paths. The
lookup order is as follows, from higher to lower priority:

#. Special value `/`

   Abbreviation for: "all default repositories".

   This is useful with the :option:`tem --repo` option. Namely, if this option
   is specified to any subcommand, the default repositories are not taken into
   consideration.  By specifying :option:`--repo /<tem --repo>`, the default
   repositories will be taken into consideration after all.

#. Special value `-`

   All repositories that can be read from stdin. The input must be formatted
   such that each line is a repository pseudo-path (the value `-` loses its
   special meaning in this case). The input is terminated by an empty line or
   EOF.

#. Repository name

   By default, the repository name is the basename of the repository absolute
   path. It can be overriden by the configuration option `general.name` in
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

SEE ALSO
========

:ref:`tem-add(1)<man_tem_add>`, **tem-fish(1)**, **tem.vim**
