Tests
=====

This project holds testing in very high regard. Code that is not properly tested
will not be accepted.

.. todo:: Add link to contrib guidelines.

How to test tem
---------------

This project provides multiple ways to test tem. For your local testing

Basic
*****

Once you have made a change in the code, you can execute :source:`tem.py`
instead of your system-wide installation of `tem`. This executable uses the
project-local configuration located at (`share/`), instead of the system
configuration.

.. todo:: Mention that one can use the project root as a tem env.

Standardized tests
******************

This method uses the tests located under the :source:`tests/` directory. They
are split up into:

- Python tests, which test the python API using `pytest`_
- CLI tests, which test the command line interface using `BATS`_

These tests can be run individually or in bulk with `make`, using
:source:`tests/Makefile`. The following targets are available:

Run all python tests:
   .. prompt:: bash

      make py

Run all CLI tests:
   .. prompt:: bash

      make cli

Run CLI tests for a tem subcommand (e.g. `tem cli`):
   .. prompt:: bash

      make {subcommand}

Run all tests (python and CLI):
   .. prompt:: bash

      make all

Run all tests in a docker container:
   .. prompt:: bash

      make docker-all

   This is the default make target. This is the most reliable way to test `tem`,
   and the one used to validate code contributed by the community.

If you want to run python tests manually, bypassing the Makefile, you have to
set some :ref:`environment variables<tests_envvars>`.

.. warning:: BATS tests should be run exclusively through `make`, never manually.

.. _pytest: https://pypi.org/project/pytest
.. _BATS: https://github.com/bats-core/bats-core

.. toctree::


Python tests
------------
Source: :source:`tests/py/`
   ..

CLI tests
---------
Source: :source:`tests/cli/`
   ..

.. _tests_envvars:

Environment variables
---------------------

These environment variables must be set for both pytest and BATS tests.

+-------------------+---------------------------------------------------------------------------+
| `TEM_PROJECTROOT` | Absolute path to the root project directory.                              |
+-------------------+---------------------------------------------------------------------------+
| `TESTDIR`         | Absolute path to :source:`tests/`.                                        |
+-------------------+---------------------------------------------------------------------------+
| `OUTDIR`          | Absolute path where test output files are stored (:source:`tests/_out/`). |
+-------------------+---------------------------------------------------------------------------+

