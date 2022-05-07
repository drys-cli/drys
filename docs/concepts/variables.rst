Local variables
===============

.. toctree::

Tutorial:
   ..

Tem allows you to set variables on a per-directory basis, making them available
to you whenever you are in that directory.

Use cases
---------

- Create variables that manage which type of build you are using and switch them
  with a single command. These variables can be used in scripts to determine
  which variant of a script should be run.
- Manage and persist environment variables, so you don't have to pass them every
  time you run a program in a directory.
- Keep track if an action was ever performed in your project, for example
  greeting new users.

Basic workflow
--------------

1. `cd` into a tem directory (See :ref:`here<TODO>` how to create one).

2. Create variable definitions in a `.tem/vars.py` file. Here you declare
   variable types, their default values and various constraints.

3. Run `tem var` to add, edit, delete or inspect your local tem variables.

Usage example
-------------

TODO add snippet

Advanced usage
--------------

If you know a bit of python, you can do a lot more stuff with variables. You can
find advanced usage in the :ref:`Python API`.
