Environment
===========

When you are in a temdir, you can run `tem env` to load the local environment
for that temdir. To simplify things, what happens is that all the files in
`.tem/env/` are executed.

Suppose that we have the following structure:

TODO...

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
