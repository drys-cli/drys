from setuptools import setup

import drys

setup(
    name="drys",
    version=drys.__version__,
    description="Don't Repeat Yourself. Seriously.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/harisgusic/drys',
    author='Haris Gušić',
    author_email='harisgusic.dev@gmail.com',
    classifiers=[
        'Programming Language :: Python :: 3.9'
    ],
    packages=['drys'],
    entry_points={
        'console_scripts': [
            'drys=drys.__main__:main'
        ]
    },
)
