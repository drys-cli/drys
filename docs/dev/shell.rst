.. _dev_shell:

Shell
=====

Tem supports a variety of shell plugins, each with its own syntax. The program
that wraps the main tem executable must export the
:func:`__TEM_SHELL_SOURCE<tem.env.vars.shell_source>` environment variable to
:term:`vanilla tem<Vanilla tem>`. This variable must contain the path to a file.
Vanilla tem will write commands to this file and the shell is supposed to source
it.
