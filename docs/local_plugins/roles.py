from docutils import nodes
from docutils.parsers.rst.states import Inliner
from sphinx.addnodes import manpage
from sphinx.util import split_explicit_title


# TOD
def command_role(
    name,
    rawtext,
    text: str,
    lineno,
    inliner: Inliner,
    options=None,
    content=None,
):
    # has_title, title, target = split_explicit_title(text)
    # title = nodes.unescape(title)
    return [manpage], []
