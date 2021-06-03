.. _man_tem_hook:

========
tem-hook
========

SYNOPSIS
========

.. raw:: html

   <center><pre><code class="no-decor">

|  tem [**--help**] [**--exec**] [**--new**] [**--add**] [**--edit**] [**--editor** *<EDITOR>*]
|      [**--force**] [**--reconfigure**] [*<HOOKS>*]

.. raw:: html

   </code></pre></center>

DESCRIPTION
===========

Hooks are executable files that run automatically whenever a tem subcommand is
run. There are two main types of hooks:

- `pre` hooks run before a tem subcommand
- `post` hooks run after a tem subcommand

The `hook` subcommand is used to list, add, execute hooks at will, or otherwise
manipulate them.  This manual page shows usage information for the `hook`
subcommand and documents the format for hooks (see :ref:`HOOKS<hooks>` section).
To see which environment variables are available when hooks are run, see the
:ref:`ENVIRONMENT<hook_environment>` section.

OPTIONS
=======

.. program:: hook

.. option:: -h, --help

   Prints the synopsis, available subcommands and options.

.. option:: -x, --exec

   Manually execute specified `HOOKS`.

.. option:: -n, --new

   Create new hooks under the `.tem/hooks` directory.

.. option:: -a, --add

   Add existing files as hooks to the `.tem/hooks` directory.

.. option:: -l, --list

   List hooks. If `<HOOKS>` are specified, only matching hooks will be
   listed, otherwise all hooks will be listed.

.. option:: -e, --edit

   Open files for editing.

.. option:: -E <EDITOR>, --editor <EDITOR>

   Same as :option:`hook --edit` but uses `<EDITOR>` instead of the default editor.

.. _hooks:

HOOKS
=====

Hooks are normally located in a `.tem/hooks` subdirectory. Each hook is of the
format `NAME.SUBCOMMAND.WHEN`, where:

- `NAME` can be any any identifier
- `SUBCOMMAND` is the subcommand that triggers this hook
- `WHEN` can be either `pre` (run before `SUBCOMMAND`) or `post` (run after
  `SUBCOMMAND`)

When hooks are run, they are invoked with the same command arguments as the
instance of tem that triggered them.

**NOTE**: Make sure the hook file is executable and not hidden.

Global hooks
------------

Hooks placed in `$PREFIX/share/tem/hooks` or `$XDG_CONFIG_HOME/tem/hooks` will
run no matter where tem is getting called from, provided their format matches
the subcommand.

.. _hook_environment:

ENVIRONMENT
===========

Some environment variables are common to all hooks, but each subcommand has
additional variables. Additionally, hooks behave differently when triggered by
different subcommands. See the appropriate subsection of this section for more
information.

The following environment variables get set by each subcommand:

Common environment
------------------

| :envvar:`TEM_ROOTDIR` - directory containing the `.tem/hooks` subdirectory
where the hook resides.

tem put
-------

**NOTE**: Hooks are run for each template argument separately.

| :envvar:`TEM_TEMPLATE` - path of the template file
| :envvar:`TEM_DEST` - path of the destination file or directory

SEE ALSO
========

:ref:`tem<man_tem>`
