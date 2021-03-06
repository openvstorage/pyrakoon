#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) iNuron - info@openvstorage.com
# This file is part of Open vStorage. For license information, see <LICENSE.txt>

import io
import os
import re
from subprocess import check_output
from setuptools import find_packages, setup
from setuptools.command.install import install


class Container(object):
    """
    Houses some variables
    """
    def __init__(self):
        self.commit_hash = None
        self.init_pys = {}


class PyrakoonInstall(install):
    def run(self):
        # Setup the hash
        set_hash(PACKAGE_NAME)
        # Run the setuptools install
        install.run(self)


CONTAINER = Container()
HASH_REGEX = "(__hash__ = .*['\"])(.*)(['\"])"


def read_init(package):
    init_py = CONTAINER.init_pys.get(package)
    if init_py is not None:
        return init_py
    with open(os.path.join(package, '__init__.py'), 'r') as init_file:
        file_contents = init_file.read()
        CONTAINER.init_pys[package] = file_contents
        return file_contents


def get_hash(package):
    """
    Retrieve the hash of the package
    """
    _ = package
    try:
        CONTAINER.commit_hash = check_output(['git', 'rev-parse', 'HEAD']).strip()
    except:
        CONTAINER.commit_hash = ''
        print 'Unable to get the hash'
    return CONTAINER.commit_hash


def set_hash(package):
    """
    Write the hash out the __hash__.py. Done during setup
    """
    package_hash = get_hash(package)
    if package_hash is not None:
        try:
            hash_file_path = os.path.join(package, '__hash__.py')
            with open(hash_file_path, 'r') as hash_f:
                contents = hash_f.read()
            new_contents = re.sub(HASH_REGEX, '\g<1>{}\g<3>'.format(package_hash), contents)
            with open(hash_file_path, 'w') as hash_f:
                hash_f.write(new_contents)
            print 'Written out the hash to __hash__.py'
        except:
            print 'Unable to write the hash'


def get_version(package):
    """
    Return package version as listed in `__version__.py`
    """
    with open(os.path.join(package, '__version__.py'), 'r') as version_f:
        contents = version_f.read()
    with open(os.path.join(package, '__hash__.py'), 'r') as hash_f:
        hash_contents = hash_f.read()
    # Unable to use __version__ as it is computed. Compute it again
    version_numbers = re.search("__version_info__ = ([0-9]+(?:, ?[0-9]+)*)", contents).group(1)
    hash_content = re.search(HASH_REGEX, hash_contents).group(2)
    if hash_content == 'None':
        hash_content = str(get_hash(package))
    return '{0}+{1}'.format('.'.join(n.strip() for n in version_numbers.split(',')), hash_content)


def get_author(package):
    """
    Return package author as listed in `__author__.py`
    """
    with open(os.path.join(package, '__author__.py'), 'r') as author_f:
        contents = author_f.read()
    return re.search("__author__ = .*['\"](.*)['\"]", contents).group(1)


def get_license(package):
    """
    Return package license as listed in `__license__.py`
    """
    with open(os.path.join(package, '__license__.py'), 'r') as license_f:
        contents = license_f.read()
    return re.search("__license__ = .*['\"](.*)['\"]", contents).group(1)


# Package meta-data.
PACKAGE_NAME = 'pyrakoon'
NAME = 'Pyrakoon'
DESCRIPTION = 'An alternative Python client for Arakoon'
URL = 'https://github.com/openvstorage/pyrakoon'
EMAIL = 'support@openvstorage.com'
AUTHOR = get_author(PACKAGE_NAME)
REQUIRES_PYTHON = '>=2.7, <3.0'
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
    cmdclass={
        'install': PyrakoonInstall,
    },
)
