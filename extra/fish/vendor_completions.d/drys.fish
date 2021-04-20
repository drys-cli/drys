# Returns 0 when the commandline contains the specified argument
function __fish_drys_subcommand
    string match -qr -- "^$argv\$" (commandline -cpo)
    return $status
end

set -l SUBCOMMANDS add ls put 

# Return 0 if the last token is the one provided as argument
function __fish_drys_opt
    string match -q -- $argv[1] (commandline -cpo | tail -1)
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

complete_put -n '__fish_contains_opt -s d' --no-files
complete_put -s 'd' -l 'directory' -r -k --description 'Destination directory' --no-files \
    -a "(__fish_complete_directories)"
