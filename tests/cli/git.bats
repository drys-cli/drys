. common.bats.in

pushd() {
    command pushd "$@" 1>/dev/null 2>/dev/null
}

shopt -s globstar

if [ -z "$___WAS_RUN_BEFORE" ]; then
    begin_test 'git'
    rm -rf ~/.tem                       2>/dev/null
    mkdir -p ~
    rm -rf ~/git
    cp -r git ~/git
    # NOTE: Don't forget about this
    cd ~/git
    git config --global init.defaultBranch master
    git config --global user.email "bats@tem"
    git config --global user.name "bats"
    git init                            1>/dev/null
    git add **/*.c **/*.h
    git commit -m "Initial commit"      1>/dev/null
    git checkout -b tem-vim             2>/dev/null
    git add **/vimrc
    git commit -m "Add vimrc files"     1>/dev/null
    git checkout -b tem-nvim            2>/dev/null
    git add **/nvimrc
    git commit -m "Add nvimrc files"    1>/dev/null
    cd "$TESTDIR/cli"
fi

@test "tem git --branch tem-vim" {
    cd ~/git
    git checkout master                 2>/dev/null

    run tem git --checkout --branch tem-vim

    # tem-vim contains everything master does plus extra
    output="$(find * -type f -not -path '*/\.*' | sort)"
    expect git ls-tree -r --name-only tem-vim
    compare_output_expected
}

@test "tem git --checkout --branch tem-nvim" {
    cd ~/git
    git checkout master                 2>/dev/null

    run tem git --checkout --branch tem-nvim

    output="$(find * -type f -not -path '*/\.*' | sort)"
    expect git ls-tree -r --name-only tem-nvim
    compare_output_expected
}

@test "tem git --list" {
    cd ~/git
    git checkout master                 2>/dev/null

    run tem git --list -b tem-vim

    expect echo -e 'subdir/vimrc\nvimrc'
    compare_output_expected
}

export ___WAS_RUN_BEFORE=true

# vim: ft=sh sw=4
