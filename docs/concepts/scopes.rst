Scopes
======

To fully utilize tem, you must know which scopes it recognizes.

Local scope
-----------

This scope is determined by the current working directory and all of its parent
directories. More specifically, only :term:`temdirs<Tem directory>` influence
the scope. For example if you are located in `/a/b/c`, the local scope is
influenced by the contents of `/a/.tem`, `/a/b/.tem` and `/a/b/c/.tem`.

User-global scope
-----------------

The user global scope is determined by the contents of the user-global config
directory for tem. This directory is platform-dependent.

System-global scope
-------------------
This scope is available to all users of a machine. It is determined by a system
config directory, which is platform-dependent.

Additional notes
----------------

To round things off, here are a few examples of how tem handles scope.
