# Copyright (C) iNuron - info@openvstorage.com
# This file is part of Open vStorage. For license information, see <LICENSE.txt>

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
