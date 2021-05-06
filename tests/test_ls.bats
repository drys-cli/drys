#!/usr/bin/env bats

. common.bats.in

if [ -z "$___WAS_RUN_BEFORE" ]; then
    begin_test 'ls'
    mkdir -p _out/repo;
    # Manually create repo inside _out/repo/
    ./prepare_files.sh files _out/repo
fi

@test "tem ls -R _out/repo -s" {
    run $EXE ls --reconfigure -R _out/repo -s
    [ "$output" = "$(ls _out/repo)" ]
}

@test "tem ls -R _out/repo -s file1" {
    run $EXE ls --reconfigure -R _out/repo -s file1
    [ "$output" = "file1.txt" ]
}

export ___WAS_RUN_BEFORE=true

# vim: ft=sh sw=4
