import os
import argparse

repos = [ os.path.expanduser('~/.local/share/drys/repo') ]

def add_common_options(parser):
    parser.add_argument('-c', '--config', metavar='FILE', help='Use the specified configuration file')

def existing_file(path):
    if not os.path.exists(path):
        raise argparse.ArgumentTypeError(path + ' does not exist')
    else:
        return path

