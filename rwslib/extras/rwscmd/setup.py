# -*- coding: utf-8 -*-
__author__ = 'anewbigging'

from setuptools import setup

setup(
    name='rwscmd',
    version='0.1',
    author = "Andrew Newbigging",
    author_email = "anewbigging@mdsol.com",
    description = "Command line utility for Rave Web Services",
    py_modules=['rwscmd', 'odmutils', 'data_scrambler'],
    install_requires=[
        'Click', 'rwslib', 'requests', 'lxml', 'fake-factory'
    ],
    entry_points='''
        [console_scripts]
        rwscmd=rwscmd:rws
    ''',
)