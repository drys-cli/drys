#!/usr/bin/env tuterm

# Setup
fake_home
tem --init-config
mkdir proj

run() {
    m 'Welcome to tem tutorial'
    c cd proj
    c mkdir hello
    c cd hello
    c tem put cpp/main.cpp cpp/CMakeLists.txt
    c ls
}

