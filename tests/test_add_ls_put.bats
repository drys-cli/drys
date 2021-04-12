#!/usr/bin/env bats

if [ -z "$___WAS_RUN_BEFORE" ]; then
    mkdir -p _out/files;
    ./prepare_files.sh files _out/files
fi

# drys add

@test "Create" {
    :
}

if [ -z "$___WAS_RUN_BEFORE" ]; then
    echo nice >&2
fi

export ___WAS_RUN_BEFORE=true
