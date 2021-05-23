contract_user() {
    pwd | sed "s:$HOME:~:"
}
prompt() {
    echo -n "\033[1;94mtem-demo \033[1;35m$(contract_user)\033[0;33m $\033[0m "
}
configure() {
    # delay in milliseconds
    DELAY=0.04
    DELAY_SEP=0.1
    DELAY_PROMPT=0.6

    # Setup _home directory
    [ -e _home ] && rm -rf _home
    cp -r home _home/
    HOME="$(abspath _home)"
    TEM_CMD="$(abspath ../../tem.py)"
    tem() {
        "$TEM_CMD" -c ~/.config/tem/config "$@"
    }
    cd _home
}

tutorial() {
    c cd proj
    c mkdir HelloWorld
    c cd HelloWorld
    # c tem ls cpp/main.cpp
    c tem put cpp/main.cpp cpp/CMakeLists.txt
    c ls
    prompt
    echo
}

