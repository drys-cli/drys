from .common import cfg

def run(command, *args, **kwargs):
    from subprocess import run, PIPE
    """
    Call an external command with the specified arguments, honoring the user's
    command overrides.
    """
    # Get the user's preferred command from the config
    cmd_string = cfg.get(command[0], 'command', fallback='ls')
    # Parse the config entry with the shell
    parsed_args = run(['sh', '-c', r'printf "%s\n" {}'.format(cmd_string)],
                         stdout=PIPE, encoding='utf-8').stdout.split('\n')
    # Remove an extra empty entry that is generated because of an empty line
    parsed_args.pop(-1)
    # Parse the command with the substitution in mind
    return run(parsed_args + command[1:],
               *args, **kwargs)
