Overview
========

Tem uses python's ``argparse`` library for parsing the command line. Everything
starts in the ``__main__`` module. An ``ArgumentParser`` is constructed and each
subcommand is added. The subcommands are responsible for customizing their own
options and descriptions.

Each tem subcommand is implemented in its own module. In those modules there is
always a ``cmd`` function with the following skeleton:

.. code-block:: python

   @cli.subcommand_routine('SUBCOMMAND_NAME')
   def cmd(args):
       ...

This function performs the actions of the subcommand.

In addition, there is a ``setup_parser`` function that sets up the
``ArgumentParser`` for that subcommand.

.. code-block:: python

   def setup_parser(subparsers):
       ...

Since there is a fair bit of common functionality that different subcommands
use, there is a ``tem.cli`` module that provides this.

The module ``tem.util`` contains common functions that are used throughout the
project. The idea is to place everything that can exist independently from the
CLI here.
