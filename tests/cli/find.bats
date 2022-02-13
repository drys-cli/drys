. common.bats.in

pushd() {
    builtin pushd "$@" >/dev/null
}

popd() {
    builtin popd "$@" >/dev/null
}

# NOTE: Output directory is under /tmp so as to avoid extra temdirs in the
# directory hierarchy
if [ -z "$___WAS_RUN_BEFORE" ]; then
    begin_test 'find'
    rm -rf /tmp/.tem # cut possible loose ends
    rm -rf /tmp/tem_find_test
    export HOME=/tmp/tem_find_test
    mkdir ~
    # Create temdir hierarchy
    mkdir -p ~/temdir1/dir2/temdir3/temdir4
    pushd ~/temdir1
    tem init >/dev/null
    pushd dir2
    pushd temdir3
    tem init >/dev/null
    pushd temdir4
    tem init >/dev/null
    popd; popd; popd; popd
fi

@test "tem find --base" {
    cd ~/temdir1/dir2/temdir3/temdir4

    run tem find --base

    [ "$status" = 0 ]
    expected=~/temdir1/dir2/temdir3/temdir4
    compare_output_expected
}

@test "tem find --root" {
    cd ~/temdir1/dir2/temdir3/temdir4

    run tem find --root

    [ "$status" = 0 ]
    expected=~/temdir1
    compare_output_expected
}

export ___WAS_RUN_BEFORE=true

# vim: ft=sh sw=4
