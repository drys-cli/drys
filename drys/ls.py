import argparse

from . import common
from . import ext
import sys, os

def setup_parser(subparsers):
    p = subparsers.add_parser('ls', help='list templates')
    common.add_common_options(p)
    p.add_argument('-s', '--short', action='store_true',
                   help="don't display headers and decorations")
    p.add_argument('-r', '--recursive', action='append', default=[],
                   help='repository to be searched')
    p.add_argument('-R', '--repo', action='append', default=[],
                   help='repository to be searched')
    p.add_argument('templates', nargs='*',
                   help='which templates to list')
    p.add_argument('ls_arguments', nargs='*',
                   help='arguments that will be passed to ls')
    p.set_defaults(func=cmd)

# TODO obsolete!?
def print_contents(repo):
    print()
    for file in os.listdir(repo):
        print('\t', file, sep='', end='')
        if os.path.isdir(repo + '/' + file):
            print('/', end='')
        print()

def cmd(parser, args):
    import subprocess as sp
    # The repos that will be considered
    repos = args.repo if args.repo else common.repos
    ls_args = args.templates + args.ls_arguments

    # TODO Make it so that ls is always displayed per-file, so that other file
    # info can be appended if needed
    for repo in repos:
        # TODO should convert repos to absolute path
        os.chdir(repo)
        file_args = []; opt_args = []
        for arg in ls_args:
            if arg and arg[0] != '-':
                # Any missing file extensions are filled in here
                extended_args = sp.run(
                    ['sh', '-c', 'printf "%s\n" ' + arg + '*'],
                    stdout=sp.PIPE, encoding='utf-8'
                ).stdout.split('\n')[:-1]
                file_args += extended_args
            else:
                opt_args.append(arg)
        # TODO Check for excluded files
        p = ext.run(['ls', '-1'] + opt_args + file_args,
                    encoding='utf-8', stdout=sp.PIPE, stderr=sp.PIPE)
        if p.returncode != 0:
            if p.stdout: print(p.stdout)
            if p.stderr: print(p.stderr)
            return
        if not args.short:
            message = 'Repository @ ' + repo
            print(message); print('=' * len(message))
        if p.stdout: print(p.stdout[:-1])
        if p.stderr: print(p.stderr)
