#!/usr/bin/env sh

print_help() {
    mid="┃ Command: tem $* ┃"
    top="$(echo "$mid" | sed 's_._━_g' | sed 's_.\(.*\)._┏\1┓_')"
    bot="$(echo "$mid" | sed 's_._━_g' | sed 's_.\(.*\)._┗\1┛_')"

    echo "$top"
    echo "$mid"
    echo "$bot"
    tem "$@" --help
}

print_help

for cmd_raw in "$TEM_PROJECTROOT"/tem/cli/*.py; do
    cmd="$(basename ${cmd_raw%%.py})"
    # Ignore files starting with _ and some other files
    if [ -z "$(echo "$cmd" | sed -n '/^_/p')" ]\
        && [ "$cmd" != "errors" ]
    then
        print_help "$cmd"
    fi
done
