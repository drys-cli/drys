#!/usr/bin/env bats

. common.bats.in

if [ -z "$___WAS_RUN_BEFORE" ]; then
    begin_test 'ls'
    mkdir -p ~/repo;
    # Manually create repo inside ~/repo/
    ./prepare_files.sh files ~/repo
fi

tem_ls() {
    tem ls "$@"
}

@test "tem ls -R ~/repo" {
    run tem_ls -R ~/repo
    header="repo @ $(realpath ~)/repo"
    expected="$(
        echo "$header"
        echo "$(echo "$header" | sed 's/./=/g')"
        ls ~/repo
    )"
    compare_output_expected
}

@test "tem ls -R ~/repo -s" {
    run tem_ls -R ~/repo -s
    expect ls ~/repo
    compare_output_expected
}

@test "tem ls -R ~/repo -s file1" {
    run tem_ls -R ~/repo -s file1
    expected='file1.txt'
    compare_output_expected
}

export ___WAS_RUN_BEFORE=true

# vim: ft=sh sw=4
