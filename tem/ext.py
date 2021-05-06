"""Functions and utilites used to properly call external commands."""
from .common import cfg
from . import common
import subprocess as sp

def parse_args(args):
    """
    Take the string `arg_str` and parse its components to a list of string
    arguments.
    """
    # Use the system shell to parse the string
    #   - the last element is a blank line which is popped before returning
    return sp.run(['sh', '-c', r'printf "%s\n" {}'.format(args)],
               stdout=sp.PIPE, encoding='utf-8').stdout.split('\n')[:-1]

def run(command, override=None, *args, **kwargs):
    """
    Call an external command with the specified arguments, honoring the user's
    command overrides. If `override` is specified, then that will be
    used as the command name instead of `command[0]`.
    """
    # The command is overridden (usually by the --command argument)
    if override:
        cmd_string = override
    else:
        # Get the user's preferred command from the config
        cmd_string = cfg.get(command[0], 'command', fallback=command[0])
    parsed_args = parse_args(cmd_string)
    # Parse the command with the substitution in mind
    try:
        return sp.run(parsed_args + command[1:],
                   *args, **kwargs)
    except Exception as e:
        common.print_error_from_exception(e)
        exit(1)
