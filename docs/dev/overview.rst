Overview
========

.. todo:: This section is outdated

Tem uses python's ``argparse`` library for parsing the command line. Everything
starts in the ``__main__`` module. An ``ArgumentParser`` is constructed and each
subcommand is added. The subcommands are responsible for customizing their own
options and descriptions.

Each tem subcommand is implemented in its own module. In those modules there is
always a ``cmd`` function with the following skeleton:

.. code-block:: python

   def cmd(args):
       ...

This function performs the actions of the subcommand.

In addition, there is a ``setup_parser`` function that sets up the
``ArgumentParser`` for that subcommand.

.. code-block:: python

   def setup_parser(parser):
       ...

Since there is a fair bit of common functionality that different subcommands
use, there is a ``tem.cli`` module that provides this.

The module ``tem.util`` contains common functions that are used throughout the
project. The idea is to place everything that can exist independently from the
CLI here.

Internal environment variables
------------------------------

.. glossary::

   `__TEM_SHELL_SOURCE`
      Path to a file (preferably a FIFO) to which tem will echo shell commands,
      which the shell wrapper is supposed to source. A more detailed explanation
      can be found in :ref:`Shell<dev_shell>`.

   `__TEM_EXPORTED_ENVIRONMENT`
      Keeps track of the exported environment, so that env scripts are not
      executed multiple times. The value is the basedir and not the entire
      environment, since the environment can be obtained from the basedir alone.

   `__TEM_SESSION_ID__`
      TODO use this at all?
      The id of the current tem session (TODO a long random string that
      guarantees no collisions). It's used so that different shell sessions can
      have separate environments.
