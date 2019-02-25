# This file is part of Pyrakoon, a distributed key-value store client.
#
# Copyright (C) 2010 Incubaid BVBA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Arakoon protocol implementation
"""

import inspect

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

# Backward compatibility
from .communication import Result, Request, RESULT_SUCCESS, PROTOCOL_VERSION
from .types import Type, String, UnsignedInteger, SignedInteger, Float, Bool, Unit, Step, Option, List, Array, Product,\
    NamedField, StatisticsType, Consistency,\
    STRING, UINT32, UINT64, INT8, INT32, INT64, FLOAT, BOOL, UNIT, STEP, STATISTICS, CONSISTENCY, CONSISTENCY_ARG
from .messages import Message,\
    Get, Set, Delete, TestAndSet, Sequence, Confirm, DeletePrefix, Replace,\
    Exists, Assert, AssertExists,\
    Hello, WhoMaster, ExpectProgressPossible, Statistics, Version, Nop, GetCurrentState, UserFunction, GetKeyCount, GetTxID


def sanity_check():
    """
    Sanity check for some invariants on types defined in this module
    """

    for (_name, value) in globals().iteritems():
        if inspect.isclass(value) and getattr(value, '__module__', None) == __name__:
            # A `Message` which has `CONSISTENCY_ARG` in its `ARGS` must have
            # an `consistency` attribute, the constructor must take such
            # argument, and if `__slots__` is defined, there should be an
            # `_consistency` field
            if issubclass(value, Message):
                if CONSISTENCY_ARG in (value.ARGS or []):
                    assert hasattr(value, 'consistency')
                    argspec = inspect.getargspec(value.__init__)
                    assert 'consistency' in argspec.args
                    if hasattr(value, '__slots__'):
                        assert '_consistency' in value.__slots__


# @todo fix sanity check with new folder structure
sanity_check()
del sanity_check


def build_prologue(cluster):
    # type: (str) -> str
    """
    Return the string to send as prologue
    :param cluster: Name of the cluster to which a connection is made
    :type cluster: str
    :return: Prologue to send to the Arakoon server
    :rtype: str
    """

    return ''.join((UINT32.serialize(Message.MASK), UINT32.serialize(PROTOCOL_VERSION), STRING.serialize(cluster)))
