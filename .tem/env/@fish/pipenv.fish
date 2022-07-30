# Produce the same effects in the environment as 'pipenv run' would

if tem var -q use_pipenv 2>/dev/null
    if [ -z "$PIPENV_ACTIVE" ]
        set -le PIPENV_ACTIVE
        set -le VIRTUAL_ENV
        set -gx PIPENV_VERBOSITY -1
        set -l _pipenv_run_env_output (pipenv run env | string collect)

        set -l _path (echo "$_pipenv_run_env_output" | string match -r "^PATH=.*" | string replace -r "^PATH=" "")
        set -l _virtualenv (echo "$_pipenv_run_env_output" | string match -r "^VIRTUAL_ENV=.*" | string replace -r "^VIRTUAL_ENV=" "")
        export PATH="$_path"
        export VIRTUAL_ENV="$_virtualenv"
        set -gx PIPENV_ACTIVE 1
    end
end
