.. _man_tem_add:

=======
tem-add
=======

SYNOPSIS
========

.. raw:: html

   <center><pre><code class="no-decor">

| tem add [**--help**] [**--move**] [**--output** *<OUT>*] [**--directory** *<DIR>*]
|         [**--edit**] [**--editor** *EDITOR*] [**--recursive** | **--norecursive**]
|         [**--reconfigure**]

.. raw:: html

   </code></pre></center>

DESCRIPTION
===========

Add a file or directory as a template to a repository.

OPTIONS
=======

.. option:: -h, --help

   Prints the synopsis and list of options.

.. option:: -o, --output=<OUT>

   The file will be added as `<OUT>`, relative to the repository path. Any
   missing directories will be created.

.. option:: -d, --directory=<DIR>

   The file will be added under the directory `<DIR>` relative to the repository
   path. Missing directories will be created.

.. option:: -m, --move

   The original file will be removed.

.. option:: -e, --edit

   Open the newly added files for editing.

.. option:: -E <EDITOR>, --editor <EDITOR>

   Same as :option:`--edit` but uses `<EDITOR>` instead of the default editor.

.. option:: -r, --recursive

   Copy directories recursively. This is enabled by default.

.. option:: --norecursive

   Do not copy directories recursively.

**NOTE**: See also :ref:`tem(1)<man_tem>` for a list of options common to all subcommands.

SEE ALSO
========

:ref:`tem(1)<man_tem>`, :ref:`tem-put(1)<man_tem_put>`
