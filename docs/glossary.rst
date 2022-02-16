Glossary
========

.. glossary::

   .. start parsing for inclusion in man page (TODO not implemented)

   Vanilla tem
      The default tem executable without any shell plugins applied.

   Template
      A file or directory that is meant to be reused.

   Tem repository
      A directory where templates are usually stored. Any directory can be
      a repository - no special requirements.

   Local environment
      An environment that is active only when you enter a directory, or
      one of its subdirectories.

   Tem directory
      Alias: **temdir**

      A directory that supports tem features. Always contains a `.tem/`
      subdirectory.

   Environment directory
      Alias: **envdir**

      A temdir that takes part in the active local environment.

   Base directory
      Alias: **basedir**

      The lowest :term:`temdir<Tem directory>` in the directory hierarchy.

   Root directory
      Alias: **rootdir**

      The topmost :term:`temdir<Tem directory>` in the directory hierarchy.

   Base envdir
      The lowest :term:`envdir<Environment directory>` in the directory
      hierarchy.

   Root envdir
      The topmost :term:`envdir<Environment directory>` in the directory
      hierarchy.

   Dot directory
      Also: **dotdir**

      A direct subdirectory of a `.tem/` directory. For example `.tem/path`,
      `.tem/env`, `.tem/hooks`, etc.

   .. stop parsing
