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
exclude_patterns    = ['_build', 'Thumbs.db', '.DS_Store', 'man']
todo_include_todos  = True

smartquotes = False     # Always display '--' verbatim
default_role = 'envvar' # Like :code: role, but the text is black
# ┏━━━━━━┓
# ┃ HTML ┃
# ┗━━━━━━┛
html_theme = 'sphinx_rtd_theme'
# Tweak manpages for inclusion in the HTML version of the docs
if 'html' in sys.argv:
    from subprocess import call
    call(['make', 'prepare-man'])

# ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
# ┃ Specific steps for ReadTheDocs ┃
# ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

# ReadTheDocs doesn't use make -- it builds directly using sphinx and this file
if os.environ.get('READTHEDOCS', False):
    from subprocess import call

    # Scripts must be made executable on ReadTheDocs, but we just give full
    # permissions to all files to prevent future headaches
    call('chmod -R 777 ./', shell=True)
    call('umask 000', shell=True)

    # Add a tag so we can customize some rst files for ReadTheDocs
    tags.add('ReadTheDocs')
    # Confer [*]
    exclude_patterns.remove('man')

    # Move them to man/ so the resulting URL looks nicer [*]
    call('mv _intermediate/man/* man/', shell=True)

    # ┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓
    # ┃ Debugging on ReadTheDocs ┃
    # ┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛

    # Only uncomment this section if something is going wrong on ReadTheDocs

    """
    # In the Sphinx documentation, this function is said to require three arguments.
    # But when the third one is positional, an exception is raised.
    # We don't use it anyway, so set its default value to None.
    def build_finished_handler(app, docname, source=None):
        # Check if the correct files have been generated
        call('ls -Rl', shell=True)

    def setup(app):
        app.connect('build-finished', build_finished_handler)
    """

