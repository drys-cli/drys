#!/usr/bin/env bats

. common.bats.in

tem_env() {
    $EXE env --reconfigure "$@"
}
pushd() {
    command pushd "$@" 1>/dev/null
}

if [ -z "$___WAS_RUN_BEFORE" ]; then
    begin_test 'env'
    rm -rf _out/.tem 2>/dev/null
    mkdir -p _out/.tem
    cp -r tem/env _out/.tem/env
fi


@test "tem env --list" {
    pushd _out
    run tem_env --list
    expected='print.sh'
    expect echo -e 'print.sh\nunexecutable.sh'

    compare_output_expected
    popd # _out
}

@test "tem env --exec --ignore [FILE]" {
    pushd _out
    run tem_env --exec --ignore unexecutable.sh
    expected='print.sh executed'

    compare_output_expected
    popd # _out
}

@test "tem env --exec --list [FILE]" {
    pushd _out
    run tem_env --exec --list --ignore unexecutable.sh
    expect echo -e 'print.sh executed\nprint.sh'

    compare_output_expected
    popd #_out
}

# Create files new_script1 and new_script2. Root directory is _out/.
@test "tem env --new [MULTIPLE FILES]" {
    pushd _out
    run tem_env --new new_script1 new_script2
    expected=''

    compare_output_expected
    [ "$(ls .tem/env)" = "$(echo -e 'new_script1\nnew_script2\nprint.sh\nunexecutable.sh')" ]
    popd # _out
}

# TODO
# @test "<ERROR_CHECK> tem env --new [MULTIPLE FILES]" {
    # pushd _out 1>/dev/null
    # run tem_env --new new_script1 new_script2
    # expected=''

    # # compare_output_expected
    # [ "$(ls .tem/env)" = "$(echo -e 'new_script1\nnew_script2\nprint.sh\nunexecutable.sh')" ]
    # popd
# }

# File new_script1 from the previous test is created again (--force option is
# used)
@test "tem env --new --force [MULTIPLE FILES]" {
    pushd _out
    run tem_env --new --force new_script1 new_script3
    expected=''

    compare_output_expected
    [ "$(ls .tem/env)" = "$(echo -e 'new_script1\nnew_script2\nnew_script3\nprint.sh\nunexecutable.sh')" ]
    popd # _out
}

@test "tem env --new --root [DIR] [MULTIPLE FILES]" {
    rm -f _out/.tem/env/*
    run tem_env --new --root _out new_script1 new_script2
    expected=''

    compare_output_expected
    [ "$(ls _out/.tem/env)" = "$(echo -e 'new_script1\nnew_script2')" ]
}

@test "tem env --add --root [DIR] [MULTIPLE FILES]" {
    rm -f _out/.tem/env/*
    run tem_env --add --root _out tem/env/*
    expected=''

    compare_output_expected
    [ "$(ls _out/.tem/env)" = "$(ls tem/env)" ]
}

@test "tem env --add --force [MULTIPLE FILES]" {
    pushd _out
    rm -f _out/.tem/env/print.sh
    run tem_env --add --force ../tem/env/*
    expected=''

    compare_output_expected
    [ "$(ls .tem/env)" = "$(ls ../tem/env)" ]
    popd # _out
}

@test "tem env --add [NONEXISTENT FILE]" {
    pushd _out
    rm -f .tem/env/*
    run tem_env --add /nonexistentfile_blabla
    expected="tem: warning: file '/nonexistentfile_blabla' doesn't exist"

    compare_output_expected
    [ -z "$(ls .tem/env)" ]
    popd # _out
}

@test "tem env --delete [MULTIPLE FILES]" {
    cp -r tem/env _out/.tem/
    pushd _out
    run tem_env --delete print.sh unexecutable.sh
    expected=''

    compare_output_expected
    [ -z "$(ls .tem/env)" ]
    popd # _out
}

@test "tem env" {
    rm -f _out/.tem/env/*
    cp tem/env/print.sh _out/.tem/env
    pushd _out
    run tem_env
    expected='print.sh executed'

    compare_output_expected
    popd # _out
}

export ___WAS_RUN_BEFORE=true

# vim: ft=sh sw=4
