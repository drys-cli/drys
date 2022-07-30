# Produce the same effects in the environment as 'pipenv run' would
set -e PIPENV_ACTIVE
set -l _path (pipenv run env | grep "^PATH=" | sed 's/^PATH=//')
set -l _virtualenv (pipenv run env | grep "^VIRTUAL_ENV=" | sed 's/^VIRTUAL_ENV=//')
export PATH="$_path"
export VIRTUAL_ENV="$_virtualenv"
set -gx PIPENV_ACTIVE 1

if [ -z "$__PYTHONSTARTUP_DEFAULT" ]
    set -gx __PYTHONSTARTUP_DEFAULT "$PYTHONSTARTUP"
end
set -gx PYTHONSTARTUP (tem find -b tem)/.tem/files/.startup.py
