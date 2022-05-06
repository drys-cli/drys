Local scripts
=============

.. toctree::

Tem allows you to manage local scripts for each directory of your choosing.

- Scripts are run using `tem run \<script_name\>`.
- Scripts are stored in `.tem/path/` for each directory.
- If parent directories have `.tem/path/`, those scripts are also available to
  you.

The `.tem/path/` directory can be organized into a hierarchy, for example:

.. code-block::

   .tem/path/
   ├── build
   ├── git/
   │   ├── describe
   │   └── pre-commit
   ├── quality/
   │   ├── format
   │   └── lint
   ├── run
   ├── tests
   └── triage/
       ├── issue
       ├── PR
       └── todos

You can create those files manually, or you can use the :ref:`tem path<man_tem_path>` command.
