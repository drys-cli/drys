import sys, os, glob
import argparse
from . import common, util

def setup_parser(subparsers):
    p = subparsers.add_parser('init',
                              help='generate a .tem directory here')
    common.add_common_options(p)

    p.add_argument('-H', '--example-hooks', action='store_true',
                   help='generate documented example hooks')
    p.add_argument('-f', '--force', action='store_true',
                   help='do not fail if .tem exists')
    p.add_argument('-v', '--verbose', action='store_true',
                   help='show the generated file tree')
    p.add_argument('-e', '--edit', action='store_true',
                   help='open generated files for editing')
    p.add_argument('-E', '--editor',
                   help='same as -e but override editor with EDITOR')
    # TODO a couple more options
    #  p.add_argument('-m', '--merge', action='store_true',
                   #  help='merge with existing')

    p.set_defaults(func=cmd)

def cmd(parser, args):
    import shutil as sh
    import subprocess
    from . import __prefix__

    if args.edit or args.editor:
        files = []

    if os.path.exists('.tem'):
        if args.force:
            if os.path.isdir('.tem'):
                sh.rmtree('.tem')
            else:
                os.remove('.tem')               # Remove existing
        else:                                   # Refuse to init if .tem exists
            print('tem: error: .tem directory already exists', end='',
                  file=sys.stderr)
            if not os.path.isdir('.tem'):
                print(' and is not a directory', end='', file=sys.stderr)
            print(file=sys.stderr)              # New line
            exit(1)

    try:
        os.mkdir('.tem')
        #  os.getcwd()
        os.mkdir('.tem/path')
        os.mkdir('.tem/hooks')
        # Copy example hooks
        if args.example_hooks:
            for file in glob.glob(__prefix__ + '/share/tem/hooks/*'):
                dest = sh.copy(file, '.tem/hooks/')
                os.chmod(dest, 0o744)
                if args.edit or args.editor:
                    files.append(dest)
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
        editor = common.get_editor(override=args.editor)
        p = common.try_open_in_editor(editor, files)
