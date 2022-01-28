. common.bats.in

if [ -z "$___WAS_RUN_BEFORE" ]; then
    begin_test 'var'
    rm -rf ~/var
    mkdir -p ~/var/.tem
fi

@test "tem var -> default [INITIAL]" {
    # Test if initially only the default variant is active
    cd ~/var

    run tem var

    [ "$status" = 0 ]
    expected="default"
    compare_output_expected
}

@test "tem var a b" {
    # Activate variants 'a' and 'b'
    cd ~/var

    tem var a b

    output="$(cat .tem/.internal/variants)"
    expected=a$'\n'b
    compare_output_expected
}

@test "tem var" {
    # List variants. NOTE: depends on previous test.
    cd ~/var

    run tem var

    [ "$status" = 0 ]
    expected=a$'\n'b
    compare_output_expected
}

@test "tem var c --verbose" {
    # Activate 'c' and list all active variants. NOTE: depends on previous tests
    cd ~/var

    run tem var c --verbose

    echo "$output"
    [ "$status" = 0 ]
    expected=a$'\n'b$'\n'c
    compare_output_expected
}

@test "tem var --exclusive e ee" {
    # Make 'e' the only active variant.
    cd ~/var

    run tem var --exclusive e ee --verbose

    expected=e$'\n'ee
    compare_output_expected
}

@test "tem var --deactivate d" {
    # Activate 'd' and deactivate it.
    cd ~/var
    initial_state="$(tem var --exclusive a b c --verbose)"
    tem var --activate d

    run tem var --deactivate d --verbose

    [ "$status" = 0 ]
    expected="$initial_state"
    compare_output_expected
}

@test "tem var --query [VARIOUS]" {
    # NOTE: depends on previous test.
    cd ~/var

    tem var --query a
    tem var --query b
    tem var --query a b c
    run tem var --query d

    [ "$status" != 0 ]
}

export ___WAS_RUN_BEFORE=true

# vim: ft=sh sw=4
