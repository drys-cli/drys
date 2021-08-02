.. _man_tem_put:

=======
tem-put
=======

SYNOPSIS
========

.. raw:: html

   <center><pre><code class="no-decor">

|  tem put [**--help**] [**--output** *<OUT>* | **--directory** *<DIR>*] [**--edit**]
|          [**--editor** *<EDITOR>*] [**--repo** *<REPO>*] [**--config** *<FILE>*]
|          [*<TEMPLATES>*]

.. raw:: html

   </code></pre></center>

DESCRIPTION
===========

If repositories are specified using :option:`--repo<tem --repo>`, then only those
repositories will be looked up, otherwise repositories from `repo_path` will be
looked up.

.. todo:: Unified way of referencing `repo_path`

OPTIONS
=======

.. program:: put

.. option:: -h, --help

   Prints the synopsis, available subcommands and options.

.. option:: -o, --output=<OUT>

   The file will be added as `<OUT>`. Any missing directories will be created.

.. option:: -d, --directory=<DIR>

   The file will be added under the directory `<DIR>`. Missing directories will
   be created.

.. option:: -e, --edit

   Open the newly added files for editing.

.. option:: -E <EDITOR>, --editor=<EDITOR>

   Same as :option:`--edit<put --edit>` but uses `<EDITOR>` instead of the default editor.

**NOTE**: See also :ref:`tem(1)<man_tem>` for a list of options common to all subcommands.

SEE ALSO
========

:ref:`tem(1)<man_tem>`, :ref:`tem-add(1)<man_tem_add>`
