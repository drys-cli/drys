. common.bats.in

REPO="$PWD/_out/put_repo"
DESTDIR="$PWD/_out/put_dest"
tem_put() { tem put -R "$REPO" "$@"; }

if [ -z "$___WAS_RUN_BEFORE" ]; then
    begin_test 'put'
    mkdir -p "$REPO" "$DESTDIR"
    rm -rf "$REPO"/* "$DESTDIR"/*
    ./prepare_files.sh files "$REPO"
fi

@test "tem put {FILE}" {
    cd "$DESTDIR"

    tem_put file1.txt

    [ "$(cat "$DESTDIR"/file1.txt)" = "$(cat "$REPO"/file1.txt)" ]
}

@test "tem put {FILE} [with -o xor -d]" {
    cd "$DESTDIR"

    # --output
    tem_put file1.txt -o _file1.txt
    [ "$(cat "$DESTDIR"/_file1.txt)" = "$(cat "$REPO"/file1.txt)" ]

    # --directory
    tem_put file1.txt -d dir
    [ "$(cat "$DESTDIR"/dir/file1.txt)" = "$(cat "$REPO"/file1.txt)" ]
}

@test "tem put {DIR}" {
    cd "$DESTDIR"

    tem_put dir1

    compare_trees "$REPO"/dir1 "$DESTDIR"/dir1/**
}

# @test "tem put {}
# TODO both -o and -d error

export ___WAS_RUN_BEFORE=true

# vim: ft=sh sw=4
