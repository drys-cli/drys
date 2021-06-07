.. _man_tem_ls:

======
tem-ls
======

SYNOPSIS
========

.. raw:: html

   <center><pre><code class="no-decor">

|  tem ls [**--help**] [**--short**] [**--path**] [**--exec** *<CMD>*] [**--number** *<N>*]
|         [**--edit**] [**--editor** *<EDITOR>*] [**--recursive** | **--norecursive**]
|         [**--repo** *<REPO>*] [**--config** *<FILE>*] [**--reconfigure**]
          [*<TEMPLATES>*] [**--**] [*<LS_ARGUMENTS>*]

.. raw:: html

   </code></pre></center>

DESCRIPTION
===========

List *<TEMPLATES>* from the default tem repositories (or those specified using
:option:`--repo<tem --repo>`), using the :command:`ls` command.

The user can specify another command instead of :command:`ls` using the
:option:`--exec<ls --exec>` option or by changing the `ls.command` configuration
option (see :ref:`tem-config(1)<man_tem_config>`).

Any additional positional arguments will be passed as arguments to :command:`ls` or
equivalent command. If those extra arguments are options, they must be specified
after the special **--** argument so that :command:`tem ls` does not interpret them as
options to itself.

OPTIONS
=======

.. program:: ls

.. option:: -h, --help

   Prints the synopsis, available subcommands and options.

.. option:: -s, --short

   Simply list all available templates, without any repository information.

.. option:: -p, --path

   Print each template with its full path. Symlinks are not resolved.

   .. todo:: implement

.. option:: -x, --command=<CMD>

   Command to use to list templates instead of the default :command:`ls`. This will
   override the `ls.command` configuration option.

.. option:: -n, --number=<N>

   List at most `<N>` templates.

   .. todo:: implement

.. option:: -e, --edit

   Open the listed files for editing.

.. option:: -E <EDITOR>, --editor=<EDITOR>

   Same as :option:`--edit<ls --edit>` but uses `<EDITOR>` instead of the default editor.

.. option:: -r, --recursive

   Recurse into subdirectories.

.. option:: --norecursive

   Do not recurse into subdirectories. This is the **default** behaviour.

**NOTE**: See also :ref:`tem(1)<man_tem>` for a list of options common to all subcommands.

SEE ALSO
========

:ref:`tem(1)<man_tem>`, :ref:`tem-config(1)<man_tem_config>`,
:ref:`tem-repo(1)<man_tem_repo>`
