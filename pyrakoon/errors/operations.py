# Copyright (C) 2019 iNuron NV
#
# This file is part of Open vStorage Open Source Edition (OSE),
# as available from
#
#      http://www.openvstorage.org and
#      http://www.openvstorage.com.
#
# This file is free software; you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License v3 (GNU AGPLv3)
# as published by the Free Software Foundation, in version 3 as it comes
# in the LICENSE.txt file of the Open vStorage OSE distribution.
#
# Open vStorage is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY of any kind.

"""
Operations error module
Contains errors that can be thrown during operations
"""

from __future__ import absolute_import

from .base import ArakoonError


class NoMagic(ArakoonError):
    """
    Server received a command without the magic mask
    """
    CODE = 0x0001


class NotFound(KeyError, ArakoonError):
    """
    Key not found
    """
    CODE = 0x0005


class AssertionFailed(ArakoonError):
    """
    Assertion failed
    """
    CODE = 0x0007


class ReadOnly(ArakoonError):
    """
    Node is read-only
    """
    CODE = 0x0008


class OutsideInterval(ValueError, ArakoonError):
    """
    Request outside interval handled by node
    """
    CODE = 0x0009


class NotSupported(ArakoonError):
    """
    Unsupported operation
    """
    CODE = 0x0020


class BadInput(ArakoonError):
    """
    Bad input
    """
    CODE = 0x0026


class InconsistentRead(ArakoonError):
    """
    Inconsistent read
    """
    CODE = 0x0080
