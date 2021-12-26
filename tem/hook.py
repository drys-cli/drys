import enum
from typing import Callable
from tem.env import Environment

PRE = 0x01   #: Type of hook that runs before a subcommand
POST = 0x02  #: Type of hook that runs after a subcommand

def hook(subcommand: str="*", when: int=PRE):
    """Decorator: hook for ``subcommand`` that is called ``when``...

    Parameters
    ----------
    subcommand: optional
        Subcommand for which this hook should run.
    when: {PRE, POST, PRE & POST}, optional
        Whether the hook should run before (PRE) or after (POST) the subcommand,
        or both.
    """
    def decorator(func):
        register_hook(func, subcommand, when)
        return func
    return decorator


def run_hooks(env: Environment, subcommand: str, type: {PRE, POST, PRE & POST}):
    """Run hooks from the given environment."""
    for envdir in env.envdirs:
        envdir.exec()


def register_hook(hook: Callable, subcommand: str="*", when: int=PRE):
    """Register a pythonic hook. This is in contrast to an executable hook."""
    _registered_hooks[when][subcommand] = hook


class _HookDict(dict):
    def __getitem__(self, key):
        if key not in self:
            self[key] = {PRE: [], POST: []}
        return super().__getitem__(key)


_registered_hooks = _HookDict()
