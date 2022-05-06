Environment
===========

Tem introduces the concept of local environments -- environments that are active
only when you are located in a particular directory.

When you are in a temdir or any of its subdirectories, run `tem env` to load the
local environment for that temdir. This will execute all files located in
`.tem/env/` recursively.

If you are using a :ref:`shell plugin<shell>`, some subdirectories of
`.tem/env/` will be treated in a special way. All files located under
`.tem/env/@\<shell_name\>` will be sourced by the shell instead of being
executed.

.. hint::

   Replace `\<shell_name\>` with the name of the shell you are using. For
   example if you are using `bash`, put those files inside `.tem/env/@bash/`.

We highly recommend using a shell plugin, as it provides great convenience by
automating some tasks for you. And it allows you to save the state of the
environment to the shell, so that subsequent runs of `tem env` will not run the
same scripts again. There are many

Suppose that we have the following structure:

Detailed description
--------------------

Without shell extension
***********************

Each time you run `tem env`, all files under `.tem/env/` without a suffix will
be executed by the system. For the files to be executed properly, they have to
be program binaries or they must begin with an appropriate shebang. If you run
`tem env` multiple times, the files will be executed multiple times. Since this
is undesired in most cases, we recommend that you use a shell extension (TODO
add link).

With shell extension
********************

When you run `tem env`, all files in `.tem/env/` will be run, using the
following rules:

- Files without suffixes will be executed by the system. For this to work, they
  should begin with an appropriate shebang.
- Files with a `py` suffix will be sourced by python
- Files with a shell suffix (exact suffix matches the shell name) will be
  sourced by the corresponding shell. Currently `fish`, `bash` and `zsh` are
  supported. The appropriate shell extension must be installed -- see
  :ref:`Shell extensions` (TODO add link).

Tem keeps track of the directories that take part in the loaded environment, so
you don't load the same environment multiple times.
