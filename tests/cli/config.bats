. common.bats.in

if [ -z "$___WAS_RUN_BEFORE" ]; then
    begin_test 'config'
fi

@test "tem config section.option value -f ~/empty.cfg [MULTIPLE CONFIG OPTIONS]" {
    rm -f ~/empty.cfg

    tem config option1 value1 -f ~/empty.cfg
    tem config section2.option2 value2 -f ~/empty.cfg
    tem config section3.option3 value3 -f ~/empty.cfg
    tem config section3.option4 value4 -f ~/empty.cfg

    output="$(cat ~/empty.cfg)"
    expected="$(
        echo -e "[general]\noption1 = value1"
        echo -e "\n[section2]\noption2 = value2"
        echo -e "\n[section3]\noption3 = value3"
        echo -e "option4 = value4"
        )"
    compare_output_expected
}

@test "tem config section.option 'multi word' value -f ~/empty.cfg" {
    rm -f ~/empty.cfg

    tem config section.option 'multi word' value -f ~/empty.cfg

    output="$(cat ~/empty.cfg)"
    expect echo -e "[section]\noption = multi word value"
    compare_output_expected
}

@test "tem config -f PROJECT_ROOT/share/config" {

    run tem config -f "$PROJECT_ROOT/share/config"

    expected="$(
        echo -e "\033[1;4m$PROJECT_ROOT/share/config:\033[0m"
        echo "    "
        cat "$PROJECT_ROOT/share/config" | sed -e '/^#/d' -e 's/^/    /'
        echo "    "
    )"
    [ $status = 0 ]
    compare_output_expected
}

export ___WAS_RUN_BEFORE=true

# vim: ft=sh sw=4
