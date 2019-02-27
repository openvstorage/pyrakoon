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
