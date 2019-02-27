# Copyright (C) iNuron - info@openvstorage.com
# This file is part of Open vStorage. For license information, see <LICENSE.txt>

"""
Query messages module
Contains messages to query the Arakoon
"""

from __future__ import absolute_import

from ... import utils
from .base import Message, KeysConsistencyMessage, RangeMessage
from ..types import Array, Option, List, Product, STRING, INT32, CONSISTENCY_ARG


class PrefixKeys(Message):
    """
    "prefix_keys" message
    """

    __slots__ = '_consistency', '_prefix', '_max_elements',

    TAG = 0x000c | Message.MASK
    ARGS = (CONSISTENCY_ARG, ('prefix', STRING), ('max_elements', INT32, -1))
    RETURN_TYPE = List(STRING)

    DOC = utils.format_doc('''
        Send a "prefix_keys" command to the server

        This method retrieves a list of keys from the cluster matching a given
        prefix. A maximum number of returned keys can be provided. If set to
        *-1* (the default), all matching keys will be returned.

        :param prefix: Prefix to match
        :type prefix: :class:`str`
        :param max_elements: Maximum number of keys to return
        :type max_elements: :class:`int`
        :param consistency: Allow reads from stale nodes
        :type consistency: :class:`pyrakoon.consistency.Consistency`

        :return: Keys matching the given prefix
        :rtype: iterable of :class:`str`
    ''')

    def __init__(self, consistency, prefix, max_elements):
        super(PrefixKeys, self).__init__()

        self._consistency = consistency
        self._prefix = prefix
        self._max_elements = max_elements

    @property
    def aw(self):
        return

    @property
    def consistency(self):
        return self._consistency

    @property
    def prefix(self):
        return self._prefix

    @property
    def max_elements(self):
        return self._max_elements


class MultiGet(KeysConsistencyMessage):
    """
    "multi_get" message
    """

    __slots__ = ()

    TAG = 0x0011 | Message.MASK
    RETURN_TYPE = List(STRING)

    DOC = utils.format_doc('''
        Send a "multi_get" command to the server

        This method returns a list of the values for all requested keys.

        :param keys: Keys to look up
        :type keys: iterable of :class:`str`
        :param consistency: Allow reads from stale nodes
        :type consistency: :class:`pyrakoon.consistency.Consistency`

        :return: Requested values
        :rtype: iterable of :class:`str`
    ''')

    def __init__(self, consistency, keys):
        super(MultiGet, self).__init__(consistency, keys)


class MultiGetOption(KeysConsistencyMessage):
    """
    "multi_get_option" message
    """

    __slots__ = ()

    TAG = 0x0031 | Message.MASK
    RETURN_TYPE = Array(Option(STRING))

    DOC = utils.format_doc('''
        Send a "multi_get_option" command to the server

        This method returns a list of value options for all requested keys.

        :param keys: Keys to look up
        :type keys: iterable of :class:`str`
        :param consistency: Allow reads from stale nodes
        :type consistency: :class:`pyrakoon.consistency.Consistency`

        :return: Requested values
        :rtype: iterable of (`str` or `None`)
    ''')

    def __init__(self, consistency, keys):
        super(MultiGetOption, self).__init__(consistency, keys)


class RevRangeEntries(RangeMessage):
    """
    "rev_range_entries" message
    """

    __slots__ = ()

    TAG = 0x0023 | Message.MASK
    RETURN_TYPE = List(Product(STRING, STRING))

    DOC = utils.format_doc('''
        Send a "rev_range_entries" command to the server

        The operation will return a list of (key, value) tuples, for keys in
        the reverse range between `begin_key` and `end_key`. The
        `begin_inclusive` and `end_inclusive` flags denote whether the
        delimiters should be included.

        The `max_elements` flag can limit the number of returned items. If it is
        negative, all matching items are returned.

        :param begin_key: Begin of range
        :type begin_key: :class:`str`
        :param begin_inclusive: `begin_key` is in- or exclusive
        :type begin_inclusive: :class:`bool`
        :param end_key: End of range
        :type end_key: :class:`str`
        :param end_inclusive: `end_key` is in- or exclusive
        :type end_inclusive: :class:`bool`
        :param max_elements: Maximum number of items to return
        :type max_elements: :class:`int`
        :param consistency: Allow reads from stale nodes
        :type consistency: :class:`pyrakoon.consistency.Consistency`

        :return: List of matching (key, value) pairs
        :rtype: iterable of `(str, str)`
    ''')

    def __init__(self, consistency, begin_key, begin_inclusive, end_key, end_inclusive, max_elements):
        super(RevRangeEntries, self).__init__(consistency, begin_key, begin_inclusive, end_key, end_inclusive, max_elements)


class Range(RangeMessage):
    """
    "Range" message
    """

    __slots__ = ()

    TAG = 0x000b | Message.MASK
    RETURN_TYPE = List(STRING)

    DOC = utils.format_doc('''
        Send a "range" command to the server

        The operation will return a list of keys, in the range between
        `begin_key` and `end_key`. The `begin_inclusive` and `end_inclusive`
        flags denote whether the delimiters should be included.

        The `max_elements` flag can limit the number of returned keys. If it is
        negative, all matching keys are returned.

        :param begin_key: Begin of range
        :type begin_key: :class:`str`
        :param begin_inclusive: `begin_key` is in- or exclusive
        :type begin_inclusive: :class:`bool`
        :param end_key: End of range
        :type end_key: :class:`str`
        :param end_inclusive: `end_key` is in- or exclusive
        :param max_elements: Maximum number of keys to return
        :type max_elements: :class:`int`
        :param consistency: Allow reads from stale nodes
        :type consistency: :class:`pyrakoon.consistency.Consistency`

        :return: List of matching keys
        :rtype: iterable of :class:`str`
    ''')

    def __init__(self, consistency, begin_key, begin_inclusive, end_key, end_inclusive, max_elements):
        super(Range, self).__init__(consistency, begin_key, begin_inclusive, end_key, end_inclusive, max_elements)


class RangeEntries(RangeMessage):
    """
    "RangeEntries" message
    """

    __slots__ = ()

    TAG = 0x000f | Message.MASK
    RETURN_TYPE = List(Product(STRING, STRING))

    DOC = utils.format_doc('''
        Send a "range_entries" command to the server

        The operation will return a list of (key, value) tuples, for keys in the
        range between `begin_key` and `end_key`. The `begin_inclusive` and
        `end_inclusive` flags denote whether the delimiters should be included.

        The `max_elements` flag can limit the number of returned items. If it is
        negative, all matching items are returned.

        :param begin_key: Begin of range
        :type begin_key: :class:`str`
        :param begin_inclusive: `begin_key` is in- or exclusive
        :type begin_inclusive: :class:`bool`
        :param end_key: End of range
        :type end_key: :class:`str`
        :param end_inclusive: `end_key` is in- or exclusive
        :type end_inclusive: :class:`bool`
        :param max_elements: Maximum number of items to return
        :type max_elements: :class:`int`
        :param consistency: Allow reads from stale nodes
        :type consistency: :class:`pyrakoon.consistency.Consistency`

        :return: List of matching (key, value) pairs
        :rtype: iterable of `(str, str)`
    ''')

    def __init__(self, consistency, begin_key, begin_inclusive, end_key, end_inclusive, max_elements):
        super(RangeEntries, self).__init__(consistency, begin_key, begin_inclusive, end_key, end_inclusive, max_elements)
