#!/usr/bin/env bats

. common.bats.in

if [ -z "$___WAS_RUN_BEFORE" ]; then
    begin_test 'repo'
fi

REPOS="$PWD"/repos

# Helper function for the first two tests because they are identical
tem_repo_list_or_noargs() {
    run tem repo -R "$REPOS/repo1"
    expected="name1 @ $REPOS/repo1"
    compare_output_expected
    [ "$status" = 0 ]
}

@test "tem repo" {
    tem_repo_list_or_noargs
}

@test "tem repo --list" {
    tem_repo_list_or_noargs
}

@test "tem repo --list [Multiple repos]" {

    run tem repo -R "$REPOS/repo1" -R "$REPOS/repo2"

    expected="$(
        echo "name1 @ $REPOS/repo1"
        echo "name2 @ $REPOS/repo2"
    )"
    compare_output_expected
    [ "$status" = 0 ]
}

@test "tem repo --list --path [Multiple repos]" {

    run tem repo -lp -R "$REPOS/repo1" -R "$REPOS/repo2"

    expected="$(
        echo "$REPOS/repo1"
        echo "$REPOS/repo2"
    )"
    compare_output_expected
    [ "$status" = 0 ]
}

@test "tem repo --list --names [Multiple repos]" {

    run tem repo -ln -R "$REPOS/repo1" -R "$REPOS/repo2"

    expected="$(echo -e "name1\nname2")"
    compare_output_expected
    [ "$status" = 0 ]
}

@test "tem repo --list -R <MULTILINE_STRING>" {

    run tem repo -R "$(echo "$REPOS/repo1"; echo "$REPOS/repo2")"

    expected="$(
        echo "name1 @ $REPOS/repo1"
        echo "name2 @ $REPOS/repo2"
    )"
    compare_output_expected
    [ "$status" = 0 ]
}

@test "tem repo --add --list [MULTIPLE REPOS]" {
    # The command will output the resulting REPO_PATH

    run tem repo -alp "$REPOS"/repo*/

    expect printf '%s\n' "$DEFAULT_REPO" "$REPOS"/repo*
    compare_output_expected
}

@test "tem repo --remove --list [MULTIPLE REPOS]" {
    # The command will output the resulting REPO_PATH

    run tem repo -rlp "$REPOS"/repo{1,2}

    expected="$DEFAULT_REPO"
    compare_output_expected
}

export ___WAS_RUN_BEFORE=true

# vim: ft=sh sw=4
