.. _man_tem_put:

=======
tem-put
=======

SYNOPSIS
========

.. raw:: html

   <center><pre><code class="no-decor">

| tem put [**--help**]  [**--output** *<OUT>*] [**--directory** *<DIR>*]
|         [**--edit**] [**--editor** *EDITOR*] [**--reconfigure**]

.. raw:: html

   </code></pre></center>

DESCRIPTION
===========

Take a template file or directory and place it somewhere.

OPTIONS
=======

.. option:: -h, --help

   Prints the synopsis and list of options.

.. option:: -o, --output=<OUT>

   The files will be added as `<OUT>`. Any missing directories will be created.

.. option:: -d, --directory=<OUT>

   The fille will be added under the directory `<DIR>`. Any missing directories
   will be created.

   .. todo:: Multiple files?

.. option:: -e, --edit

   Open the newly added files for editing.

.. option:: -E <EDITOR>, --editor <EDITOR>

   Same as :option:`--edit` but uses `<EDITOR>` instead of the default editor.

**NOTE**: See also :ref:`tem(1)<man_tem>` for a list of options common to all
subcommands.

SEE ALSO
========

:ref:`tem(1)<man_tem>`, :ref:`tem-add(1)<man_tem_add>`
