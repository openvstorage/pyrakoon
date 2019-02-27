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

from __future__ import absolute_import

from .base import Message
from .crud import Get, Set, Delete, TestAndSet, Sequence, Confirm, DeletePrefix, Replace
from .testing import Exists, Assert, AssertExists
from .misc import Hello, WhoMaster, ExpectProgressPossible, Statistics, Version, Nop, GetCurrentState, UserFunction, GetKeyCount, GetTxID
from .query import PrefixKeys, MultiGet, MultiGetOption, RevRangeEntries, Range, RangeEntries
