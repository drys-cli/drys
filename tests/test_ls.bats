#!/usr/bin/env bats

. common.bats.in

if [ -z "$___WAS_RUN_BEFORE" ]; then
    begin_test 'ls'
    mkdir -p _out/repo;
    # Manually create repo inside _out/repo/
    ./prepare_files.sh files _out/repo
fi

tem_ls() {
    tem ls --reconfigure "$@"
}

@test "tem ls -R _out/repo" {
    run tem_ls -R _out/repo
    expected="$(
        echo "repo @ _out/repo"
        echo "================"
        ls _out/repo
    )"
    compare_output_expected
}

@test "tem ls -R _out/repo -s" {
    run tem_ls -R _out/repo -s
    expect ls _out/repo
    compare_output_expected
}

@test "tem ls -R _out/repo -s file1" {
    run tem_ls -R _out/repo -s file1
    expected='file1.txt'
    compare_output_expected
}

export ___WAS_RUN_BEFORE=true

# vim: ft=sh sw=4
