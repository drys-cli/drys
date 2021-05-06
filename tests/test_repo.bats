#!/usr/bin/env bats

. common.bats.in

compare_output_expected() {
    echo -e "Output:\n$output"
    echo -e "Expected:\n$expected"
    [ "$output" = "$expected" ]
}

drys_repo() {
    $EXE repo --reconfigure "$@"
}

if [ -z "$___WAS_RUN_BEFORE" ]; then
    begin_test 'repo'
fi

REPOS="$PWD"/repos

@test "drys repo --list" {
    run drys_repo -R "$REPOS/repo1"
    expected="name1 @ $REPOS/repo1"
    compare_output_expected
    [ "$status" = 0 ]
}

@test "drys repo --list [Multiple repos]" {
    run drys_repo -R "$REPOS/repo1" -R "$REPOS/repo2" -R "$REPOS/repo3"
    expected="$(
        echo "name1 @ $REPOS/repo1"
        echo "name2 @ $REPOS/repo2"
        echo "repo3 @ $REPOS/repo3"
    )"
    compare_output_expected
    [ "$status" = 0 ]
}

@test "drys repo --list --path [Multiple repos]" {
    run drys_repo -lp -R "$REPOS/repo1" -R "$REPOS/repo2" -R "$REPOS/repo3"
    expected="$(
        echo "$REPOS/repo1"
        echo "$REPOS/repo2"
        echo "$REPOS/repo3"
    )"
    compare_output_expected
    [ "$status" = 0 ]
}

@test "drys repo --list --names [Multiple repos]" {
    run drys_repo -ln -R "$REPOS/repo1" -R "$REPOS/repo2" -R "$REPOS/repo3"
    expected="$(echo -e "name1\nname2\nrepo3")"
    compare_output_expected
    [ "$status" = 0 ]
}

@test "drys repo --list -R <MULTILINE_STRING>" {
    run drys_repo -R "$(echo "$REPOS/repo1"; echo "$REPOS/repo2")"
    expected="$(
        echo "name1 @ $REPOS/repo1"
        echo "name2 @ $REPOS/repo2"
    )"
    compare_output_expected
    [ "$status" = 0 ]
}

@test "PIPE | drys repo -R - --list --path" {
    expected="$(
        echo "$REPOS/repo1"
        echo "$REPOS/repo2"
    )"
    drys_repo_through_pipe() {
        echo "$expected" | $EXE repo --reconfigure -R - --list --path
        return $?
    }
    run drys_repo_through_pipe
    compare_output_expected
    [ "$status" = 0 ]
}

export ___WAS_RUN_BEFORE=true

# vim: ft=sh sw=4
