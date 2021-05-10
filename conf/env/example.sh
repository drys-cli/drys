#!/usr/bin/env sh

# A script that is executed when `tem env` is run. The file name must not have a .pre
# or .post suffix.
#
# In order to be run correctly, it must be executable by the user (you might
# need a shebang).
# Alternatively, if you want to source this file using your current shell, you
# must have the appropriate extension installed and this file name must have the
# appropriate suffix (e.g. .bash, .zsh or .fish)
#
# Note: tem will first try to execute the file. The file will be sourced into
# the shell only if it fails to execute.
