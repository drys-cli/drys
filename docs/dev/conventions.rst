Conventions
===========

Tem is very strict when it comes to adherence to standards and conventions. The
:ref:`zen` must be followed at all times. One of the goals of tem is to set new
standards when it comes to:

- The design of rich, smart and generalizable ecosystems
- Interoperability between existing tools
- The documentation of software for users and developers alike

.. _zen:

Zen Of Tem
----------

- Generality need not sacrifice usability
- Don't repeat yourself, or anyone else
- Use established standards and good practices and elevate them to new grounds
- Follow the Unix philosophy
- Develop tem to use tem; use tem to develop tem

.. note:: The zen is amendable.

Style guide
-----------

Always use ``functools.wraps`` around the wrapper function in a decorator, so
that the wrapper inherits the identity of the wrapee. This improves the
documentation.

Miscellaneous
-------------

- Internally used environment variables must start and end with `__`, following
  the python convention
