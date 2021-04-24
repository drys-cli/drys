#!/usr/bin/env bats

[ -z "$EXE" ] && EXE=drys
print() { echo -e "$*" >&2; }

if [ -z "$___WAS_RUN_BEFORE" ]; then
    print "\033[1;33mTest 'help'\033[0m"
fi

@test "drys {each_command...} --help" {
    ./print_help.sh
}

export ___WAS_RUN_BEFORE=true
