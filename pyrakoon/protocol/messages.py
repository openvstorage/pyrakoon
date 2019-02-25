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

from .communication import Request, Result, RESULT_SUCCESS
from .types import Option, List, STRING, UINT32, UINT64, INT8, INT32, INT64, FLOAT, BOOL, UNIT, STEP, STATISTICS, CONSISTENCY, CONSISTENCY_ARG


class Message(object):
    """
    Base type for Arakoon command messages
    """

    # Generic command mask value
    MASK = 0xb1ff0000
    # Tag (code) of the command
    TAG = None
    # Arguments required for the command
    ARGS = None
    # Return type of the command
    RETURN_TYPE = None
    # Docstring for methods exposing this command
    DOC = None
    # Serialized representation of :attr:`TAG`
    _tag_bytes = None

    def serialize(self):
        """
        Serialize the command

        :return: Iterable of bytes of the serialized version of the command
        :rtype: iterable of :class:`str`
        """

        if self._tag_bytes is None:
            self._tag_bytes = ''.join(UINT32.serialize(self.TAG))

        yield self._tag_bytes

        for arg in self.ARGS:
            if len(arg) == 2:
                name, type_ = arg
            elif len(arg) == 3:
                name, type_, _ = arg
            else:
                raise ValueError

            for bytes_ in type_.serialize(getattr(self, name)):
                yield bytes_

    def receive(self):
        """
        Read and deserialize the return value of the command

        Running as a coroutine, this method can read and parse the server
        result value once this command has been submitted.

        This method yields values of type :class:`Request` to request more data
        (which should then be injected using the :meth:`send` method of the
        coroutine). The number of requested bytes is provided in the
        :attr:`~Request.count` attribute of the :class:`Request` object.

        Finally a :class:`Result` value is generated, which contains the server
        result in its :attr:`~Result.value` attribute.

        :raise ArakoonError: Server returned an error code

        :see: :func:`pyrakoon.utils.process_blocking`
        """

        from pyrakoon import errors

        code_receiver = UINT32.receive()
        request = code_receiver.next()

        while isinstance(request, Request):
            value = yield request
            request = code_receiver.send(value)

        if not isinstance(request, Result):
            raise TypeError

        code = request.value

        if code == RESULT_SUCCESS:
            result_receiver = self.RETURN_TYPE.receive()
        else:
            # Error
            result_receiver = STRING.receive()

        request = result_receiver.next()

        while isinstance(request, Request):
            value = yield request
            request = result_receiver.send(value)

        if not isinstance(request, Result):
            raise TypeError

        result = request.value

        if code == RESULT_SUCCESS:
            yield Result(result)
        else:
            if code in errors.ERROR_MAP:
                raise errors.ERROR_MAP[code](result)
            else:
                raise errors.ArakoonError(
                    'Unknown error code 0x%x, server said: %s' % \
                        (code, result))


class Hello(Message):
    """
    "hello" message
    """

    __slots__ = '_client_id', '_cluster_id',

    TAG = 0x0001 | Message.MASK
    ARGS = ('client_id', STRING), ('cluster_id', STRING),
    RETURN_TYPE = STRING

    DOC = utils.format_doc('''
        Send a "hello" command to the server

        This method will return the string returned by the server when
        receiving a "hello" command.

        :param client_id: Identifier of the client
        :type client_id: :class:`str`
        :param cluster_id: Identifier of the cluster connecting to. \
            This must match the cluster configuration.
        :type cluster_id: :class:`str`

        :return: Message returned by the server
        :rtype: :class:`str`
    ''')

    def __init__(self, client_id, cluster_id):
        super(Hello, self).__init__()

        self._client_id = client_id
        self._cluster_id = cluster_id

    client_id = property(operator.attrgetter('_client_id'))
    cluster_id = property(operator.attrgetter('_cluster_id'))


class WhoMaster(Message):
    """
    "who_master" message
    """

    __slots__ = ()

    TAG = 0x0002 | Message.MASK
    ARGS = ()
    RETURN_TYPE = Option(STRING)

    DOC = utils.format_doc('''
        Send a "who_master" command to the server

        This method returns the name of the current master node in the Arakoon
        cluster.

        :return: Name of cluster master node
        :rtype: :class:`str`
    ''')


class Exists(Message):
    """
    "exists" message
    """

    __slots__ = '_consistency', '_key',

    TAG = 0x0007 | Message.MASK
    ARGS = CONSISTENCY_ARG, ('key', STRING),
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
        super(Exists, self).__init__()

        self._consistency = consistency
        self._key = key

    key = property(operator.attrgetter('_key'))
    consistency = property(operator.attrgetter('_consistency'))


class Get(Message):
    """
    "get" message
    """

    __slots__ = '_consistency', '_key',

    TAG = 0x0008 | Message.MASK
    ARGS = CONSISTENCY_ARG, ('key', STRING),
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
        super(Get, self).__init__()

        self._consistency = consistency
        self._key = key

    consistency = property(operator.attrgetter('_consistency'))
    key = property(operator.attrgetter('_key'))


class Set(Message):
    """
    "set" message
    """

    __slots__ = '_key', '_value',

    TAG = 0x0009 | Message.MASK
    ARGS = ('key', STRING), ('value', STRING),
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
        super(Set, self).__init__()

        self._key = key
        self._value = value

    key = property(operator.attrgetter('_key'))
    value = property(operator.attrgetter('_value'))


class Delete(Message):
    """
    "delete" message
    """

    __slots__ = '_key',

    TAG = 0x000a | Message.MASK
    ARGS = ('key', STRING),
    RETURN_TYPE = UNIT

    DOC = utils.format_doc('''
        Send a "delete" command to the server

        This method deletes a given key from the cluster.

        :param key: Key to delete
        :type key: :class:`str`
    ''')

    def __init__(self, key):
        super(Delete, self).__init__()

        self._key = key

    key = property(operator.attrgetter('_key'))


class PrefixKeys(Message):
    """
    "prefix_keys" message
    """

    __slots__ = '_consistency', '_prefix', '_max_elements',

    TAG = 0x000c | Message.MASK
    ARGS = CONSISTENCY_ARG, ('prefix', STRING), ('max_elements', INT32, -1),
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
    consistency = property(operator.attrgetter('_consistency'))
    prefix = property(operator.attrgetter('_prefix'))
    max_elements = property(operator.attrgetter('_max_elements'))


class TestAndSet(Message):
    """
    "test_and_set" message
    """

    __slots__ = '_key', '_test_value', '_set_value',

    TAG = 0x000d | Message.MASK
    ARGS = ('key', STRING), ('test_value', Option(STRING)), \
        ('set_value', Option(STRING)),
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
        super(TestAndSet, self).__init__()

        self._key = key
        self._test_value = test_value
        self._set_value = set_value

    key = property(operator.attrgetter('_key'))
    test_value = property(operator.attrgetter('_test_value'))
    set_value = property(operator.attrgetter('_set_value'))


class Sequence(Message):
    """
    "sequence" and "synced_sequence" message
    """

    __slots__ = '_steps', '_sync',

    ARGS = ('steps', List(STEP)), ('sync', BOOL, False),
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


class Range(Message):
    """
    "Range" message
    """

    __slots__ = '_consistency', '_begin_key', '_begin_inclusive', '_end_key', '_end_inclusive', '_max_elements',

    TAG = 0x000b | Message.MASK
    ARGS = CONSISTENCY_ARG, \
        ('begin_key', Option(STRING)), ('begin_inclusive', BOOL), \
        ('end_key', Option(STRING)), ('end_inclusive', BOOL), \
        ('max_elements', INT32, -1),
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

    def __init__(self, consistency, begin_key, begin_inclusive,
        end_key, end_inclusive, max_elements):
        super(Range, self).__init__()

        self._consistency = consistency
        self._begin_key = begin_key
        self._begin_inclusive = begin_inclusive
        self._end_key = end_key
        self._end_inclusive = end_inclusive
        self._max_elements = max_elements

    consistency = property(operator.attrgetter('_consistency'))
    begin_key = property(operator.attrgetter('_begin_key'))
    begin_inclusive = property(operator.attrgetter('_begin_inclusive'))
    end_key = property(operator.attrgetter('_end_key'))
    end_inclusive = property(operator.attrgetter('_end_inclusive'))
    max_elements = property(operator.attrgetter('_max_elements'))


class RangeEntries(Message):
    """
    "RangeEntries" message
    """

    __slots__ = '_consistency', '_begin_key', '_begin_inclusive', '_end_key', \
        '_end_inclusive', '_max_elements',

    TAG = 0x000f | Message.MASK
    ARGS = CONSISTENCY_ARG, \
        ('begin_key', Option(STRING)), ('begin_inclusive', BOOL), \
        ('end_key', Option(STRING)), ('end_inclusive', BOOL), \
        ('max_elements', INT32, -1),
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
        super(RangeEntries, self).__init__()

        self._consistency = consistency
        self._begin_key = begin_key
        self._begin_inclusive = begin_inclusive
        self._end_key = end_key
        self._end_inclusive = end_inclusive
        self._max_elements = max_elements

    consistency = property(operator.attrgetter('_consistency'))
    begin_key = property(operator.attrgetter('_begin_key'))
    begin_inclusive = property(operator.attrgetter('_begin_inclusive'))
    end_key = property(operator.attrgetter('_end_key'))
    end_inclusive = property(operator.attrgetter('_end_inclusive'))
    max_elements = property(operator.attrgetter('_max_elements'))


class MultiGet(Message):
    """
    "multi_get" message
    """

    __slots__ = '_consistency', '_keys',

    TAG = 0x0011 | Message.MASK
    ARGS = CONSISTENCY_ARG, ('keys', List(STRING)),
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
        super(MultiGet, self).__init__()

        self._consistency = consistency
        self._keys = keys

    consistency = property(operator.attrgetter('_consistency'))
    keys = property(operator.attrgetter('_keys'))


class MultiGetOption(Message):
    """
    "multi_get_option" message
    """

    __slots__ = '_consistency', '_keys',

    TAG = 0x0031 | Message.MASK
    ARGS = CONSISTENCY_ARG, ('keys', List(STRING)),
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
        super(MultiGetOption, self).__init__()

        self._consistency = consistency
        self._keys = keys

    consistency = property(operator.attrgetter('_consistency'))
    keys = property(operator.attrgetter('_keys'))


class ExpectProgressPossible(Message):
    """
    "expect_progress_possible" message
    """

    __slots__ = ()

    TAG = 0x0012 | Message.MASK
    ARGS = ()
    RETURN_TYPE = BOOL

    DOC = utils.format_doc('''
        Send a "expect_progress_possible" command to the server

        This method returns whether the master thinks progress is possible.

        :return: Whether the master thinks progress is possible
        :rtype: :class:`bool`
    ''')


class GetKeyCount(Message):
    """
    "get_key_count" message
    """

    __slots__ = ()

    TAG = 0x001a | Message.MASK
    ARGS = ()
    RETURN_TYPE = UINT64

    DOC = utils.format_doc('''
        Send a "get_key_count" command to the server

        This method returns the number of items stored in Arakoon.

        :return: Number of items stored in the database
        :rtype: :class:`int`
    ''')


class UserFunction(Message):
    """
    "user_function" message
    """

    __slots__ = '_function', '_arg',

    TAG = 0x0015 | Message.MASK
    ARGS = ('function', STRING), ('argument', Option(STRING)),
    RETURN_TYPE = Option(STRING)

    DOC = utils.format_doc('''
        Send a "user_function" command to the server

        This method returns the result of the function invocation.

        :param function: Name of the user function to invoke
        :type function: :class:`str`
        :param argument: Argument to pass to the function
        :type argument: :class:`str` or :data:`None`

        :return: Result of the function invocation
        :rtype: :class:`str` or :data:`None`
    ''')

    def __init__(self, function, argument):
        super(UserFunction, self).__init__()

        self._function = function
        self._argument = argument

    function = property(operator.attrgetter('_function'))
    argument = property(operator.attrgetter('_argument'))


class Confirm(Message):
    """
    "confirm" message
    """

    __slots__ = '_key', '_value',

    TAG = 0x001c | Message.MASK
    ARGS = ('key', STRING), ('value', STRING),
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
        super(Confirm, self).__init__()

        self._key = key
        self._value = value

    key = property(operator.attrgetter('_key'))
    value = property(operator.attrgetter('_value'))


class Assert(Message):
    """
    "assert" message
    """

    __slots__ = '_consistency', '_key', '_value',

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
        super(Assert, self).__init__()

        self._consistency = consistency
        self._key = key
        self._value = value

    consistency = property(operator.attrgetter('_consistency'))
    key = property(operator.attrgetter('_key'))
    value = property(operator.attrgetter('_value'))


class AssertExists(Message):
    """
    "assert_exists" message
    """

    __slots__ = '_consistency', '_key',

    TAG = 0x0029 | Message.MASK
    ARGS = CONSISTENCY_ARG, ('key', STRING),
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
        super(AssertExists, self).__init__()

        self._consistency = consistency
        self._key = key

    consistency = property(operator.attrgetter('_consistency'))
    key = property(operator.attrgetter('_key'))


class RevRangeEntries(Message):
    """
    "rev_range_entries" message
    """

    __slots__ = '_consistency', '_begin_key', '_begin_inclusive', '_end_key', \
        '_end_inclusive', '_max_elements',

    TAG = 0x0023 | Message.MASK
    ARGS = CONSISTENCY_ARG, \
        ('begin_key', Option(STRING)), ('begin_inclusive', BOOL), \
        ('end_key', Option(STRING)), ('end_inclusive', BOOL), \
        ('max_elements', INT32, -1),
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
        super(RevRangeEntries, self).__init__()

        self._consistency = consistency
        self._begin_key = begin_key
        self._begin_inclusive = begin_inclusive
        self._end_key = end_key
        self._end_inclusive = end_inclusive
        self._max_elements = max_elements

    consistency = property(operator.attrgetter('_consistency'))
    begin_key = property(operator.attrgetter('_begin_key'))
    begin_inclusive = property(operator.attrgetter('_begin_inclusive'))
    end_key = property(operator.attrgetter('_end_key'))
    end_inclusive = property(operator.attrgetter('_end_inclusive'))
    max_elements = property(operator.attrgetter('_max_elements'))


class Statistics(Message):
    """
    "statistics" message
    """

    __slots__ = ()

    TAG = 0x0013 | Message.MASK
    ARGS = ()
    RETURN_TYPE = STATISTICS

    DOC = utils.format_doc('''
        Send a "statistics" command to the server

        This method returns some server statistics.

        :return: Server statistics
        :rtype: `Statistics`
    ''')


class Version(Message):
    """
    "version" message
    """

    __slots__ = ()

    TAG = 0x0028 | Message.MASK
    ARGS = ()
    RETURN_TYPE = Product(INT32, INT32, INT32, STRING)

    DOC = utils.format_doc('''
        Send a "version" command to the server

        This method returns the server version.

        :return: Server version
        :rtype: `(int, int, int, str)`
     ''')


class DeletePrefix(Message):
    """
    "delete_prefix" message
    """

    __slots__ = '_prefix',

    TAG = 0x0027 | Message.MASK
    ARGS = ('prefix', STRING),
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

    prefix = property(operator.attrgetter('_prefix'))


class Replace(Message):
    """
    "replace" message
    """

    __slots__ = '_key', '_value',

    TAG = 0x0033 | Message.MASK
    ARGS = ('key', STRING), ('value', Option(STRING)),
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
        self._key = key
        self._value = value

    key = property(operator.attrgetter('_key'))
    value = property(operator.attrgetter('_value'))


class Nop(Message):
    """
    "nop" message
    """

    __slots__ = ()

    TAG = 0x0041 | Message.MASK
    ARGS = ()
    RETURN_TYPE = UNIT

    DOC = utils.format_doc('''
        Send a "nop" command to the server

        This enforces consensus throughout a cluster, but has no further
        effects.
    ''')


class GetCurrentState(Message):
    """
    "get_current_state" message
    """

    __slots__ = ()

    TAG = 0x0032 | Message.MASK
    ARGS = ()
    RETURN_TYPE = STRING

    DOC = utils.format_doc('''
        Send a "get_current_state" command to the server

        This call returns a string representing the current state of the node,
        and can be used for troubleshooting purposes.

        :return: State of the server
        :rtype: :class:`str`
    ''')


class GetTxID(Message):
    """
    "get_txid" message
    """

    __slots__ = ()
    TAG = 0x0043 | Message.MASK
    ARGS = ()
    RETURN_TYPE = CONSISTENCY

    DOC = utils.format_doc('''
        Send a "get_txid" command to the server

        This call returns the current transaction ID (if available) of the node.

        :return: Transaction ID of the node
        :rtype: :class:`pyrakoon.consistency.Consistency`
        ''')
