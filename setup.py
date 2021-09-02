from setuptools import setup

import tem

setup(
    name="tem",
    version=tem.__version__,
    description="Don't Repeat Yourself. Ever. Again",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/tem-cli/tem",
    author="Haris Gušić",
    author_email="harisgusic.dev@gmail.com",
    classifiers=["Programming Language :: Python :: 3.9"],
    packages=["tem", "tem.cli"],
    entry_points={"console_scripts": ["tem=tem.__main__:main"]},
)
