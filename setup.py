#!/usr/bin/env python

import os
import sys
import re

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == "publish":
    os.system("python setup.py sdist upload")
    sys.exit()

packages = [
    "rwslib",
    "rwslib.rws_requests",
    "rwslib.builders",
    "rwslib.extras",
    "rwslib.extras.audit_event",
    "rwslib.extras.rwscmd",
]

rwsinit = open("rwslib/__init__.py").read()
author = re.search(r"__author__ = \"([^\"]+)\"", rwsinit).group(1)
version = re.search(r"__version__ = \"([^\"]+)\"", rwsinit).group(1)

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="rwslib",
    version=version,
    description="Rave web services for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=author,
    author_email="isparks@mdsol.com",
    packages=packages,
    package_dir={"rwslib": "rwslib"},
    include_package_data=True,
    install_requires=['requests',
                      'lxml',
                      'six',
                      'click',
                      'faker',
                      "enum34; python_version < '3.4'",
                      ],
    tests_require=['mock', 'httpretty'],
    license="MIT License",
    url='https://github.com/mdsol/rwslib/',
    zip_safe=False,
    test_suite='rwslib.tests.all_tests',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    entry_points="""
    [console_scripts]
    rwscmd=rwslib.extras.rwscmd.rwscmd:rws
    """,
)
