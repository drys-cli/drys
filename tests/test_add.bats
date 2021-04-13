#!/usr/bin/env bats

[ -z "$EXE" ] && EXE=drys

print() { echo -e "$*" >&2; }

if [ -z "$___WAS_RUN_BEFORE" ]; then
    print "\033[1;33mTest 'add'\033[0m"
    mkdir -p _out/files
    ./prepare_files.sh files _out/files
fi

# Compare the contents of the directory at $1 with the files specified in the
# remaining arguments. Perform a diff between each specified file with its
# counterpart in the directory at $2.
compare_trees() {
    shopt -s globstar
    original="$(cat "$1"/** 2>/dev/null || true)"
    repo="$(cat "${@:2}" 2>/dev/null || true)"
    run diff <(echo "$original") <(echo "$repo")
    echo Diff:; echo "$output" | awk '{print "\t",$0}'
    [ "$status" == 0 ]
}

setup() {
    [ -d '_out/repo' ] && rm -r _out/repo
    mkdir -p _out/repo;
}

@test "drys add -R _out/repo files" {
    $EXE add -R _out/repo _out/files
    shopt -s globstar
    compare_trees '_out/repo/files' _out/files/**
}

@test "drys add -R _out/repo files/file1.txt files/file2.txt" {
    $EXE add -R _out/repo _out/files/file1.txt _out/files/file2.txt
    compare_trees '_out/repo' _out/files/file{1,2}.txt
}

export ___WAS_RUN_BEFORE=true
