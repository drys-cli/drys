. common.bats.in

if [ -z "$___WAS_RUN_BEFORE" ]; then
    begin_test 'var'
    for i in $(seq 1 7); do
        rm -rf ~/var"$i"
        mkdir -p ~/var"$i"/.tem
        cp "$TESTDIR/var/vars.py" ~/var"$i"/.tem/vars.py
    done
fi

print_all_defaults() {
    printf "%s\n" \
        "str1 = 'val1'" \
        "str2 = 'val3'" \
        "bool1 = False" \
        "bool2 = True"
}

print_all_variable_names() {
    print_all_defaults | sed 's/\([^[:space:]]\) =.*/\1/'
}

# ┏━━━━━━━┓
# ┃ Tests ┃
# ┗━━━━━━━┛

@test "tem var <SINGLE ARG> [DEFAULT]" {
    cd ~/var1

    run tem var str1

    expected="$(print_all_defaults | grep str1)"
    compare_output_expected
}

@test "tem var [ALL, DEFAULTS]" {
    cd ~/var1

    run tem var

    [ "$status" = 0 ]
    expect print_all_defaults
    compare_output_expected
}

@test "tem var -q [VARIANTS, DEFAULTS]" {
    cd ~/var1

    run tem var -q bool1
    [ "$status" = 1 ]

    run tem var -q bool2
    [ "$status" = 0 ]

    run tem var -q bool1 bool2
    [ "$status" = 1 ]
}

@test "tem var -q [STRINGS, DEFAULTS]" {
    cd ~/var1

    run tem var -q str1:val1
    [ "$status" = 0 ]

    run tem var -q str1:nonexistent
    [ "$status" = 1 ]

    run tem var -q str1:val1 str2:val3
    [ "$status" = 0 ]

    run tem var -q str1:val1 str2:nonexistent
    [ "$status" = 1 ]
}

# Tests that modify the state

# NOTE: TOGGLE test depends on this
@test "tem var [ASSIGNMENT]" {
    cd ~/var2

    run tem var str1=val2

    [ "$status" = 0 ]
    expect printf "%s\n" "str1 = 'val2'"
    compare_output_expected

    run tem var bool1=true

    [ "$status" = 0 ]
    expect printf "%s\n" "bool1 = True"
    compare_output_expected
}

# NOTE: Depends on ASSIGNMENT test
@test "tem var bool1! [TOGGLE]" {
    cd ~/var3

    run tem var bool1!

    [ "$status" = 0 ]
    expect printf "%s\n" "bool1 = True"
    compare_output_expected
}

# Miscellaneous tests

@test "tem var [EDITED BEFOREHAND]" {
    cd ~/var4
    tem var str1=val2 bool1=True bool2=False

    run tem var

    [ "$status" = 0 ]
    expect printf "%s\n" "str1 = 'val2'" "str2 = 'val3'" "bool1 = True" "bool2 = False"
    compare_output_expected
}

@test "tem var -q <MISCELLANEOUS> [EDITED BEFOREHAND]" {
    cd ~/var5
    tem var str1=val2 bool1=True bool2=False

    run tem var -q str1:val2 bool1 bool2:false

    [ "$status" = 0 ]
}

@test "tem var <MISCELLANEOUS>" {
    cd ~/var6

    run tem var str1 bool1! str2=val4 bool2=false

    [ "$status" = 0 ]
    expect printf "%s\n" \
        "str1 = 'val1'" \
        "bool1 = True" \
        "str2 = 'val4'" \
        "bool2 = False"
    compare_output_expected
}

# ┏━━━━━━━━━━━━━┓
# ┃ Error tests ┃
# ┗━━━━━━━━━━━━━┛

warning() {
    echo "tem var: warning:" "$@"
}

err() {
    echo "tem var: error:" "$@"
}

warn_undefined() {
    warning "variable '$1' is not defined"
}

warn_bad_value() {
    warning "value '$2' does not match type for variable '$1'"
}

warn_invalid_expression() {
    warning "invalid expression: $1"
}

warn_toggle_only_variant() {
    warning "invalid expression: $1 (only variants can be toggled)"
}

err_query_only_variant() {
    err "invalid expression: $1 (only variants can be queried this way)"
}

err_invalid_expression() {
    err "invalid expression: $1"
}

err_invalid_expressions() {
    err "none of the specified expressions are valid"
}

@test "tem var <nonexistent>" {
    cd ~/var7

    run tem var nonexistent=1 2>&1

    [ "$status" = 1 ]
    expected="$(
        warn_undefined nonexistent
        err_invalid_expressions
    )"
    compare_output_expected

    run tem var nonexistent=1 str1=val2 2>&1

    [ "$status" = 0 ]
    expected="$(
        warn_undefined nonexistent
        echo "str1 = 'val2'"
    )"
    compare_output_expected
}

@test "tem var str1!- [BAD SYNTAX]" {
    cd ~/var7

    run tem var str1!-

    [ "$status" = 1 ]
    expected="$(
        warn_invalid_expression str1!-
        err_invalid_expressions
    )"
    compare_output_expected
}

@test "tem var str1=<bad_value>" {
    cd ~/var7

    run tem var str1=bad_value 2>&1

    [ "$status" = 1 ]
    expected="$(
        warn_bad_value str1 bad_value
        err_invalid_expressions
    )"
    compare_output_expected
}

@test "tem var str1! [TOGGLE NON-VARIANT]" {
    cd ~/var7

    run tem var str1! 2>&1
    [ "$status" = 1 ]
    expected="$(
        warn_toggle_only_variant str1!
        err_invalid_expressions
    )"
    compare_output_expected
}

@test "tem var -q str1 [QUERY NON-VARIANT AS VARIANT]" {
    cd ~/var7

    run tem var -q str1 str2:val3 2>&1

    [ "$status" = 1 ]
    expect err_query_only_variant str1
    compare_output_expected
}

@test "tem var -q bool1! [BAD SYNTAX]" {
    cd ~/var7

    run tem var -q bool1! 2>&1

    [ "$status" = 1 ]
    expect err_invalid_expression bool1!
    compare_output_expected
}

@test "tem var -d" {
    : # TODO
}

@test "tem var -e bool1 str2=val4" {
    : # TODO
}

@test "tem var -ze bool1 str2" {
    : # TODO
}

@test "tem var -de" {
    : # TODO
}

export ___WAS_RUN_BEFORE=true

# vim: ft=sh sw=4
