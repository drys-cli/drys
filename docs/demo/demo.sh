contract_user() {
    pwd | sed "s:$HOME:~:"
}
prompt() {
    echo -ne "\033[1;94mtem-demo \033[1;35m$(contract_user)\033[0;33m $\033[0m "
}

setup() {
    FAKE_HOME='/tmp/tuterm_tem_tutorial'
    [ -e "$FAKE_HOME" ] && rm -rf "$FAKE_HOME"
    cp -r "$(dirname "$TUTORIAL_FILE")"/.tem-home "$FAKE_HOME"

    if [ -n "$TEM_DEBUG" ]; then
        readonly TEM_CMD="$(abspath ../../tem.py)"
        tem() { "$TEM_CMD" -c ~/.config/tem/config "$@"; }
    else
        tem() { /usr/bin/env tem "$@"; }
    fi

    HOME="$FAKE_HOME"
    cd "$HOME"
}

run() {
    m 'Welcome to tem tutorial'
    c cd proj
    c mkdir hello
    c cd hello
    c tem put cpp/main.cpp cpp/CMakeLists.txt
    c ls
}

