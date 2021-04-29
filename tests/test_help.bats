#!/usr/bin/env bats

. common.bats.in

if [ -z "$___WAS_RUN_BEFORE" ]; then
    begin_test 'help'
fi

@test "drys {each_command...} --help" {
    ./print_help.sh
}

export ___WAS_RUN_BEFORE=true

# vim: ft=sh sw=4
