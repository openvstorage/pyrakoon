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
Crud message module
Contains messages to perform CRUD operations
"""

from __future__ import absolute_import

from ... import utils
from .base import Message, KeyMessage, KeyConsistencyMessage, KeyValueMessage
from ..types import Option, List, STRING, UINT32, BOOL, UNIT, STEP


class Get(KeyConsistencyMessage):
    """
    "get" message
    """

    __slots__ = ()

    TAG = 0x0008 | Message.MASK
    RETURN_TYPE = STRING

    DOC = utils.format_doc('''
        Send a "get" command to the server

        This method returns the value of the requested key.

        :param key: Key to retrieve
        :type key: :class:`str`
        :param consistency: Allow reads from stale nodes
        :type consistency: :class:`pyrakoon.consistency.Consistency`

        :return: Value for the given key
        :rtype: :class:`str`
    ''')

    def __init__(self, consistency, key):
        super(Get, self).__init__(consistency, key)


class Set(KeyValueMessage):
    """
    "set" message
    """
    __slots__ = ()

    TAG = 0x0009 | Message.MASK
    RETURN_TYPE = UNIT

    DOC = utils.format_doc('''
        Send a "set" command to the server

        This method sets a given key to a given value on the server.

        :param key: Key to set
        :type key: :class:`str`
        :param value: Value to set
        :type value: :class:`str`
    ''')

    def __init__(self, key, value):
        super(Set, self).__init__(key, value)


class Delete(KeyMessage):
    """
    "delete" message
    """

    __slots__ = ()

    TAG = 0x000a | Message.MASK
    RETURN_TYPE = UNIT

    DOC = utils.format_doc('''
        Send a "delete" command to the server

        This method deletes a given key from the cluster.

        :param key: Key to delete
        :type key: :class:`str`
    ''')


class TestAndSet(KeyMessage):
    """
    "test_and_set" message
    """

    __slots__ = ('_test_value', '_set_value')

    TAG = 0x000d | Message.MASK
    ARGS = (('key', STRING), ('test_value', Option(STRING)), ('set_value', Option(STRING)))
    RETURN_TYPE = Option(STRING)

    DOC = utils.format_doc('''
        Send a "test_and_set" command to the server

        When `test_value` is not :data:`None`, the value for `key` will only be
        modified if the existing value on the server is equal to `test_value`.
        When `test_value` is :data:`None`, the `key` will only be set of there
        was no value set for the `key` before.

        When `set_value` is :data:`None`, the `key` will be deleted on the server.

        The original value for `key` is returned.

        :param key: Key to act on
        :type key: :class:`str`
        :param test_value: Expected value to test for
        :type test_value: :class:`str` or :data:`None`
        :param set_value: New value to set
        :type set_value: :class:`str` or :data:`None`

        :return: Original value of `key`
        :rtype: :class:`str`
    ''')

    def __init__(self, key, test_value, set_value):
        super(TestAndSet, self).__init__(key)

        self._test_value = test_value
        self._set_value = set_value

    @property
    def test_value(self):
        return self._test_value

    @property
    def set_value(self):
        return self._set_value


class Sequence(Message):
    """
    "sequence" and "synced_sequence" message
    """

    __slots__ = '_steps', '_sync',

    ARGS = (('steps', List(STEP)), ('sync', BOOL, False))
    RETURN_TYPE = UNIT

    DOC = utils.format_doc('''
        Send a "sequence" or "synced_sequence" command to the server

        The operations passed to the constructor should be instances of
        implementations of the :class:`pyrakoon.sequence.Step` class. These
        operations will be executed in an all-or-nothing transaction.

        :param steps: Steps to execute
        :type steps: iterable of :class:`pyrakoon.sequence.Step`
        :param sync: Use *synced_sequence*
        :type sync: :class:`bool`
    ''')

    def __init__(self, steps, sync):
        from pyrakoon import sequence

        super(Sequence, self).__init__()

        if len(steps) == 1 and isinstance(steps[0], sequence.Sequence):
            self._sequence = steps[0]
        else:
            self._sequence = sequence.Sequence(steps)

        self._sync = sync

    @property
    def sequence(self):
        return self._sequence

    @property
    def sync(self):
        return self._sync

    def serialize(self):
        tag = (0x0010 if not self.sync else 0x0024) | Message.MASK

        for bytes_ in UINT32.serialize(tag):
            yield bytes_

        sequence_bytes = ''.join(self.sequence.serialize())

        for bytes_ in STRING.serialize(sequence_bytes):
            yield bytes_


class Confirm(KeyValueMessage):
    """
    "confirm" message
    """

    __slots__ = ()

    TAG = 0x001c | Message.MASK
    RETURN_TYPE = UNIT

    DOC = utils.format_doc('''
        Send a "confirm" command to the server

        This method sets a given key to a given value on the server, unless
        the value bound to the key is already equal to the provided value, in
        which case the action becomes a no-op.

        :param key: Key to set
        :type key: :class:`str`
        :param value: Value to set
        :type value: :class:`str`
    ''')

    def __init__(self, key, value):
        super(Confirm, self).__init__(key, value)


class DeletePrefix(Message):
    """
    "delete_prefix" message
    """

    __slots__ = ('_prefix',)

    TAG = 0x0027 | Message.MASK
    ARGS = (('prefix', STRING),)
    RETURN_TYPE = UINT32

    DOC = utils.format_doc('''
        Send a "delete_prefix" command to the server

        `delete_prefix prefix` will delete all key/value-pairs from the
        database where given `prefix` is a prefix of `key`.

        :param prefix: Prefix of binding keys to delete
        :type prefix: :class:`str`
        :return: Number of deleted bindings
        :rtype: :class:`int`
    ''')

    def __init__(self, prefix):
        super(DeletePrefix, self).__init__()

        self._prefix = prefix

    @property
    def prefix(self):
        return self._prefix


class Replace(KeyValueMessage):
    """
    "replace" message
    """

    __slots__ = ()

    TAG = 0x0033 | Message.MASK
    ARGS = (('key', STRING), ('value', Option(STRING)))
    RETURN_TYPE = Option(STRING)

    DOC = utils.format_doc('''
        Send a "replace" command to the server

        `replace key value` will replace the value bound to the given key with
        the provided value, and return the old value bound to the key.
        If `value` is :data:`None`, the key is deleted.
        If the key was not present in the database, :data:`None` is returned.

        :param key: Key to replace
        :type key: :class:`str`
        :param value: Value to set
        :type value: :class:`str` or :data:`None`

        :return: Original value bound to the key
        :rtype: :class:`str` or :data:`None`
    ''')

    def __init__(self, key, value):
        super(Replace, self).__init__(key, value)
