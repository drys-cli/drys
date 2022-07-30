if [ -z "$__PYTHONSTARTUP_DEFAULT" ]
    set -gx __PYTHONSTARTUP_DEFAULT "$PYTHONSTARTUP"
end
set -gx PYTHONSTARTUP (tem find -b tem)/.tem/files/.startup.py
