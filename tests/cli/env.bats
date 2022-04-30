. common.bats.in

if [ -z "$___WAS_RUN_BEFORE" ]; then
    begin_test 'env'
    rm -rf ~/.tem 2>/dev/null
    mkdir -p ~/.tem
    cp -r dottem/env ~/.tem/env
fi


@test "tem env --list" {
    cd ~

    run tem env --list

    expected='print.sh'
    expect echo -e 'print.sh\nunexecutable.sh'
    compare_output_expected
}

@test "tem env --exec --ignore [FILE]" {
    cd ~

    run tem env --exec --ignore unexecutable.sh

    expected='print.sh executed'
    compare_output_expected
}

@test "tem env --exec --list [FILE]" {
    cd ~

    run tem env --exec --list --ignore unexecutable.sh

    expect echo -e 'print.sh executed\nprint.sh'
    compare_output_expected
}

# Create files new_script1 and new_script2.
@test "tem env --new [MULTIPLE FILES]" {
    cd ~

    run tem env --new new_script1 new_script2

    expected=''
    compare_output_expected
    [ "$(ls .tem/env)" = "$(echo -e 'new_script1\nnew_script2\nprint.sh\nunexecutable.sh')" ]
}

# TODO
# @test "<ERROR_CHECK> tem env --new [MULTIPLE FILES]" {
    # cd ~ 1>/dev/null
    # run tem env --new new_script1 new_script2
    # expected=''

    # # compare_output_expected
    # [ "$(ls .tem/env)" = "$(echo -e 'new_script1\nnew_script2\nprint.sh\nunexecutable.sh')" ]
# }

# File new_script1 from the previous test is created again (--force option is
# used)
@test "tem env --new --force [MULTIPLE FILES]" {
    cd ~

    run tem env --new --force new_script1 new_script3

    expected=''
    compare_output_expected
    [ "$(ls .tem/env)" = "$(echo -e 'new_script1\nnew_script2\nnew_script3\nprint.sh\nunexecutable.sh')" ]
}

# @test "tem env --new --root [DIR] [MULTIPLE FILES]" {
#     rm -f ~/.tem/env/*
#     run tem env --new --root ~ new_script1 new_script2
#     expected=''

#     compare_output_expected
#     [ "$(ls ~/.tem/env)" = "$(echo -e 'new_script1\nnew_script2')" ]
# }

# @test "tem env --add --root [DIR] [MULTIPLE FILES]" {
#     rm -f ~/.tem/env/*
#     run tem env --add --root ~ dottem/env/*
#     expected=''

#     compare_output_expected
#     [ "$(ls ~/.tem/env)" = "$(ls tem/env)" ]
# }

@test "tem env --add --force [MULTIPLE FILES]" {
    cd ~
    rm -f .tem/env/*
    cp "$TESTDIR/cli/dottem/env/unexecutable.sh" .tem/env/

    run tem env --add --force "$TESTDIR"/cli/dottem/env/*

    expected=''
    compare_output_expected
    [ "$(ls .tem/env)" = "$(ls "$TESTDIR/cli/dottem/env")" ]
}

@test "tem env --add [NONEXISTENT FILE]" {
    cd ~
    rm -f .tem/env/*

    run tem env --add /nonexistentfile_blabla

    expected="tem env: warning: file '/nonexistentfile_blabla' does not exist"
    compare_output_expected
    [ -z "$(ls .tem/env)" ]
}

@test "tem env --delete [MULTIPLE FILES]" {
    cp -r dottem/env ~/.tem/
    cd ~

    run tem env --delete print.sh unexecutable.sh

    expected=''
    compare_output_expected
    [ -z "$(ls .tem/env)" ]
}

@test "tem env" {
    rm -f ~/.tem/env/*
    cp dottem/env/print.sh ~/.tem/env
    cd ~

    run tem env

    expected='print.sh executed'
    compare_output_expected
}

export ___WAS_RUN_BEFORE=true

# vim: ft=sh sw=4
