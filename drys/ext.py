import subprocess
from .common import config

def run(command, *args, **kwargs):
    """
    Call an external command with the specified arguments, honoring the user's
    command overrides.
    """
    return subprocess.run(config[command], *args, **kwargs)
