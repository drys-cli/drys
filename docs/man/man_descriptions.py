#!/usr/bin/env python3

man_descriptions = {
    "tem": "Template and Environment Manager",
    "tem-add": "Add templates to a tem repository",
    "tem-rm": "Remove templates from a tem repository",
    "tem-put": "Copy a template to a destination",
    "tem-ls": "List templates",
    "tem-repo": "Perform operations on tem repositories",
    "tem-config": "Configure tem",
    "tem-init": "Generate a .tem directory",
    "tem-env": "Run or modify local environments",
    "tem-git": "Manage environments versioned under git",
    "tem-hook": "Various manipulations with tem hooks",
    "tem-tutorial": "Tutorial for new users of tem",
}


def generate_description_substitutions(rst_prolog):
    """
    Add to `rst_prolog` lines defining substitutions named man_desc_* containing
    the description for each manual page defined in `man_descriptions`. E.g. the
    manual page for tem-add gets a substitution man_desc_tem_add. Returns the
    modified `rst_prolog`.
    """
    for entry in man_descriptions.items():
        rst_prolog += ".. |man_desc_{}| replace:: {}\n".format(
            entry[0].replace("-", "_"), entry[1]
        )
    return rst_prolog


if __name__ == "__main__":
    import sys

    print(man_descriptions[sys.argv[1]])
