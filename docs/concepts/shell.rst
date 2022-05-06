.. _shell:

Shell plugins
=============

.. toctree::

Tem is most useful when it is able to modify the state of the calling shell for
you. For example, having to type `tem run \<script\>` each time can be a hassle
compared to having `<script>` available in your `PATH`.

The default `tem` executable by itself cannot modify the state of the calling
shell. You need to install a shell plugin. There is a plugin for each of the
major shells (`bash`, `fish` and `zsh`). What a shell plugin does is define a
function called `tem` that wraps the `tem` executable. The way to do that is
platform-dependent:

.. tabs::

   .. tab:: Arch Linux

      .. tabs::

         .. tab:: Bash

            .. code:: shell

               pacman -S tem-bash

         .. tab:: Fish

            .. code:: shell

               pacman -S tem-fish

         .. tab:: Zsh

            .. code:: shell

               pacman -S tem-zsh


   .. tab:: ...rest

      TODO

The perks of using a shell plugin
---------------------------------

These are all the things you can do with tem that require a shell plugin:

- Tem can automatically make local scripts available in your `PATH` when you run
  `tem env`. In fact, tem with a shell plugin puts `.tem/path/` into the `PATH`
  by default. This behavior can be customized.
- You can define local shell variables, functions, completions, aliases and
  abbreviations (depending on the features supported by your shell).
- Tem can automatically load a local environment the moment you `cd` to a
  directory.
- You can use `tem cd` to conveniently `cd` to some predefined locations
  supported by tem.
