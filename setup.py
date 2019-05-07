#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os
import re
from setuptools import find_packages, setup

init_pys = {}


def read_init(package):
    init_py = init_pys.get(package)
    if init_py is not None:
        return init_py
    with open(os.path.join(package, '__init__.py'), 'r') as init_file:
        file_contents = init_file.read()
        init_pys[package] = file_contents
        return file_contents


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = read_init(package)
    # Unable to use __version__ as it is computed. Compute it again
    version_numbers = re.search("__version_info__ = ([0-9]+(?:, ?[0-9]+)*)", init_py).group(1)
    return '.'.join(n.strip() for n in version_numbers.split(','))


def get_author(package):
    """
    Return package author as listed in `__author__` in `init.py`.
    """
    init_py = read_init(package)
    return re.search("__author__ = .*['\"](.*)['\"]", init_py).group(1)


def get_license(package):
    """
    Return package license as listed in `__license` in `init.py`.
    """
    init_py = read_init(package)
    return re.search("__license__ = .*['\"](.*)['\"]", init_py).group(1)


# Package meta-data.
PACKAGE_NAME = 'pyrakoon'
NAME = 'Pyrakoon'
DESCRIPTION = 'An alternative Python client for Arakoon'
URL = 'https://github.com/openvstorage/pyrakoon'
EMAIL = 'support@openvstorage.com'
AUTHOR = get_author(PACKAGE_NAME)
REQUIRES_PYTHON = '>=2.7.0,<=3.0'
VERSION = get_version(PACKAGE_NAME)
LICENSE = get_license(PACKAGE_NAME)

# Packages
REQUIRED = []
EXTRAS = {}

# Import the README and use it as the long-description.
try:
    with io.open('README.MD', encoding='utf-8') as f:
        long_description = '\n' + f.read()
except IOError:
    long_description = DESCRIPTION

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=('test', 'demo')),
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    license=LICENSE,
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
)
