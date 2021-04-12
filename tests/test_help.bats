#!/usr/bin/env bats

[ -z "$EXE" ] && EXE=drys


@test "$EXE --help" {
    $EXE --help
}

@test "$EXE ls --help" {
    $EXE ls --help
}
@test "$EXE add --help" {
    $EXE --help
}
@test "$EXE put --help" {
    $EXE --help
}
