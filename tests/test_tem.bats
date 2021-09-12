#!/usr/bin/env bats

. common.bats.in

if [ -z "$___WAS_RUN_BEFORE" ]; then
    begin_test 'tem'
fi

@test "tem {each_command...} --help" {
    ./print_help.sh
}

@test "tem --init-user" {
    # Test if the command creates ~/.config/tem/config and
    # ~/.local/share/tem/repo
    rm -rf ~/.config

    tem --init-user

    [ -f ~/.config/tem/config ]
    [ -d ~/.local/share/tem/repo ]
}

@test "tem --init-user [AGAIN] [ERR]" {

    run tem --init-user

    [ "$status" != 0 ]
}

export ___WAS_RUN_BEFORE=true

# vim: ft=sh sw=4
