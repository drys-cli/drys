#!/usr/bin/env bats

. common.bats.in

if [ -z "$___WAS_RUN_BEFORE" ]; then
    begin_test 'config'
    mkdir -p _out/;
fi

@test "tem config section.option value -f _out/empty.cfg [MULTIPLE CONFIG OPTIONS]" {
    rm -f _out/empty.cfg
    $EXE config option1 value1 -f _out/empty.cfg
    $EXE config section2.option2 value2 -f _out/empty.cfg
    $EXE config section3.option3 value3 -f _out/empty.cfg
    $EXE config section3.option4 value4 -f _out/empty.cfg

    output="$(cat _out/empty.cfg)"
    expected="$(
        echo -e "[general]\noption1 = value1"
        echo -e "\n[section2]\noption2 = value2"
        echo -e "\n[section3]\noption3 = value3"
        echo -e "option4 = value4"
        )"

    compare_output_expected
}

@test "tem config section.option 'multi word' value -f _out/empty.cfg" {
    rm -f _out/empty.cfg
    $EXE config section.option 'multi word' value -f _out/empty.cfg

    output="$(cat _out/empty.cfg)"
    expect echo -e "[section]\noption = multi word value"

    compare_output_expected
}

@test "tem config -f ../conf/config" {
    run $EXE config -f ../conf/config

    expected="$(
        echo ../conf/config:
        section=
        while read -r line; do
            if echo "$line" | grep -q '^\[.*\]$'; then
                section="$(sed 's_^\[\(.*\)\]_\1_' <<< "$line")"
            elif [ -n "$(sed -e '/^#/d' -e '/^$/d' <<< "$line")" ]; then
                echo "    $section.$line"
            fi
        done < ../conf/config
    )"

    [ $status = 0 ]
    compare_output_expected
}

export ___WAS_RUN_BEFORE=true

# vim: ft=sh sw=4
