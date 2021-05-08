.. _tem_tutorial:

============
tem-tutorial
============

.. todo:: Contents

DESCRIPTION
===========

For a comprehensive specification of all of tem's capabilities see
:ref:`tem(1)<man_tem>`. For information on how to configure tem, see
:ref:`tem-config(1)<man_tem_config>`.

BASIC USE CASE
==============

Scenario 1: Creating project templates
--------------------------------------

Say you frequently create projects that have a similar structure. It can be a
hassle to setup the file structure from scratch every time.

So what do you do?

You save a template somewhere and just copy it whenever you start
a new project. But if you are like me, you will quickly get tired of having to
`cd` back and forth every time. Also, if you have a lot of templates it can
get messy.

Using tem:

1. Create a repository of templates.

.. code-block:: none

   tem repo --add path/to/repoX

This will register a path as a default repository. There can be multiple default
repositories, and they are kept inside the user's configuration file as
'`general.default_repos`' (see :ref:`tem-config(1)<man_tem_config>`).

2. Add a project directory or file as a template

.. code-block:: none

   tem add path/to/projectX

This will create the file or directory `path/to/repoX/projectX`. You can also
categorize templates by putting them in subdirectories of a repository.

For example if `projectX` is a C++ project, you might want to do this instead:

.. code-block:: none

   tem add path/to/projectX -d cpp

which will create `path/to/repoX/cpp/projectX` ...

Scenario N: Different environments for different tastes
-------------------------------------------------------

.. todo:: This is planned somewhere along the road
