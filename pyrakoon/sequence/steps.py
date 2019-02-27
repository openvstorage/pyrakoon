# Copyright (C) iNuron - info@openvstorage.com
# This file is part of Open vStorage. For license information, see <LICENSE.txt>

"""
Sequence steps module
Contains all steps a sequence can make
"""

from __future__ import absolute_import

from .. import protocol


class Step(object):
    """
    A step in a sequence operation
    """
    # Operation command tag
    TAG = None
    # Argument definition
    ARGS = None

    def __init__(self, *args):
        if len(args) != len(self.ARGS):
            raise TypeError('Invalid number of arguments')

        for (_, type_), arg in zip(self.ARGS, args):
            type_.check(arg)

    def serialize(self):
        # type: () -> Iterator[str]
        """
        Serialize the operation
        :return: Serialized operation
        :rtype: Iterator[str]
        """
        for bytes_ in protocol.UINT32.serialize(self.TAG):
            yield bytes_

        for name, type_ in self.ARGS:
            for bytes_ in type_.serialize(getattr(self, name)):
                yield bytes_


class Set(Step):
    """
    "Set" operation
    """
    TAG = 1
    ARGS = ('key', protocol.STRING), ('value', protocol.STRING),

    def __init__(self, key, value):
        # type: (str, str) -> None
        """
        :param key: Key to set
        :type key: str
        :param value: Value to set
        :type value: str
        """
        super(Set, self).__init__(key, value)

        self._key = key
        self._value = value

    @property
    def key(self):
        # type: () -> str
        """
        Key to set
        :rtype: str
        """
        return self._key

    @property
    def value(self):
        # type: () -> str
        """
        Value to set
        :rtype: str
        """
        return self._value


class Delete(Step):
    """
    "Delete" operation
    """
    TAG = 2
    ARGS = ('key', protocol.STRING),

    def __init__(self, key):
        # type: (str) -> None
        """
        :param key: Key to delete
        :type key: str
        """
        super(Delete, self).__init__(key)

        self._key = key

    @property
    def key(self):
        # type: () -> str
        """
        Key to delete
        """
        return self._key


class Assert(Step):
    """
    "Assert" operation
    """
    TAG = 8
    ARGS = (('key', protocol.STRING), ('value', protocol.Option(protocol.STRING)))

    def __init__(self, key, value):
        # type: (str, str) -> None
        super(Assert, self).__init__(key, value)

        self._key = key
        self._value = value

    @property
    def key(self):
        # type: () -> str
        """
        Key for which to assert the given value

        :rtype: str
        """
        return self._key

    @property
    def value(self):
        # type: () -> Union[str, None]
        """
        Expected value

        :rtype: Union[str, None]
        """
        return self._value


class AssertExists(Step):
    """
    "AssertExists" operation
    """
    TAG = 15
    ARGS = ('key', protocol.STRING),

    def __init__(self, key):
        # type: (str) -> None
        """
        :param key: Key to check
        :type key: str
        """
        super(AssertExists, self).__init__(key)

        self._key = key

    @property
    def key(self):
        # type: () -> str
        """
        Key to check
        :rtype: str
        """
        return self._key


class Replace(Step):
    """
    "Replace" operation
    """

    TAG = 16
    ARGS = (('key', protocol.STRING), ('wanted', protocol.Option(protocol.STRING)))

    def __init__(self, key, wanted):
        """
        :param key: Key to replace
        :type key: str
        :param wanted: Value to set
        :type wanted: Union[str, None]
        """
        super(Replace, self).__init__(key, wanted)

        self._key = key
        self._wanted = wanted

    @property
    def key(self):
        # type: () -> str
        """
        Key for which the value needs to be replaced
        :rtype: str
        """
        return self._key

    @property
    def wanted(self):
        # type: () -> Union[str, None]
        """
        Value to set the key to or None to delete the key
        :rtype: Union[str, None]
        """
        return self._wanted


class DeletePrefix(Step):
    """
    "DeletePrefix" operation
    """

    TAG = 14
    ARGS = ('prefix', protocol.STRING),

    def __init__(self, prefix):
        # type: (str) -> None
        """
        :param prefix: Prefix to delete
        :type prefix: str
        """
        super(DeletePrefix, self).__init__(prefix)

        self._prefix = prefix

    @property
    def prefix(self):
        # type: () -> str
        """
        Prefix to delete
        :return:
        """
        return self._prefix
