#!/usr/bin/env python3

man_descriptions = {
    'tem': 'Template and Environment Manager',
    }

if __name__ == '__main__':
    import sys
    print(man_descriptions[sys.argv[1]])
