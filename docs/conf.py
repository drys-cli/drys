import glob
import os
import sys

from sphinx.application import Sphinx
from sphinx.domains import std

# ┏━━━━━━━━━━━━━━┓
# ┃ Project info ┃
# ┗━━━━━━━━━━━━━━┛
project = "tem"
copyright = "2021, Haris Gušić"
author = "Haris Gušić"

sys.path.insert(0, os.path.dirname(__file__) + "/..")
import tem

release = tem.__version__

# ┏━━━━━━━━━━━━━━━━━━━━━━━┓
# ┃ General configuration ┃
# ┗━━━━━━━━━━━━━━━━━━━━━━━┛
extensions = [
    "sphinx.ext.todo",
    "sphinx.ext.autodoc",
    "sphinx_codeautolink",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
    "sphinx_rtd_dark_mode",
    "sphinx_copybutton",
    "sphinx-prompt",
    "sphinx_toolbox.source",
    "sphinx_toolbox.collapse",
    "sphinx_tabs.tabs",
    "hoverxref.extension",
]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "man"]
todo_include_todos = True

default_role = "envvar"  # Like :code: role, but the text is black
if os.environ.get("READTHEDOCS"):
    rtd_project = os.environ.get("READTHEDOCS_PROJECT")
    rtd_lang = os.environ.get("READTHEDOCS_LANGUAGE")
    rtd_version = os.environ.get("READTHEDOCS_VERSION")
    manpages_url = "https://{rtd_project}.readthedocs.io/{rtd_lang}/{rtd_version}/man/"
else:
    manpages_url = f"file://{os.path.dirname(__file__)}/_build/html/_intermediate/man/{{page}}.html"

sys.path.insert(0, os.path.abspath(".."))
# ┏━━━━━━┓
# ┃ HTML ┃
# ┗━━━━━━┛
html_theme = "sphinx_rtd_theme"
default_dark_mode = False
html_static_path = ["_static"]
html_css_files = [
    "custom.css",
]
# Tweak manpages for inclusion in the HTML version of the docs
if "html" in sys.argv:
    from subprocess import call

    call(["make", "prepare-man"])

# Generate substitutions for manual page descriptions
sys.path.insert(1, "man")
from man_descriptions import *

try:
    rst_prolog  # Variable exists?
except NameError:
    rst_prolog = ""  # No: create it as an empty string
rst_prolog = generate_description_substitutions(rst_prolog)

# ┏━━━━━━━━━━━━┓
# ┃ Python doc ┃
# ┗━━━━━━━━━━━━┛
autodoc_member_order = "bysource"
autodoc_typehints = "description"
autodoc_typehints_description_target = "documented_params"
autodoc_typehints_format = "short"
add_module_names = False
add_function_parentheses = False
autosummary_generate = True
python_use_unqualified_type_hints = True
napoleon_custom_sections = [
    "Constants",
    "Attributes",
    "Returns",
    "Methods",
    "Indexing and lookup",
]

# ┏━━━━━━━━━━━━━━━━┓
# ┃ Sphinx toolbox ┃
# ┗━━━━━━━━━━━━━━━━┛
github_username = "tem-cli"
github_repository = "tem"
source_link_target = "GitHub"

# ┏━━━━━━━━━━━┓
# ┃ Hoverxref ┃
# ┗━━━━━━━━━━━┛
hoverxref_auto_ref = True
hoverxref_sphinxtabs = True
hoverxref_modal_hover_delay = 0
hoverxref_tooltip_animation_duration = 250

# ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
# ┃ Specific steps for ReadTheDocs ┃
# ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

# ReadTheDocs doesn't use make -- it builds directly using sphinx and this file
if os.environ.get("READTHEDOCS", False):
    from subprocess import call

    # Scripts must be made executable on ReadTheDocs, but we just give full
    # permissions to all files to prevent future headaches
    call("chmod -R 777 ./", shell=True)
    call("umask 000", shell=True)

    # Add a tag so we can customize some rst files for ReadTheDocs
    tags.add("ReadTheDocs")
    # Confer [*]
    exclude_patterns.remove("man")

    # Move them to man/ so the resulting URL looks nicer [*]
    call("mv _intermediate/man/* man/", shell=True)

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

# ┏━━━━━━━━━━━━━━━━━━┓
# ┃ Hacks and tricks ┃
# ┗━━━━━━━━━━━━━━━━━━┛

# Remove first two lines of docstring for `tem.var`
def remove_module_docstring(app, what, name, obj, options, lines):
    if what == "module" and name == "tem.var":
        del lines[0]


# TODO override so as to provide a way to automatically add :term: to all
# occurrences of glossary words
class GlossaryDirective(std.Glossary):
    def run(self):
        super().run()


def setup(app: Sphinx):
    app.connect("autodoc-process-docstring", remove_module_docstring)
    app.connect("source-read", on_source_read)
    app.add_directive("glossary", GlossaryDirective, override=True)


def on_source_read(app, docname, source):
    # TODO
    pass
