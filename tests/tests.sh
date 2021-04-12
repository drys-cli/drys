#!/usr/bin/env sh

export EXE=drys
export BATS='bats --formatter pretty'

$BATS test_help.bats
