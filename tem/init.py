import sys, os, glob
import argparse
from . import common, util
from .util import print_cli_err

def setup_parser(subparsers):
    p = subparsers.add_parser('init', add_help=False,
                              help='generate a .tem directory')
    common.add_common_options(p)

    p.add_argument('-H', '--example-hooks', action='store_true',
                   help='generate documented example hooks')
    p.add_argument('-n', '--example-env', action='store_true',
                   help='generate documented example environment scripts')
    p.add_argument('-r', '--as-repo', action='store_true',
                   help='current directory will be initialized as a repository')
    common.add_edit_options(p)
    p.add_argument('-f', '--force', action='store_true',
                   help='do not fail if .tem exists')
    p.add_argument('-v', '--verbose', action='store_true',
                   help='show the generated file tree')
    # TODO a couple more options
    #  p.add_argument('-m', '--merge', action='store_true',
                   #  help='merge with existing')

    p.set_defaults(func=cmd)

@common.subcommand_routine('init')
def cmd(args):
    import shutil as sh
    import subprocess
    from . import __prefix__

    # Make sure that .tem/ is valid before doing anything else
    if os.path.exists('.tem'):
        if args.force:
            if os.path.isdir('.tem'):
                sh.rmtree('.tem')
            else:
                os.remove('.tem')               # Remove existing
        else:                                   # Refuse to init if .tem exists
            print_err('.tem already exists', end='')
            if not os.path.isdir('.tem'):
                print_err(' and is not a directory', end='')
            print_err()                         # New line
            exit(1)

    files = []                  # Keeps track of all files that have been copied
    # Copy the files
    try:
        SHARE_DIR = __prefix__ + '/share/tem/'
        os.mkdir('.tem')
        os.mkdir('.tem/path')
        os.mkdir('.tem/hooks')
        os.mkdir('.tem/env')
        # Create a list of files that will be copied
        files = [ SHARE_DIR + file for file in ['config', 'ignore'] ]
        if args.as_repo: files.append(SHARE_DIR + 'repo')
        if args.example_hooks:
            files += [ file for file in glob.glob(SHARE_DIR + 'hooks/*') ]
        if args.example_env:
            files += [ file for file in glob.glob(SHARE_DIR + 'env/*') ]
        # Copy files to .tem/
        for i, file in enumerate(files):
            dest = sh.copy(file, '.tem/' + file.replace(SHARE_DIR, ''))
            files[i] = dest
    except Exception as e:
        util.print_error_from_exception(e)

    print('Initialization was successful.')
    if args.verbose:
        # If 'tree' command exists, show the generated tree
        try:
            p = subprocess.run(['tree', '--noreport', '-F', '.tem/'],
                               encoding='utf-8', stdout=subprocess.PIPE)

            print('Generated tree:')
            print(p.stdout)
            print('Legend:\n\t/ directory\n\t* executable file')
        except Exception:
            pass
    if args.edit or args.editor:
        p = common.try_open_in_editor(files, override_editor=args.editor)
