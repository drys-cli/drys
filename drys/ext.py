
def call(command):
    """
    Call an external command with the specified arguments, honoring the user's
    command overrides.
    """
    import subprocess
    # TODO for now, just call the default command
    subprocess.call(command)
