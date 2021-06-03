#!/usr/bin/env python3

man_descriptions = {
    'tem': 'Template and Environment Manager',
    'tem-add': 'Add a file as a template',
    'tem-put': 'Copy a template to a destination',
    'tem-hook': 'Various manipulations with tem hooks',
    'tem-config': 'tem configuration file specification',
    'tem-tutorial': 'tutorial for new users of tem',
    }

if __name__ == '__main__':
    import sys
    print(man_descriptions[sys.argv[1]])
