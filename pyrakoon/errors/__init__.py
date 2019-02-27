# Copyright (C) iNuron - info@openvstorage.com
# This file is part of Open vStorage. For license information, see <LICENSE.txt>

"""
Errors module
Contains all errors that can be raised by the Arakoon client
"""

from __future__ import absolute_import

import inspect

from .base import ArakoonError, UnknownFailure
from .connection import NoHello, NotMaster, WrongCluster, GoingDown, NoLongerMaster, MaxConnections, TooManyDeadNodes
from .operations import NoMagic, NotFound, AssertionFailed, ReadOnly, OutsideInterval, NotSupported, BadInput, InconsistentRead

# Map of Arakoon error codes to exception types
ERROR_MAP = dict((value.CODE, value) for value in globals().itervalues()
                 if inspect.isclass(value) and issubclass(value, ArakoonError)
                 and value.CODE is not None)
