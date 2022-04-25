``tem.var``
===========

.. toctree::

.. autolink-concat:: on
.. autolink-preface::

   from tem.var import *

Access tem variables using the full power of Python.

.. automodule:: tem.var
   :members:
   :exclude-members: VariableContainer

.. rubric:: Helpers
.. autoclass:: tem.var.VariableContainer

Examples
--------

Simplest way to add a variable
******************************

Although tem variables use Python code, you don't need to know Python to use
them. If you don't know

Defining variables
++++++++++++++++++

.. code:: python

   # A variable that can take any value from a list of allowed values
   build_type = Variable(["release", "debug"], default="debug")
   # A bool variable with default value False (also known as a variant)
   use_pipenv = Variable(bool)
   # The previous line is equivalent to the following:
   use_pipenv = Variant()
   # A variable whose value is used to update the `API_KEY` environment variable
   api_key = Variable(str, to_env="API_KEY")
   # Variable value is taken from `API_KEY2`, but changing the variable doesn't
   # change the environment variable
   api_key2 = Variable(str, from_env="API_KEY2")
   # The tem variable and the environment variable are bound together
   api_key3 = Variable(str, to_env="API_KEY3", from_env="API_KEY3")

Documenting variables
+++++++++++++++++++++

.. todo:: Not implemented

.. code:: python
   build_type.doc = "Build type"
   build_type.doc["release"] = "Release build"
   build_type.doc["debug"] = "Debug build"

Handy tricks
************

You can make variants mutually exclusive.

.. code:: python

   debug = Variant("debug")
   release = Variant("release")
   mutex(debug, release)

This way, if you try to do the following (assuming both ``debug`` and
``release`` were inactive beforehand):

.. code:: python

   activate(debug)
   activate(release)

it will fail, because the ``debug`` and ``release`` variants can't both be
active at the same time.

Advanced usage
**************

If you know a bit of python, you can do a lot more stuff with variables. For
example, you can define variables using the ``var`` decorator.

.. code:: python

   # Create a variable with an on_change callback
   @var
   def use_pipenv(value) -> bool:
      if value:
         os.environ["PIPENV_ACTIVE"] = str(1) if value else ""
      return value
   use_pipenv.value = True  # Set the default value

   # Create a variable that has a list of allowed values
