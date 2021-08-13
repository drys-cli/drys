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

   1. A *template* is a file or directory that is meant to be reused
   2. A *tem repository* is a directory where templates are stored
   3. A *local environment* is an environment that is active only when you enter
      a directory

OPTIONS
=======

.. program:: tem

.. option:: -v, --version

   Prints the currently installed version of tem.

.. option:: -h, --help

   Prints the synopsis, available subcommands and options.

.. option:: --init-user

   Generate initial user configuration file at the path with the highest priority,
   usually `~/.config/tem/config`. (see :ref:`tem-config(1)<man_tem_config>`)
   Also create an empty default repository at `~/.local/share/tem/repo`.

.. option:: --debug

   Runs the command inside a python debugger (requires the python package
   `pudb <https://pypi.org/project/pudb>`_
   to be installed). This is meant for developers.

**The following options are common to all subcommands:**

.. option:: -h, --help

   Prints the synopsis and list of options.

.. option:: -c <FILE>, --config=<FILE>

   Load the specified configuration file on top of the default configuration
   (see :ref:`tem-config(1)<man_tem_config>`).

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

|man_desc_tem_add|. See :ref:`tem-add(1)<man_tem_add>`.

rm
--

|man_desc_tem_rm|. See :ref:`tem-rm(1)<man_tem_rm>`.

put
---

|man_desc_tem_put|. See :ref:`tem-put(1)<man_tem_put>`.

ls
--

|man_desc_tem_ls|. See :ref:`tem-ls(1)<man_tem_ls>`.

repo
----

|man_desc_tem_repo|. See :ref:`tem-repo(1)<man_tem_repo>`.

config
------

|man_desc_tem_config|. See :ref:`tem-config(1)<man_tem_config>`.

init
----

|man_desc_tem_init|. See :ref:`tem-init(1)<man_tem_init>`.

env
---

|man_desc_tem_env|. See :ref:`tem-env(1)<man_tem_env>`.

git
---

|man_desc_tem_git|. See :ref:`tem-git(1)<man_tem_git>`.

hook
----

|man_desc_tem_hook|. See :ref:`tem-hook(1)<man_tem_hook>`.

FILES
=====

Each directory can have a `.tem` subdirectory that contains files that are of
interest to **tem**. The standard contents of that directory are:

.. table::

   +----------+--------------------------------------------------------------+
   | File     | Description                                                  |
   +----------+--------------------------------------------------------------+
   | `path/`  | Prepended to :envvar:`PATH` when local environment is active |
   +----------+--------------------------------------------------------------+
   | `env/`   | Executables that get run by :command:`tem env`               |
   +----------+--------------------------------------------------------------+
   | `hooks/` | Executables that get triggered by tem subcommands            |
   +----------+--------------------------------------------------------------+
   | `config` | Local **tem** configuration                                  |
   +----------+--------------------------------------------------------------+
   | `repo`   | Repository configuration                                     |
   +----------+--------------------------------------------------------------+
   | `ignore` | Files that **tem** shall ignore                              |
   +----------+--------------------------------------------------------------+

.. todo:: How to make this table display wider in manpage output

Extensions to **tem** may use additional subdirectories. Please consult the
appropriate manuals.

REPOSITORY
==========

A repository is a dedicated directory that contains templates. Each subcommand
takes a :option:`--repo<tem --repo>` option that allows you to specify which repositories
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

   This is useful with the :option:`--repo<tem --repo>` option. Namely, if this option
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

COMMON BEHAVIOR
===============

The commands are designed in order to be maximally consistent. This section
documents some of the common behaviors. Knowing those can significantly flatten
the learning curve for tem.

1. tem provides shortcuts at every corner

   Every tem command that takes file or directory arguments accepts relative or
   absolute paths. However, if the specified file does not contain any
   :guilabel:`/` characters, it will be looked up in some of the directories
   recognized by tem. TODO
2. Most commands support :option:`--edit<tem --edit>` and
   :option:`--editor<tem --editor>` options.

Each command can take a `--repo` option. This specifies a repository to look up
in order to perform the command. If a `--template` option is given, then the
TODO

SEE ALSO
========

:ref:`tem-add(1)<man_tem_add>`, **tem-fish(1)**, **tem.vim**
