#!/usr/bin/env bats

[ -z "$EXE" ] && EXE=drys

print() { echo -e "$*" >&2; }

if [ -z "$___WAS_RUN_BEFORE" ]; then
    print "\033[1;33mTest 'help'\033[0m"
fi

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

export ___WAS_RUN_BEFORE=true
