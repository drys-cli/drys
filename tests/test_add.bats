#!/usr/bin/env bats

. common.bats.in

# Prepare an empty repository at the path in "$1"
prepare() {
    REPO="$1"
    mkdir -p "$REPO"
    rm -rf "$REPO"/*
    drys_add="$EXE add -R $REPO"
}

if [ -z "$___WAS_RUN_BEFORE" ]; then
    begin_test 'add'
    mkdir -p _out/files
    rm -rf _out/files/*
    ./prepare_files.sh files _out/files
fi

@test "drys add {FILE}" {
    prepare _out/add_singlefile1/

    $drys_add _out/files/file1.txt
    [ "$(cat $REPO/file1.txt)" = "$(cat _out/files/file1.txt)" ]
}

@test "drys add {FILE} [with -o xor -d]" {
    prepare _out/add_singlefile2/

    $drys_add _out/files/file1.txt -o _file1.txt
    [ "$(cat $REPO/_file1.txt)" = "$(cat _out/files/file1.txt)" ]

    $drys_add _out/files/file1.txt -d dir
    [ "$(cat $REPO/dir/file1.txt)" = "$(cat _out/files/file1.txt)" ]
}

@test "drys add {DIR}" {
    prepare _out/add_singledir/

    $drys_add _out/files
    compare_trees "$REPO/files" _out/files/**
}

@test "drys add {DIR} [with -o xor -d]" {
    prepare _out/add_singledir1/

    $drys_add _out/files -o dir
    compare_trees "$REPO/dir" _out/files/**

    $drys_add _out/files -d _dir
    compare_trees "$REPO/_dir/files" _out/files/**
}

@test "drys add {FILE1,FILE2}" {
    prepare _out/add_multifile/

    $drys_add _out/files/file1.txt _out/files/file2.txt
    compare_trees '_out/repo' _out/files/file{1,2}.txt
}

# TODO both -o and -d error

# NOTE: This modifies the contents of _out/files, so any tests that rely on
# these files must not come after this test
# @test "Move a file and a directory to a repository" {
    # rm -rf _out/repo2/*
    # mkdir -p _out/repo2
    # $EXE add -R _out/repo2 --move _out/files/file1.txt
    # $EXE add -R _out/repo2 --move _out/files/dir1
    # # Contents of the moved directory 'dir1'
    # ls_dir1="$(ls _out/repo2/dir1)"
    # # List the moved file
    # ls_file="$(ls _out/repo2/file1.txt)"
    # echo -e "Contents of '_out/repo2/dir1':\n$ls_dir1"
    # echo -e "Result of 'ls _out/repo2/file1.txt':\n$ls_file"
    # # Original files must be gone
    # [ ! -e '_out/files/dir1' ] && [ ! -e '_out/files/file1.txt' ]
    # # Contents of the moved 'dir1' must match the original
    # [ "$ls_dir1" = "$(ls files/dir1)" ]
    # # The moved file 'file1.txt' must exist in '_out/repo2'
    # [ "$ls_file" = '_out/repo2/file1.txt' ]
# }

export ___WAS_RUN_BEFORE=true

# vim: ft=sh sw=4
