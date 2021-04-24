# Returns 0 when the commandline contains the specified argument
function __fish_drys_subcommand
    string match -qr -- "^$argv\$" (commandline -cpo)
    return $status
end

set -l SUBCOMMANDS add ls put config

# Return 0 if the last token is the one provided as argument
function __fish_drys_opt
    string match -q -- $argv[1] (commandline -cpo | tail -1)
end

# TODO figure this out
function __fish_drys_ls
    set path ~/.local/share/drys/repo/
    set -l current "$path"(commandline -cpo | tail -1)
    notify-send "$current"
    [ ! -e "$current" ] && set -l current (dirname "$current")/
    echo "$current" > /tmp/TEST.txt
    set test (__fish_complete_path "$current" | sed "s:$path::")
    echo "$test"
end

# Default command
complete -c drys -n "not __fish_seen_subcommand_from $SUBCOMMANDS" --no-files -a "$SUBCOMMANDS"
complete -c drys -s 'h' -l 'help' -d 'Print help'

# drys put

function complete_put
    argparse -i 'n/condition=' -- $argv
    set -l conditions '__fish_seen_subcommand_from put' 
    [ -n "$_flag_n" ] && set -l conditions "$conditions && $_flag_n"
    complete -c drys -n "$conditions" $argv
end

complete_put -s 'd' -l 'directory' -r -k --description 'Destination directory' --no-files \
    -a "(__fish_complete_directories)"
complete_put -n 'not __fish_drys_opt -d && not __fish_drys_opt -o' --no-files \
    -a "(drys ls -s -e find -- '*')"

# drys config

function complete_config
    argparse -i 'n/condition=' -- $argv
    set -l conditions '__fish_seen_subcommand_from config' 
    [ -n "$_flag_n" ] && set -l conditions "$conditions && $_flag_n"
    complete -c drys -n "$conditions" $argv
end

complete_config --no-files
complete_config -s 'f' -l 'file' -r -a '__fish_complete_directories'
