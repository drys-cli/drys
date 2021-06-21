import sys, os
import argparse

from . import common, util
from .util import print_cli_err

def setup_parser(subparsers):
    p = subparsers.add_parser('ls', add_help=False,
                              help='list templates')
    common.add_common_options(p)

    p.add_argument('-s', '--short', action='store_true',
                   help="don't display headers and decorations")
    p.add_argument('-p', '--path', action='store_true', help='print full path')
    p.add_argument('-x', '--command', metavar='CMD',
                   help='ls command to use')
    p.add_argument('-n', '--number', metavar='N', type=int,
                   help='list contents of no more than N repositories')
    common.add_edit_options(p)

    recursion = p.add_mutually_exclusive_group()
    recursion.add_argument('-r', '--recursive', action='store_true',
                           help='recurse into subdirectories')
    recursion.add_argument('--norecursive', dest='recursive',
                           action='store_false',
                           help='do not recurse into subdirectories [default]')

    p.add_argument('templates', metavar='TEMPLATES', nargs='*',
                   help='which templates to list')
    # TODO is there a way to show a '--' in the usage synopsis? I tried this but
    # '--' shows up at the end of help (argparse.SUPPRESS doesn't help either)
    # Also I would like this to show up after templates and before ls_arguments
    #  ATTEMPT: p.add_argument('--', action='store_true', dest='__discard')
    p.add_argument('ls_arguments', metavar='LS_ARGUMENTS', nargs='*',
                   help='arguments that will be passed to ls')
    p.set_defaults(func=cmd)

# TODO decouple the shorthand-completion part into another function
def separare_files_and_options(args):
    """
    Take a list of arguments and separate out files and options. An option is
    any string starting with a '-'. File arguments are relative to the current
    working directory and they can be incomplete. Any file argument will be
    completed to a valid path if a file whose name start with that argument
    exists. Returns a tuple (file_list, option_list).
    """
    file_args = []; opt_args = []

    for arg in args:
        if arg and arg[0] != '-':
            file_args.append(arg)
        else:
            opt_args.append(arg)
    return file_args, opt_args

# TODO Currently matches files that start with the incomplete_path entries
# I might try to make it more sophisticated some day
def fill_in_gaps(incomplete_paths):
    """
    Take all paths from `incomplete_paths` and complete them to match actual
    files. Returns a list that contains the completed paths.
    """
    import subprocess as sp
    paths = []
    for arg in incomplete_paths:
        paths += sp.run(
            ['sh', '-c', 'printf "%s\n" ' + arg + '*'],
            stdout=sp.PIPE, encoding='utf-8'
        ).stdout.split('\n')[:-1]
    return [ p for p in paths if os.path.exists(p) ]

@common.subcommand_routine('ls')
@common.subcommand_routine('ls')
def cmd(args):
    from . import ext
    import subprocess as sp
    # The repos that will be considered
    repos = common.form_repo_list(args.repo, cmd='ls')
    repos = common.resolve_and_validate_repos(repos)
    ls_args = args.templates + args.ls_arguments

    edit_files = []     # Files that will be edited if --edit[or] was provided
    original_cwd = os.getcwd()
    # TODO Make it so that ls is always displayed per-file, so that other file
    # info can be appended or prepended on each line
    for i, repo in enumerate(repos):
        os.chdir(repo)
        file_args, opt_args = separare_files_and_options(ls_args)
        # Any missing file extensions are filled in here
        # TODO Check for excluded files
        full_file_args = fill_in_gaps(file_args)
        if not any(os.scandir()) or (file_args and not full_file_args):
            continue                            # Nothing to show in this repo
        if args.path:
            full_file_args = [ os.path.abspath(f) for f in full_file_args ]
        cmd_args = ['ls'] + opt_args + full_file_args
        p = ext.run(cmd_args, override=args.command,
                    encoding='utf-8', stdout=sp.PIPE, stderr=sp.PIPE)
        if args.edit or args.editor:
            edit_files += [ os.path.abspath(f) for f in full_file_args ]
        # Print what the command spit out
        if p.returncode != 0:
            if p.stdout: print(p.stdout)
            if p.stderr: print_cli_err(p.stderr)
            return
        if not args.short:
            message = util.fetch_name(repo) + ' @ ' + repo
            print(message); print('=' * len(message))
        if p.stdout: print(p.stdout[:-1])
        if p.stderr: print_cli_err(p.stderr)

        if args.number and i >= args.number - 1:            # --number option
            break

    os.chdir(original_cwd)

    if edit_files:
        common.try_open_in_editor(edit_files)
