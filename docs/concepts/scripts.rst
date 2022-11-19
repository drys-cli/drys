Local scripts
=============

.. toctree::

Tem allows you to manage local scripts for each directory of your choosing.

- Scripts can be created using `tem path --edit <script_name>`
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

You can create those files manually, or you can use the `tem path`
command.

..
   TODO: make man page for `tem path`

**Example**:

- Create and edit the script `quality/lint` from above using `tem path --edit quality/lint`.
- To run the linter, you can run `tem run quality/lint`.

.. note::
   A planned feature is to give tem the ability to automatically hoist scripts to the top,
   so you can just use `tem run lint`. For the time being, on UNIX, you can create a symlink
   using:

   .. code-block:: shell

      ln -s .tem/path/quality/lint .tem/path/lint`

If you have a shell plugin installed and enabled (currently only the `fish`
shell is supported), you can omit `tem run` and just run `lint`. But you have to
run `tem env` beforehand, or have the fish plugin configured to do that
automatically when you `cd` into a directory.
