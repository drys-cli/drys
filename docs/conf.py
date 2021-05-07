import glob, sys, os

# ┏━━━━━━━━━━━━━━┓
# ┃ Project info ┃
# ┗━━━━━━━━━━━━━━┛
project = 'tem'
copyright = '2021, Haris Gušić'
author = 'Haris Gušić'

sys.path.insert(0, os.path.dirname(__file__) + '/..')
import tem
release = tem.__version__

# ┏━━━━━━━━━━━━━━━━━━━━━━━┓
# ┃ General configuration ┃
# ┗━━━━━━━━━━━━━━━━━━━━━━━┛
extensions = [
    'sphinx.ext.todo'
]
exclude_patterns    = ['_build', 'Thumbs.db', '.DS_Store']
todo_include_todos  = True

smartquotes = False     # Always display '--' verbatim
default_role = 'envvar' # Like :code: role, but the text is black

# ┏━━━━━━┓
# ┃ HTML ┃
# ┗━━━━━━┛
html_theme = 'sphinx_rtd_theme'

# ┏━━━━━━━━━━━┓
# ┃ Man pages ┃
# ┗━━━━━━━━━━━┛
man_pages = []

# Provides function get_description to load command descriptions for man pages
sys.path.insert(0, os.path.dirname(__file__))
from man_descriptions import man_descriptions

for f in glob.glob('tem*.rst'):
    man_pages.append((
        f[:-4], # source file (extension .rst removed)
        f[:-4], # output file (under output dir)
        man_descriptions[f[:-4]], # description
        'Haris Gušić <harisgusic.dev@gmail.com>', # author
        1, # section
    ))
