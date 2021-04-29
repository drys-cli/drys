#!/usr/bin/env python3

import drys

import argparse, sys
from drys import common
# drys rm <file> --wipe
# drys cd <file|dir>
# drys where <file|dir>
# drys link <target file|dir> <symlink>     # alias ln

def main():
    argv = sys.argv

    parser = argparse.ArgumentParser()

    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s version TODO')
    common.add_common_options(parser, main_parser=True)
    parser.add_argument('--debug', action='store_true',
                        help='start python debugger')
    parser.set_defaults(func=None)

    # Setup subcommand parsers
    sub = parser.add_subparsers(title='commands', metavar='')
    from drys import add
    from drys import put
    from drys import ls
    from drys import repo
    from drys import config
    add.setup_parser(sub)
    put.setup_parser(sub)
    ls.setup_parser(sub)
    repo.setup_parser(sub)
    config.setup_parser(sub)

    # TODO figure out how to handle config loading to use aliases
    # Parse arguments before reading config. This allows us to process arguments
    # that can potentially terminate the program immediately (like '--help')
    args = parser.parse_args();

    if args.debug:
        import pudb; pu.db


    config = args._config if args.func else []
    if args.config: config += args.config
    # ┏━━━━━━┓
    # ┃ NOTE ┃
    # ┗━━━━━━┛
    # Because the --config option is part of both the main parser and all the
    # subparsers, whenever a command is specified, the contents of args.config
    # are reset. So, args.config contains only those occurrences that are
    # specified AFTER a subcommand.
    # For example after running: drys -c file1 ls -c file2 -c file3
    #   args.config will be [ 'file2', 'file3' ]
    #
    # This is a workaround I intend to remove once I figure out a proper way
    # around it
    if not args.config:
        for i in range(1, len(sys.argv)):
            if sys.argv[i] and sys.argv[i][0] != '-':
                break
            if sys.argv[i] in ['--config', '-c'] and i+1 < len(sys.argv):
                config += [ sys.argv[i+1] ]

    # Load configuration, both default and from arguments
    common.load_config(config)

    if args.func:
        args.func(parser, args)

if __name__ == '__main__':
    main()
