# Copyright (C) iNuron - info@openvstorage.com
# This file is part of Open vStorage. For license information, see <LICENSE.txt>

"""
Base error module
"""


class ArakoonError(Exception):
    """
    Base type for all Arakoon client errors
    """
    # Error code sent by the Arakoon server
    CODE = None


class UnknownFailure(ArakoonError):
    """
    Unknown failure
    """
    CODE = 0x00ff
