# Copyright (C) iNuron - info@openvstorage.com
# This file is part of Open vStorage. For license information, see <LICENSE.txt>

"""
Testing messages module
Contains various message to test values on the Arakoon
"""

from __future__ import absolute_import

from ... import utils
from .base import Message, KeyConsistencyMessage, KeyValueConsistencyMessage
from ..types import Option, STRING, BOOL, UNIT, CONSISTENCY_ARG


class Exists(KeyConsistencyMessage):
    """
    "exists" message
    """

    __slots__ = ()

    TAG = 0x0007 | Message.MASK
    RETURN_TYPE = BOOL

    DOC = utils.format_doc('''
        Send an "exists" command to the server

        This method returns a boolean which tells whether the given `key` is
        set on the server.

        :param key: Key to test
        :type key: :class:`str`
        :param consistency: Allow reads from stale nodes
        :type consistency: :class:`pyrakoon.consistency.Consistency`

        :return: Whether the given key is set on the server
        :rtype: :class:`bool`
    ''')

    def __init__(self, consistency, key):
        super(Exists, self).__init__(consistency, key)


class Assert(KeyValueConsistencyMessage):
    """
    "assert" message
    """

    __slots__ = ()

    TAG = 0x0016 | Message.MASK
    ARGS = CONSISTENCY_ARG, ('key', STRING), ('value', Option(STRING)),
    RETURN_TYPE = UNIT

    DOC = utils.format_doc('''
        Send an "assert" command to the server

        `assert key vo` throws an exception if the value associated with the
        key is not what was expected.

        :param key: Key to check
        :type key: :class:`str`
        :param value: Optional value to compare
        :type value: :class:`str` or :data:`None`
        :param consistency: Allow reads from stale nodes
        :type consistency: :class:`pyrakoon.consistency.Consistency`
    ''')

    def __init__(self, consistency, key, value):
        super(Assert, self).__init__(consistency, key, value)


class AssertExists(KeyConsistencyMessage):
    """
    "assert_exists" message
    """

    __slots__ = ()

    TAG = 0x0029 | Message.MASK
    RETURN_TYPE = UNIT

    DOC = utils.format_doc('''
        Send an "assert_exists" command to the server

        `assert_exists key` throws an exception if the key doesn't exist in
        the database.

        :param key: Key to check
        :type key: :class:`str`
        :param consistency: Allow reads from stale nodes
        :type consistency: :class:`pyrakoon.consistency.Consistency`
    ''')

    def __init__(self, consistency, key):
        super(AssertExists, self).__init__(consistency, key)
