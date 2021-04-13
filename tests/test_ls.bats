#!/usr/bin/env bats

[ -z "$EXE" ] && EXE=drys

print() { echo -e "$*" >&2; }

if [ -z "$___WAS_RUN_BEFORE" ]; then
    print "\033[1;33mTest 'ls'\033[0m"
    mkdir -p _out/repo;
    # Manually create repo inside _out/repo/
    ./prepare_files.sh files _out/repo
fi

# drys ls

@test "drys ls -R _out/repo -s" {
    run $EXE ls --reconfigure -R _out/repo -s
    [ "$output" = "$(ls _out/repo)" ]
}

@test "drys ls -R _out/repo -s file1" {
    run $EXE ls --reconfigure -R _out/repo -s file1
    [ "$output" = "$(echo file1.txt)" ]
}

@test "empty test" {
}

export ___WAS_RUN_BEFORE=true

