"""Functions and utilites for interfacing with external commands."""
import os
import shutil
import subprocess as sp
import sys

from .config import cfg


def parse_args(args):
    """
    Take the string `arg_str` and parse its components to a list of string
    arguments.
    """
    # Use the system shell to parse the string
    #   - the last element is a blank line which is popped before returning
    return sp.run(
        ["sh", "-c", rf'printf "%s\n" {args}'],
        stdout=sp.PIPE,
        encoding="utf-8",
        check=False,
    ).stdout.split("\n")[:-1]


def run(command, *args, override=None, **kwargs):
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
        cmd_string = cfg.get(command[0], "command", fallback=command[0])
    # Parse the command with the substitution in mind
    parsed_args = parse_args(cmd_string)
    # If `tem` output is to a tty, make the subprocess think that its output is
    # also to a tty
    if os.isatty(1) and shutil.which("unbuffer"):
        parsed_args = ["unbuffer"] + parsed_args
    try:
        return sp.run(parsed_args + command[1:], *args, check=False, **kwargs)
    except Exception as e:
        # TODO create front end in cli
        # pylint: disable-next=import-outside-toplevel
        from .cli import common as cli

        cli.print_exception_message(e)
        sys.exit(1)


shell = cfg["general.shell"]
if not shell:
    shell = os.environ.get("SHELL")


def shell_arglist(commandline):
    """
    Return the list of arguments that /bin/sh would parse from
    ``commandline``.
    .. note:: The shell is run as a subcommand for this.
    """
    p = sp.run(
        f"printf '%s\n' {commandline}",
        shell=True,
        stdout=sp.PIPE,
        encoding="utf-8",
        check=False,
    )
    return p.stdout.split("\n")[:-1]
