#!/usr/bin/env bats

. common.bats.in

if [ -z "$___WAS_RUN_BEFORE" ]; then
    begin_test 'tem'
fi

tem_() {
    "$TEM_EXECUTABLE" "$@"
}

@test "tem {each_command...} --help" {
    ./print_help.sh
}

@test "tem --init-user" {
    # Test if the command creates ~/.config/tem/config and
    # ~/.local/share/tem/repo
    tem_ --init-user
    expected="$(tree -a --noreport home/.config/ | tail -n +2)"
    cd ~
    output="$(tree -a --noreport ~/.config/ | tail -n +2)"
    compare_output_expected
    [ -d ~/.local/share/tem/repo ]
}

@test "tem --init-user [AGAIN] [ERR]" {
    run tem_ --init-user
    [ "$status" != 0 ]
}

export ___WAS_RUN_BEFORE=true

# vim: ft=sh sw=4
