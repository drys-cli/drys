#!/usr/bin/env sh

[ -z "$EXE" ] && EXE=tem

print_help() {
    mid="┃ Command: $EXE $* ┃"
    top="$(echo "$mid" | sed 's_._━_g' | sed 's_.\(.*\)._┏\1┓_')"
    bot="$(echo "$mid" | sed 's_._━_g' | sed 's_.\(.*\)._┗\1┛_')"

    echo "$top"
    echo "$mid"
    echo "$bot"
    $EXE "$@" --help
}

print_help

for cmd_raw in "$(dirname "$TEM_EXECUTABLE")"/tem/cli/*.py; do
    cmd="$(basename ${cmd_raw%%.py})"
    print_help "$cmd"
done
