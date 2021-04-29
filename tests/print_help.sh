#!/usr/bin/env sh

[ -z "$EXE" ] && EXE=drys

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
print_help ls
print_help add
print_help put
print_help config
