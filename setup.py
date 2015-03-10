#!/usr/bin/env python

import os
import sys

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
    version='1.0.2',
    description='Rave web services for Python',
    long_description=open('README.md').read(),
    author='Ian Sparks',
    author_email='isparks@mdsol.com',
    packages=packages,
    package_dir={'rwslib': 'rwslib'},
    include_package_data=True,
    install_requires=['requests','lxml','httpretty'],
    license=open('LICENSE.txt').read(),
    zip_safe=False,
    test_suite='rwslib.tests.all_tests',
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ),
)
