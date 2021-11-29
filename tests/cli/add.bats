. common.bats.in

# Prepare an empty repository at the path in "$1"
prepare() {
    REPO="$1"
    mkdir -p "$REPO"
    rm -rf "$REPO"/*
    tem_add () {
        tem add -R $REPO "$@"
    }
}

if [ -z "$___WAS_RUN_BEFORE" ]; then
    begin_test 'add'
    mkdir -p ~/files
    rm -rf ~/files/*
    ./prepare_files.sh files ~/files
fi

@test "tem add {FILE}" {
    prepare ~/add_singlefile1/

    tem_add ~/files/file1.txt

    [ "$(cat $REPO/file1.txt)" = "$(cat ~/files/file1.txt)" ]
}

@test "tem add {FILE} [with -o xor -d]" {
    prepare ~/add_singlefile2/

    # --output
    tem_add ~/files/file1.txt -o _file1.txt
    [ "$(cat $REPO/_file1.txt)" = "$(cat ~/files/file1.txt)" ]

    # --directory
    tem_add ~/files/file1.txt -d dir
    [ "$(cat $REPO/dir/file1.txt)" = "$(cat ~/files/file1.txt)" ]
}

@test "tem add {DIR}" {
    prepare ~/add_singledir/

    tem_add ~/files

    compare_trees "$REPO/files" ~/files/**
}

@test "tem add {DIR} [with -o xor -d]" {
    prepare ~/add_singledir1/

    # --output
    tem_add ~/files -o dir
    compare_trees "$REPO/dir" ~/files/**

    # --directory
    tem_add ~/files -d _dir
    compare_trees "$REPO/_dir/files" ~/files/**
}

@test "tem add {FILE1,FILE2}" {
    prepare ~/add_multifile/

    tem_add ~/files/file1.txt ~/files/file2.txt

    compare_trees "$REPO" ~/files/file{1,2}.txt
}

# TODO both -o and -d error

# NOTE: This modifies the contents of ~/files, so any tests that rely on
# these files must not come after this test
# @test "Move a file and a directory to a repository" {
    # rm -rf ~/repo2/*
    # mkdir -p ~/repo2
    # tem add -R ~/repo2 --move ~/files/file1.txt
    # tem add -R ~/repo2 --move ~/files/dir1
    # # Contents of the moved directory 'dir1'
    # ls_dir1="$(ls ~/repo2/dir1)"
    # # List the moved file
    # ls_file="$(ls ~/repo2/file1.txt)"
    # echo -e "Contents of '~/repo2/dir1':\n$ls_dir1"
    # echo -e "Result of 'ls ~/repo2/file1.txt':\n$ls_file"
    # # Original files must be gone
    # [ ! -e '~/files/dir1' ] && [ ! -e '~/files/file1.txt' ]
    # # Contents of the moved 'dir1' must match the original
    # [ "$ls_dir1" = "$(ls files/dir1)" ]
    # # The moved file 'file1.txt' must exist in '~/repo2'
    # [ "$ls_file" = '~/repo2/file1.txt' ]
# }

export ___WAS_RUN_BEFORE=true

# vim: ft=sh sw=4
