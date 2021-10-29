import os

from tem import util


def active_variants() -> list[str]:
    return _read_variants()


def activate(variants: list[str]):
    _write_variants(util.unique(active_variants() + variants))


def deactivate(variants: list[str]):
    new = [var for var in active_variants() if var not in variants]
    _write_variants(new)


def set_active_variants(variants: list[str]):
    _write_variants(util.unique(variants))


def _read_variants() -> list[str]:
    """Read the active variants for the current."""
    if not os.path.exists(".tem/.internal/variants"):
        return []
    with open(".tem/.internal/variants", encoding="utf-8") as f:
        return f.read().split("\n")


def _write_variants(variants: list[str]):
    if not os.path.exists(".tem/.internal"):
        os.mkdir(".tem/.internal")
    with open(".tem/.internal/variants", "w", encoding="utf-8") as f:
        f.write("\n".join(variants))
