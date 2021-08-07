"""Functions and utilites used to properly call external commands."""
import os, shutil, subprocess as sp

from .cli import cfg
from . import util

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
    if isinstance(command, str):
        command = [command]
    # The command is overridden (usually by the --command argument)
    if override:
        cmd_string = override
    else:
        # Get the user's preferred command from the config
        cmd_string = cfg.get(command[0], 'command', fallback=command[0])
    # Parse the command with the substitution in mind
    parsed_args = parse_args(cmd_string)
    # If `tem` output is to a tty, make the subprocess think that its output is
    # also to a tty
    if os.isatty(1) and shutil.which('unbuffer'):
        parsed_args = ['unbuffer'] + parsed_args
    try:
        return sp.run(parsed_args + command[1:],
                   *args, **kwargs)
    except Exception as e:
        util.print_error_from_exception(e)
        exit(1)
