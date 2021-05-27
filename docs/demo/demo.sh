contract_user() {
    pwd | sed "s:$HOME:~:"
}
prompt() {
    echo -ne "\033[1;94mtem-demo \033[1;35m$(contract_user)\033[0;33m $\033[0m "
}

setup() {
    FAKE_HOME='/tmp/tuterm_tem_tutorial'
    [ -e "$FAKE_HOME" ] && rm -rf "$FAKE_HOME"
    cp -r home "$FAKE_HOME"

    TEM_CMD="$(abspath ../../tem.py)"
    tem() {
        "$TEM_CMD" -c ~/.config/tem/config "$@"
    }

    HOME="$FAKE_HOME"
    cd "$HOME"
}

run() {
    m 'tem tutorial'
    c cd proj
    c mkdir HelloWorld
    c cd HelloWorld
    # c tem ls cpp/main.cpp
    c tem put cpp/main.cpp cpp/CMakeLists.txt
    c ls
    prompt
    echo
}

