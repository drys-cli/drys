#!/usr/bin/env bats

. common.bats.in

tem_repo() {
    $EXE repo --reconfigure "$@"
}

if [ -z "$___WAS_RUN_BEFORE" ]; then
    begin_test 'repo'
fi

REPOS="$PWD"/repos

# Helper function for the first two tests because they are identical
tem_repo_list_or_noargs() {
    run tem_repo -R "$REPOS/repo1"
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
    run tem_repo -R "$REPOS/repo1" -R "$REPOS/repo2" -R "$REPOS/repo3"
    expected="$(
        echo "name1 @ $REPOS/repo1"
        echo "name2 @ $REPOS/repo2"
        echo "repo3 @ $REPOS/repo3"
    )"
    compare_output_expected
    [ "$status" = 0 ]
}

@test "tem repo --list --path [Multiple repos]" {
    run tem_repo -lp -R "$REPOS/repo1" -R "$REPOS/repo2" -R "$REPOS/repo3"
    expected="$(
        echo "$REPOS/repo1"
        echo "$REPOS/repo2"
        echo "$REPOS/repo3"
    )"
    compare_output_expected
    [ "$status" = 0 ]
}

@test "tem repo --list --names [Multiple repos]" {
    run tem_repo -ln -R "$REPOS/repo1" -R "$REPOS/repo2" -R "$REPOS/repo3"
    expected="$(echo -e "name1\nname2\nrepo3")"
    compare_output_expected
    [ "$status" = 0 ]
}

@test "tem repo --list -R <MULTILINE_STRING>" {
    run tem_repo -R "$(echo "$REPOS/repo1"; echo "$REPOS/repo2")"
    expected="$(
        echo "name1 @ $REPOS/repo1"
        echo "name2 @ $REPOS/repo2"
    )"
    compare_output_expected
    [ "$status" = 0 ]
}

@test "PIPE | tem repo -R - --list --path" {
    expected="$(
        echo "$REPOS/repo1"
        echo "$REPOS/repo2"
    )"
    tem_repo_through_pipe() {
        echo "$expected" | $EXE repo --reconfigure -R - --list --path
        return $?
    }
    run tem_repo_through_pipe
    compare_output_expected
    [ "$status" = 0 ]
}

@test "tem repo --add --list [MULTIPLE REPOS]" {
    mkdir -p _out
    cp tem/config _out/config
    export TEM_CONFIG=_out/config

    # The command will output the resulting REPO_PATH
    run tem_repo -c _out/config -alp "$REPOS"/repo*/
    expect realpath "$REPOS"/repo*/
    compare_output_expected
}

@test "tem repo --remove --list [MULTIPLE REPOS]" {
    export TEM_CONFIG=_out/config

    # The command will output the resulting REPO_PATH
    run tem_repo -c _out/config -rlp "$REPOS"/repo{1,2}
    expect realpath "$REPOS"/repo3
    compare_output_expected
}

export ___WAS_RUN_BEFORE=true

# vim: ft=sh sw=4
