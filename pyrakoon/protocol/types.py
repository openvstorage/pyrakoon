# Copyright (C) iNuron - info@openvstorage.com
# This file is part of Open vStorage. For license information, see <LICENSE.txt>

from __future__ import absolute_import

import struct
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO
from .communication import Request, Result
from .. import utils
from .. import consistency


class Type(object):
    """
    Base type for Arakoon serializable types
    """

    PACKER = None
    """
    :class:`~struct.Struct` instance used by default :meth:`serialize` and
    :meth:`receive` implementations
    :type: :class:`struct.Struct`
    """

    def check(self, value):
        """
        Check whether a value is valid for this type

        :param value: Value to test
        :type value: :obj:`object`

        :return: Whether the value is valid for this type
        :rtype: :class:`bool`
        """

        raise NotImplementedError()

    def serialize(self, value):
        """
        Serialize value

        :param value: Value to serialize
        :type value: :obj:`object`

        :return: Iterable of bytes of the serialized value
        :rtype: iterable of :class:`str`
        """

        if not self.PACKER:
            raise NotImplementedError()

        yield self.PACKER.pack(value)

    def receive(self):
        """
        Receive and parse a result from the server

        This method is a coroutine which yields :class:`Request` instances, and
        finally a :class:`Result`. When a :class:`Request` instance is yielded,
        the number of bytes as specified in the :attr:`~Request.count`
        attribute should be sent back.

        If finally a :class:`Result` instance is yield, its
        :attr:`~Result.value` attribute contains the actual message result.

        :see: :meth:`Message.receive`
        """

        if not self.PACKER:
            raise NotImplementedError

        data = yield Request(self.PACKER.size)

        result, = self.PACKER.unpack(data)

        yield Result(result)


class String(Type):
    """
    String type
    """

    def check(self, value):
        if not isinstance(value, str):
            raise TypeError

    def serialize(self, value):
        length = len(value)

        for bytes_ in UINT32.serialize(length):
            yield bytes_

        yield struct.pack('<%ds' % length, value)

    def receive(self):
        length_receiver = UINT32.receive()
        request = length_receiver.next()

        while isinstance(request, Request):
            value = yield request
            request = length_receiver.send(value)

        if not isinstance(request, Result):
            raise TypeError()

        length = request.value

        if length == 0:
            result = ''
        else:
            data = yield Request(length)
            result, = struct.unpack('<%ds' % length, data)

        yield Result(result)


class UnsignedInteger(Type):
    """
    Unsigned integer type
    """

    def __init__(self, bits, pack):
        """
        Initialize an unsigned integer type

        :param bits: Bits containing the value
        :type bits: :class:`int`
        :param pack: Struct type, passed to `struct.Struct`
        :type pack: :class:`str`
        """

        super(UnsignedInteger, self).__init__()

        self.MAX_INT = (2 ** bits) - 1
        self.PACKER = struct.Struct(pack)

    def check(self, value):
        if not isinstance(value, (int, long)):
            raise TypeError

        if value < 0:
            raise ValueError('Unsigned integer expected')

        if value > self.MAX_INT:
            raise ValueError('Integer overflow')


class SignedInteger(Type):
    """
    Signed integer type
    """

    def __init__(self, bits, pack):
        """
        Initialize an unsigned integer type

        :param bits: Bits containing the value
        :type bits: :class:`int`
        :param pack: Struct type, passed to `struct.Struct`
        :type pack: :class:`str`
        """

        super(SignedInteger, self).__init__()

        self.MAX_INT = ((2 ** bits) / 2) - 1
        self.PACKER = struct.Struct(pack)

    def check(self, value):
        if not isinstance(value, (int, long)):
            raise TypeError

        if abs(value) > self.MAX_INT:
            raise ValueError('Integer overflow')


class Float(Type):
    """
    Float type
    """

    PACKER = struct.Struct('<d')

    def check(self, value):
        if not isinstance(value, float):
            raise TypeError()


class Bool(Type):
    """
    Bool type
    """

    PACKER = struct.Struct('<c')

    TRUE = chr(1)
    FALSE = chr(0)

    def check(self, value):
        if not isinstance(value, bool):
            raise TypeError

    def serialize(self, value):
        if value:
            yield self.PACKER.pack(self.TRUE)
        else:
            yield self.PACKER.pack(self.FALSE)

    def receive(self):
        value_receiver = super(Bool, self).receive()
        request = value_receiver.next()

        while isinstance(request, Request):
            value = yield request
            request = value_receiver.send(value)

        if not isinstance(request, Result):
            raise TypeError

        value = request.value

        if value == self.TRUE:
            yield Result(True)
        elif value == self.FALSE:
            yield Result(False)
        else:
            raise ValueError('Unexpected bool value "0x%02x"' % ord(value))


class Unit(Type):
    """
    Unit type
    """

    def check(self, value):
        raise NotImplementedError('Unit can\'t be checked')

    def serialize(self, value):
        raise NotImplementedError('Unit can\'t be serialized')

    def receive(self):
        yield Result(None)


class Step(Type):
    """
    Step type
    """

    def check(self, value):
        # Circular dependency
        from .. import sequence

        if not isinstance(value, sequence.Step):
            raise TypeError

        if isinstance(value, sequence.Sequence):
            for step in value.steps:
                if not isinstance(step, sequence.Step):
                    raise TypeError

                if isinstance(step, sequence.Sequence):
                    self.check(step)

    def serialize(self, value):
        for part in value.serialize():
            yield part

    def receive(self):
        raise NotImplementedError('Steps can\'t be received')


class Option(Type):
    """
    Option type
    """

    def __init__(self, inner_type):
        super(Option, self).__init__()
        self._inner_type = inner_type

    def check(self, value):
        if value is None:
            return

        self._inner_type.check(value)

    def serialize(self, value):
        if value is None:
            for bytes_ in BOOL.serialize(False):
                yield bytes_
        else:
            for bytes_ in BOOL.serialize(True):
                yield bytes_

            for bytes_ in self._inner_type.serialize(value):
                yield bytes_

    def receive(self):
        has_value_receiver = BOOL.receive()
        request = has_value_receiver.next()

        while isinstance(request, Request):
            value = yield request
            request = has_value_receiver.send(value)

        if not isinstance(request, Result):
            raise TypeError()

        has_value = request.value

        if not has_value:
            yield Result(None)
        else:
            receiver = self._inner_type.receive()
            request = receiver.next()

            while isinstance(request, Request):
                value = yield request
                request = receiver.send(value)

            if not isinstance(request, Result):
                raise TypeError()

            yield Result(request.value)


class List(Type):
    """
    List type
    """

    def __init__(self, inner_type):
        super(List, self).__init__()
        self._inner_type = inner_type

    def check(self, value):
        # Get rid of the usual suspects
        if isinstance(value, (str, unicode, )):
            raise TypeError()

        values = tuple(value)

        for value in values:
            self._inner_type.check(value)

    def serialize(self, value):
        values = tuple(value)

        for bytes_ in UINT32.serialize(len(values)):
            yield bytes_

        for value in values:
            for bytes_ in self._inner_type.serialize(value):
                yield bytes_

    def receive(self):
        count_receiver = UINT32.receive()
        request = count_receiver.next()

        while isinstance(request, Request):
            value = yield request
            request = count_receiver.send(value)

        if not isinstance(request, Result):
            raise TypeError()

        count = request.value

        values = [None] * count
        for idx in xrange(count - 1, -1, -1):
            receiver = self._inner_type.receive()
            request = receiver.next()

            while isinstance(request, Request):
                value = yield request
                request = receiver.send(value)

            if not isinstance(request, Result):
                raise TypeError()

            value = request.value

            # Note: can't 'yield' value, otherwise we might not read all values
            # from the stream, and leave it in an unclean state
            values[idx] = value

        yield Result(values)


class Array(Type):
    """
    Array type
    """

    def __init__(self, inner_type):
        super(Array, self).__init__()

        self._inner_type = inner_type

    def check(self, value):
        raise NotImplementedError('Arrays can\'t be checked')

    def serialize(self, value):
        raise NotImplementedError('Arrays can\'t be serialized')

    def receive(self):
        count_receiver = UINT32.receive()
        request = count_receiver.next()

        while isinstance(request, Request):
            value = yield request
            request = count_receiver.send(value)

        if not isinstance(request, Result):
            raise TypeError()

        count = request.value

        values = [None] * count
        for idx in xrange(0, count):
            receiver = self._inner_type.receive()
            request = receiver.next()

            while isinstance(request, Request):
                value = yield request
                request = receiver.send(value)

            if not isinstance(request, Result):
                raise TypeError()

            value = request.value

            # Note: can't 'yield' value, otherwise we might not read all values
            # from the stream, and leave it in an unclean state
            values[idx] = value

        yield Result(values)


class Product(Type):
    """
    Product type
    """

    def __init__(self, *inner_types):
        super(Product, self).__init__()

        self._inner_types = tuple(inner_types)

    def check(self, value):
        # Get rid of the usual suspects
        if isinstance(value, (str, unicode, )):
            raise TypeError()

        values = tuple(value)

        if len(values) != len(self._inner_types):
            raise ValueError()

        for type_, value_ in zip(self._inner_types, values):
            type_.check(value_)

    def serialize(self, value):
        values = tuple(value)

        for type_, value_ in zip(self._inner_types, values):
            for bytes_ in type_.serialize(value_):
                yield bytes_

    def receive(self):
        values = []

        for type_ in self._inner_types:
            receiver = type_.receive()
            request = receiver.next()

            while isinstance(request, Request):
                value = yield request
                request = receiver.send(value)

            if not isinstance(request, Result):
                raise TypeError()

            value = request.value
            values.append(value)

        yield Result(tuple(values))


class NamedField(Type):
    """
    NamedField type
    """

    FIELD_TYPE_INT = 1
    FIELD_TYPE_INT64 = 2
    FIELD_TYPE_FLOAT = 3
    FIELD_TYPE_STRING = 4
    FIELD_TYPE_LIST = 5

    def check(self, value):
        raise NotImplementedError('NamedFields can\'t be checked')

    def serialize(self, value):
        raise NotImplementedError('NamedFields can\'t be serialized')

    @classmethod
    def receive(cls):
        type_receiver = INT32.receive()
        request = type_receiver.next()

        while isinstance(request, Request):
            value = yield request
            request = type_receiver.send(value)

        if not isinstance(request, Result):
            raise TypeError()

        type_ = request.value

        name_receiver = STRING.receive()
        request = name_receiver.next()

        while isinstance(request, Request):
            value = yield request
            request = name_receiver.send(value)

        if not isinstance(request, Result):
            raise TypeError()

        name = request.value

        if type_ == cls.FIELD_TYPE_INT:
            value_receiver = INT32.receive()
        elif type_ == cls.FIELD_TYPE_INT64:
            value_receiver = INT64.receive()
        elif type_ == cls.FIELD_TYPE_FLOAT:
            value_receiver = FLOAT.receive()
        elif type_ == cls.FIELD_TYPE_STRING:
            value_receiver = STRING.receive()
        elif type_ == cls.FIELD_TYPE_LIST:
            value_receiver = List(NamedField).receive()
        else:
            raise ValueError('Unknown named field type %d' % type_)

        request = value_receiver.next()

        while isinstance(request, Request):
            value = yield request
            request = value_receiver.send(value)

        if not isinstance(request, Result):
            raise TypeError()

        value = request.value

        if type_ == cls.FIELD_TYPE_LIST:
            result = dict()
            map(result.update, value)
            value = result

        yield Result({name: value})


class StatisticsType(Type):
    """
    Statistics type
    """

    def check(self, value):
        raise NotImplementedError('Statistics can\'t be checked')

    def serialize(self, value):
        raise NotImplementedError('Statistics can\'t be serialized')

    def receive(self):
        buffer_receiver = STRING.receive()
        request = buffer_receiver.next()

        while isinstance(request, Request):
            value = yield request
            request = buffer_receiver.send(value)

        if not isinstance(request, Result):
            raise TypeError()

        read = StringIO.StringIO(request.value).read
        result = utils.read_blocking(NamedField.receive(), read)

        if 'arakoon_stats' not in result:
            raise ValueError('Missing expected \'arakoon_stats\' value')

        yield Result(result['arakoon_stats'])

class RangeAssertionType(Type):
    def check(self, value):
        pass #TODO

    def serialize(self, value):
        for bytes_ in INT32.serialize(1):
            yield bytes_

        keys = value._keys
        n_keys = len(keys)

        for bytes_ in INT32.serialize(n_keys):
            yield bytes_

        for k in keys:
            for data in STRING.serialize(k):
                yield data


class Consistency(Type):
    """
    Consistency type
    """

    def check(self, value):
        if value is not consistency.CONSISTENT \
                and value is not consistency.INCONSISTENT \
                and value is not None \
                and not isinstance(value, consistency.AtLeast):
            raise ValueError('Invalid `consistency` value')

    def serialize(self, value):
        if value is consistency.CONSISTENT or value is None:
            yield '\0'
        elif value is consistency.INCONSISTENT:
            yield '\1'
        elif isinstance(value, consistency.AtLeast):
            yield '\2'
            for data in INT64.serialize(value.i):
                yield data
        else:
            raise ValueError()

    def receive(self):
        tag_receiver = INT8.receive()
        request = tag_receiver.next()

        while isinstance(request, Request):
            value = yield request
            request = tag_receiver.send(value)

        if not isinstance(request, Result):
            raise TypeError

        if request.value == 0:
            yield Result(consistency.CONSISTENT)
        elif request.value == 1:
            yield Result(consistency.INCONSISTENT)
        elif request.value == 2:
            i_receiver = INT64.receive()
            request = i_receiver.next()

            while isinstance(request, Request):
                value = yield request
                request = i_receiver.send(value)

            if not isinstance(request, Result):
                raise TypeError()

            yield Result(consistency.AtLeast(request.value))
        else:
            raise ValueError('Unknown consistency tag \'%d\'' % request.value)


# Instances
STRING = String()

UINT32 = UnsignedInteger(32, '<I')
UINT64 = UnsignedInteger(64, '<Q')

INT8 = SignedInteger(8, '<b')
INT32 = SignedInteger(32, '<i')
INT64 = SignedInteger(64, '<q')

FLOAT = Float()

BOOL = Bool()

UNIT = Unit()

STEP = Step()

STATISTICS = StatisticsType()

CONSISTENCY = Consistency()

# Well-known `consistency` argument
CONSISTENCY_ARG = ('consistency', CONSISTENCY, None)

RANGE_ASSERTION = RangeAssertionType()
