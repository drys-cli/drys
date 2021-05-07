import glob, sys, os

man_pages = []

# Provides function get_description to load command descriptions for man pages
sys.path.insert(0, os.path.dirname(__file__))
from man_descriptions import man_descriptions

for f in glob.glob('tem*.rst'):
    man_pages.append((
        f[:-4],                         # source file (extension .rst removed)
        f[:-4],                         # output file (under output dir)
        man_descriptions[f[:-4]],       # description
        'Haris Gušić <harisgusic.dev@gmail.com>',   # author
        1,                                          # section
    ))

