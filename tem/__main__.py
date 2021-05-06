#!/usr/bin/env python3

import tem

import argparse, sys, os
from tem import common
# tem where <file|dir>
# tem link <target file|dir> <symlink>     # alias ln

def init_config():
    existent_cfg = [path for path in common.user_config_paths
                if os.path.exists(path)]
    if existent_cfg:
        # User config file already exists
        print('tem: error: configuration already exists at '
              + existent_cfg[0], file=sys.stderr)
        exit(1)
    else:
        common.copy(tem.__prefix__ + '/share/tem/config',
                    common.get_user_config_path())
        exit(0)

def main():
    argv = sys.argv

    parser = argparse.ArgumentParser()

    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s version TODO')
    common.add_common_options(parser, main_parser=True)
    parser.add_argument('--init-config', action='store_true',
                        help='generate initial user configuration file')
    parser.add_argument('--debug', action='store_true',
                        help='start in debugger mode')
    parser.set_defaults(func=None)

    # Setup subcommand parsers
    sub = parser.add_subparsers(title='commands', metavar='')
    from tem import add
    from tem import rm
    from tem import put
    from tem import ls
    from tem import repo
    from tem import config
    add.setup_parser(sub)
    rm.setup_parser(sub)
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

    if args.init_config:
        init_config()

    # ┏━━━━━━┓
    # ┃ NOTE ┃
    # ┗━━━━━━┛
    # Because the --config option is part of both the main parser and all the
    # subparsers, whenever a command is specified, the contents of args.config
    # are reset. So, args.config contains only those occurrences that are
    # specified AFTER a subcommand.
    # For example after running: tem -c file1 ls -c file2 -c file3
    #   args.config will be [ 'file2', 'file3' ]
    #
    # This is a workaround I intend to remove once I figure out a proper way
    # around it
    config = []
    for i in range(1, len(sys.argv)):
        if sys.argv[i] in ['--config', '-c'] and i < len(sys.argv) - 1:
            config.append(sys.argv[i+1])

    # Load configuration, both default and from arguments
    common.load_config(config)

    if args.func:
        args.func(parser, args)

if __name__ == '__main__':
    main()
