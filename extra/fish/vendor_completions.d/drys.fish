set -l SUBCOMMANDS add ls put config repo

# {{{ Helper functions

# Defines a function __fish_drys_complete_*, where the wildcard is actually
# replaced by each drys subcommand (from $SUBCOMMANDS)
#
# Example:
#
# The function __fish_drys_complete_add acts as an alias for:
#
#   complete -c drys -n "__fish_seen_subcommand_from add"
#
# Also, additional conditions can be specified using -n and all the other
# options that work for complete will work for this command as well

for cmd in $SUBCOMMANDS
    eval\
    "function __fish_drys_complete_$cmd
         set -l conditions '__fish_seen_subcommand_from $cmd'"'
         argparse -i "n/condition=" -- $argv
         [ -n "$_flag_n" ] && set -l conditions "$conditions && $_flag_n"
         complete -c drys -n "$conditions" $argv
     end'
end

# Return 0 if the last token is the one provided as argument
function __fish_drys_last_arg
    string match -q -- $argv[1] (commandline -cpo | tail -1)
end

function __fish_drys_ls
    set -l comp (commandline -ct)
    for repo in (drys repo --list)
        pushd "$repo"
        if [ "$argv[1]" = '/' ]
            __fish_complete_directories "$comp" ''
        else
            complete -C"nOnExIsTeNtCoMmAndZIOAGA2329jdbfaFkahDf21234h8z43 $comp"
        end
        popd
    end
end

# }}}

# {{{ Default command (no subcommand)
complete -c drys -n "not __fish_seen_subcommand_from $SUBCOMMANDS" -f -a "$SUBCOMMANDS"
complete -c drys -s 'h' -l 'help' -d 'Print help' -f
# }}}

# {{{ drys put

__fish_drys_complete_put -f\
    -a "(__fish_drys_ls)"\
    -n 'not __fish_drys_last_arg -d && not __fish_drys_last_arg -o'

__fish_drys_complete_put -s 'o' -l 'output' -rkF -d 'Destination file'

__fish_drys_complete_put -s 'd' -l 'directory' -rf -d 'Destination directory'\
    -a "(__fish_complete_directories)"

# }}}

# {{{ drys add

__fish_drys_complete_add -s 'd' -l 'directory' -rkf -d 'Destination directory'\
    -a "(__fish_drys_ls /)"

__fish_drys_complete_add -s 'o' -l 'output' -rkf -d 'Destination file'\
    -a "(__fish_drys_ls)"

# }}}

# {{{ drys repo
__fish_drys_complete_repo -s 'l' -l 'list' -f
# }}}

# {{{ drys config

__fish_drys_complete_config -f
__fish_drys_complete_config -s 'f' -l 'file' -r -a '(__fish_complete_directories)'

# }}}

# vim: ft=fish foldmethod=marker sw=4
