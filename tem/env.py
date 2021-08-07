import sys, os
import argparse

from . import cli, util, dot
from .util import print_cli_err, print_cli_warn, print_err

def setup_parser(subparsers):
    p, _ =  dot.setup_parser_intermediate (
        subparsers, 'env', help='run or modify local environments'
    )
    p.set_defaults(func=cmd)

def validate_file_arguments_as_script_names(files):
    any_invalid_files = False
    for file in files:
        if '/' in file:
            print_cli_err("file '{}' is invalid".format(file))
            any_invalid_files = True
    if any_invalid_files: exit(1)

def get_and_validate_rootdir(args):
    rootdir = None
    subdir = '/.tem/' + (args.subdir if args.subdir else 'env')
    if args.root:                                   # --root option
        rootdir = args.root
    else:
        # We have to look upwards for a suitable rootdir
        if args.recursive:
            cwd = os.getcwd()
            # Find a parent directory with a subdirectory tree as in `subdir`
            while cwd != '/':
                if os.path.isdir(cwd + subdir):     # Env dir exists under `cwd`
                    rootdir = cwd
                    break
                cwd = os.path.dirname(cwd)          # Go up one directory
            if cwd == '/':                          # Nothing was found
                print_cli_err("environment directory was not found")
                if args.exec or not args.force: exit(1)
        else:
            rootdir = '.'
    subdir = rootdir + subdir
    if not rootdir or not os.path.isdir(subdir):
        # Environment directory is invalid
        if os.path.exists(subdir):
            print_cli_err("'{}' exists and is not a directory".format(subdir))
            print_err('Try running `tem init --force` first.')
        else:
            print_cli_err("directory '{}' not found".format(subdir))
            print_err('Try running `tem init` first.')
        if args.exec or not args.force: exit(1)

    return rootdir, subdir

@cli.subcommand_routine('env')
def cmd(args):
    # TODO:
    #   --add: handle multiple files with same name
    # Exec is the default action if no other actions have been specified
    if not (args.new or args.add or args.edit or args.editor or args.list):
        args.exec = True
    rootdir, subdir = get_and_validate_rootdir(args)
    args.files = [ file for file in args.files if file not in args.ignore ]
    # TODO determine what constitutes a failed run, and what is just a skip
    import subprocess
    if args.new:                                                # --new option
        validate_file_arguments_as_script_names(args.files)
        any_conflicts = False
        dest_files = []
        for file in args.files:
            dest = subdir + '/' + file
            if not os.path.exists(dest):
                open(dest, 'x').close()                     # Create empty file
                os.chmod(dest, os.stat(dest).st_mode | 0o100)       # chmod u+x
            elif args.force:
                os.chmod(dest, os.stat(dest).st_mode | 0o100)       # chmod u+x
            else:
                any_conflicts = True
                print_cli_err("file '{}' already exists".format(dest))
            dest_files.append(dest)
        if any_conflicts:
            print_err('\nTry running with --force.')
            exit(1)
        elif args.edit or args.editor:
            cli.try_open_in_editor(dest_files, args.editor)
    elif args.add:                                              # --add option
        import shutil
        any_nonexisting = False
        any_conflicts = False
        dest_files = []
        for src in args.files:
            dest = subdir + '/' + util.basename(src)
            if os.path.exists(src):
                if not os.path.exists(dest) or args.force:
                    shutil.copy(src, dest)
                else:
                    print_cli_warn("file '{}' already exists".format(dest))
                    any_conflicts = True
            else:
                print_cli_warn("file '{}' doesn't exist".format(src))
                any_nonexisting = True
            dest_files.append(dest)         # Files that may be opened by editor
        if any_nonexisting or any_conflicts:
            exit(1)
        elif args.edit or args.editor:
            cli.try_open_in_editor(dest_files, args.editor)
    elif args.delete:                                       # --delete option
        any_problems = False
        for file in args.files:
            target_file = subdir + '/' + file
            if os.path.isfile(target_file):
                os.remove(target_file)
            elif os.path.isdir(target_file):
                print_cli_warn("'{}' is a directory"
                          .format(target_file))
            else:
                print_cli_warn("file '{}' doesn't exist")
        if any_problems:
            exit(1)
    else:
        # If no files are passed as arguments, use all files from .tem/env/
        if not args.files:
            args.files = [ file for file in os.listdir(subdir)
                          if file not in args.ignore ]
        if not args.files and args.verbose:
            print_cli_warn('no environment scripts found')
            exit(1)
        elif args.edit or args.editor:
            cli.try_open_in_editor([ subdir + '/' + f for f in args.files ],
                                       args.editor)
            return
        elif args.exec:                                         # --exec option
            os.environ['PATH'] = util.abspath(rootdir) + '/.tem/path:' \
                + os.environ['PATH']
            for file in args.files:
                if os.path.isdir(subdir + '/' + file):
                    continue
                if args.edit or args.editor:
                    cli.try_open_in_editor(files, override_editor=args.editor)
                try:
                    subprocess.run(subdir + '/' + file)
                    if args.verbose:
                        print_err("tem: info: script `{}` was run successfully"
                                  .format(file))
                except:
                    print_cli_err("script `{}` could not be run"
                              .format(file))
                    exit(1)
    if args.list:                                               # --list option
        import subprocess; from . import ext
        ls_args = ['ls', '-1']
        os.chdir(subdir)
        # Without --new and --add options, only display files from `args.files`.
        # With --new or --add options, all files will be displayed.
        if not args.new and not args.add:
            ls_args += args.files
        p = ext.run(ls_args, encoding='utf-8')
        exit(p.returncode)
