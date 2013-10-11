#!/usr/bin/env python

import os
import sys

import rwslib

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

packages = [
    'rwslib',
    'rwslib.rws_requests',
]


setup(
    name='rwslib',
    version=rwslib.__version__,
    description='Rave web services for Python',
    long_description=open('README.md').read(),
    author='Ian Sparks',
    author_email='isparks@mdsol.com',
    packages=packages,
    package_data={'': ['LICENSE.txt'],},
    package_dir={'rwslib': 'rwslib'},
    include_package_data=True,
    install_requires=['requests','lxml','httpretty'],
    license=open('LICENSE.txt').read(),
    zip_safe=False,
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ),
)
