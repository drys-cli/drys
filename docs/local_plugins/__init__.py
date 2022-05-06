from sphinx.application import Sphinx
from .roles import command_role


def setup(app: Sphinx):
    pass
    # TODO app.add_role("command", command_role, override=True)
