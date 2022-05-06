.. _dev_shell:

Shell
=====

Tem supports a variety of shell plugins. In an ideal world, the goal would be
for all shells to support the same set of features. But, different shells have
their quirks and so we can only strive to maximize compatibility.

Regardless of the concrete shell, the shell's startup script should define a
`tem` function. When the user calls `tem` on the command line, this function
will be invoked instead of the `tem` executable. This function can be obtained
by sourcing a file provided by the tem package, which is platform-dependent.

Before calling the `tem` executable (also called :term:`vanilla tem<Vanilla
tem>`), the function must export the
:func:`__TEM_SHELL_SOURCE<tem.env.vars.shell_source>` environment variable,
setting its content to the path of a file that vanilla tem can write to. The
purpose of this file is the following:

- When vanilla tem wants the shell to do something, it writes a command or list
  of commands to this file
- After vanilla tem exits, the parent shell sources this file

This is merely a simple and cheap way to provide vanilla tem with the ability to
manipulate the state of the calling shell. A more obvious way would be to let 
