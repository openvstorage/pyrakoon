# Copyright (C) iNuron - info@openvstorage.com
# This file is part of Open vStorage. For license information, see <LICENSE.txt>
from .. import utils
from .utils import validate_signature as _validate_signature


class Update(object):
    def write(self, fob):
        raise NotImplementedError()


class Set(Update):
    def __init__(self, key, value):
        self._key = key
        self._value = value


class Delete(Update):
    def __init__(self, key):
        self._key = key


class DeletePrefix(Update):
    def __init__(self, prefix):
        self._prefix = prefix


class Assert(Update):
    def __init__(self, key, value):
        self._key = key
        self._value = value


class AssertExists(Update):
    def __init__(self, key):
        self._key = key


class Replace(Update):
    def __init__(self, key, wanted):
        self._key = key
        self._wanted = wanted


class Sequence(Update):
    def __init__(self):
        self._updates = []

    def addUpdate(self, u):
        self._updates.append(u)

    @utils.update_argspec('self', 'key', 'value')
    @_validate_signature('string', 'string')
    def addSet(self, key, value):
        self._updates.append(Set(key, value))

    @utils.update_argspec('self', 'prefix', )
    @_validate_signature('string')
    def addDeletePrefix(self, prefix):
        self._updates.append(DeletePrefix(prefix))

    @utils.update_argspec('self', 'key')
    @_validate_signature('string')
    def addDelete(self, key):
        self._updates.append(Delete(key))

    def addAssert(self, key, value):
        self._updates.append(Assert(key, value))

    @utils.update_argspec('self', 'key')
    @_validate_signature('string')
    def addAssertExists(self, key):
        self._updates.append(AssertExists(key))

    @utils.update_argspec('self', 'key', 'wanted')
    @_validate_signature('string', 'string_option')
    def addReplace(self, key, wanted):
        self._updates.append(Replace(key, wanted))
