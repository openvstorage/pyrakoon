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
from pyrakoon.consistency import Consistency
from ..communication import Request, Result, RESULT_SUCCESS
from ..types import STRING, UINT32, CONSISTENCY_ARG, List, Option, BOOL, INT32


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
                    'Unknown error code 0x%x, server said: %s' % (code, result))


class KeyMessage(Message):
    """
    Interface class with key and value properties
    """

    __slots__ = '_key',

    ARGS = (('key', STRING),)

    def __init__(self, key):
        # type: (str) -> None
        """
        :param key: Key to use
        :type key: str
        """
        super(KeyMessage, self).__init__()

        self._key = key

    @property
    def key(self):
        return self._key


class KeyValueMessage(KeyMessage):
    """
    Interface class with key and value properties
    """

    __slots__ = '_value',

    ARGS = (('key', STRING), ('value', STRING))

    def __init__(self, key, value):
        # type: (str, any) -> any
        """
        :param key: Key to use
        :type key: str
        :param value: Value to use
        :type value: any 
        """
        super(KeyValueMessage, self).__init__(key)
        self._value = value

    @property
    def value(self):
        return self._value


class KeyConsistencyMessage(Message):
    """
    Interface class with key and consistency properties
    """
    __slots__ = '_consistency', '_key'

    ARGS = (CONSISTENCY_ARG, ('key', STRING))

    def __init__(self, consistency, key):
        # type: (Consistency, str) -> None
        """
        :param key: Key to use
        :type key: str
        :param consistency: Allow reads from stale nodes
        :type consistency: Consistency
        """
        super(KeyConsistencyMessage, self).__init__()

        self._consistency = consistency
        self._key = key

    @property
    def consistency(self):
        return self._consistency

    @property
    def key(self):
        return self._key


class KeyValueConsistencyMessage(KeyConsistencyMessage):
    """
    Interface class with key, value and consistency properties
    """

    __slots__ = '_value',

    ARGS = (CONSISTENCY_ARG, ('key', STRING), ('value', STRING))

    def __init__(self, consistency, key, value):
        # type: (Consistency, str, any) -> None
        """
        :param key: Key to use
        :type key: str
        :param consistency: Allow reads from stale nodes
        :type consistency: Consistency
        :param value: Value to use
        :type value: any
        """
        super(KeyValueConsistencyMessage, self).__init__(consistency, key)
        self._value = value

    @property
    def value(self):
        return self._value
    
    
class KeysConsistencyMessage(Message):
    """
    Interface class with keys and consistency properties
    """
    __slots__ = '_consistency', '_keys',

    ARGS = CONSISTENCY_ARG, ('keys', List(STRING)),

    def __init__(self, consistency, keys):
        super(KeysConsistencyMessage, self).__init__()

        self._consistency = consistency
        self._keys = keys

    @property
    def consistency(self):
        return self._consistency

    @property
    def keys(self):
        return self._keys


class RangeMessage(Message):
    """
    Interface class for ranges
    """
    __slots__ = ('_consistency', '_begin_key', '_begin_inclusive', '_end_key', '_end_inclusive', '_max_elements')

    ARGS = (CONSISTENCY_ARG, ('begin_key', Option(STRING)), ('begin_inclusive', BOOL), ('end_key', Option(STRING)),
            ('end_inclusive', BOOL), ('max_elements', INT32, -1))

    def __init__(self, consistency, begin_key, begin_inclusive, end_key, end_inclusive, max_elements):
        # type: (Consistency, str, bool, str, bool, int) -> None
        """
        :param begin_key: Begin of range
        :type begin_key: str
        :param begin_inclusive: `begin_key` is in- or exclusive
        :type begin_inclusive: bool
        :param end_key: End of range
        :type end_key: str
        :param end_inclusive: `end_key` is in- or exclusive
        :type end_inclusive: bool
        :param max_elements: Maximum number of items to return
        :type max_elements: int
        :param consistency: Allow reads from stale nodes
        :type consistency: Consistency
        """
        super(RangeMessage, self).__init__()

        self._consistency = consistency
        self._begin_key = begin_key
        self._begin_inclusive = begin_inclusive
        self._end_key = end_key
        self._end_inclusive = end_inclusive
        self._max_elements = max_elements

    @property
    def consistency(self):
        return self._consistency

    @property
    def begin_key(self):
        return self._begin_key

    @property
    def begin_inclusive(self):
        return self._begin_inclusive

    @property
    def end_key(self):
        return self._end_key

    @property
    def end_inclusive(self):
        return self._end_inclusive

    @property
    def max_elements(self):
        return self._max_elements
