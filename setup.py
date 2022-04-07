from setuptools import setup, find_packages

import os
import sys
import tem


setup(
    name="tem",
    version=os.environ.get("VERSION", "0.0.0"),
    description="Don't Repeat Yourself. Ever. Again",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/tem-cli/tem",
    author="Haris Gušić",
    author_email="harisgusic.dev@gmail.com",
    classifiers=["Programming Language :: Python :: 3.9"],
    packages=find_packages(),
    entry_points={"console_scripts": ["tem=tem.__main__:main"]},
)
