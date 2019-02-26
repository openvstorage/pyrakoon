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
Functional Arakoon client
Exposes all possible messages that can be sent towards the server as methods
"""

from __future__ import absolute_import

import logging

from .socket import ArakoonSocketClient
from ..consistency import Consistency, Consistent, NoGuarantee, AtLeast
from ..utils import convert_exceptions as _convert_exceptions, validate_signature as _validate_signature
from ..sequence import Set, Delete, DeletePrefix, Assert, AssertExists, Replace, Sequence
from ..errors import ArakoonException
from ... import utils, consistency, sequence, protocol
from ...constants.logging import PYRAKOON_COMPAT_LOGGER
from ...protocol import admin

logger = logging.getLogger(PYRAKOON_COMPAT_LOGGER)


class ArakoonClient(object):

    def __init__(self, config, timeout=0, noMasterTimeout=0):
        """
        Constructor of an Arakoon client object.

        It takes one optional paramater 'config'.
        This parameter contains info on the arakoon server nodes.
        See the constructor of L{ArakoonClientConfig} for more details.

        @param config: The L{ArakoonClientConfig} object to be used by the client. Defaults to None in which
        case a default L{ArakoonClientConfig} object will be created.
        @type config: L{ArakoonClientConfig}
        @param timeout: tcp connection timeout
        @type timeout: int or float
        @param noMasterTimeout: period (in seconds) messages to the master should be retried when a master re-election occurs
        @type noMasterTimeout: int or float
        """
        self._client = ArakoonSocketClient(config, timeout, noMasterTimeout)

        # Keep a reference, for compatibility reasons
        self._config = config
        self._consistency = Consistent()

    def _initialize(self, config):
        raise NotImplementedError()

    def _determine_consistency(self, provided_consistency):
        determined_consistency = provided_consistency or self._consistency

        if isinstance(determined_consistency, Consistent):
            determined_consistency = consistency.CONSISTENT
        elif isinstance(determined_consistency, NoGuarantee):
            determined_consistency = consistency.INCONSISTENT
        elif isinstance(determined_consistency, AtLeast):
            determined_consistency = consistency.AtLeast(determined_consistency.i)
        else:
            raise ValueError('consistency')
        return determined_consistency

    @utils.update_argspec('self', 'clientId', ('clusterId', 'arakoon'))
    @_convert_exceptions
    @_validate_signature('string', 'string')
    def hello(self, clientId, clusterId='arakoon'):
        """
        Send a string of your choosing to the server.

        Will return the server node identifier and the version of arakoon it is running

        @type clientId  : string
        @type clusterId : string
        @param clusterId : must match the cluster_id of the node

        @rtype: string
        @return: The master identifier and its version in a single string
        """

        return self._client.hello(clientId, clusterId)

    @utils.update_argspec('self', 'key', ('consistency', None))
    @_convert_exceptions
    @_validate_signature('string', 'consistency_option')
    def exists(self, key, consistency=None):
        """
        @type key : string
        @param key : key
        @return : True if there is a value for that key, False otherwise
        """

        return self._client.exists(key, consistency=consistency)

    @utils.update_argspec('self', 'key', ('consistency', None))
    @_convert_exceptions
    @_validate_signature('string', 'consistency_option')
    def get(self, key, consistency=None):
        """
        Retrieve a single value from the store.

        Retrieve the value associated with the given key

        @type key: string
        @param key: The key whose value you are interested in

        @rtype: string
        @return: The value associated with the given key
        """
        return self._client.get(key, consistency=self._determine_consistency(consistency))

    @utils.update_argspec('self', 'key', 'value')
    @_convert_exceptions
    @_validate_signature('string', 'string')
    def set(self, key, value):
        """
        Update the value associated with the given key.

        If the key does not yet have a value associated with it, a new key value pair will be created.
        If the key does have a value associated with it, it is overwritten.
        For conditional value updates see L{testAndSet}

        @type key: string
        @type value: string
        @param key: The key whose associated value you want to update
        @param value: The value you want to store with the associated key

        @rtype: void
        """

        return self._client.set(key, value)

    @utils.update_argspec('self', 'seq', ('sync', False))
    @_convert_exceptions
    @_validate_signature('sequence', 'bool')
    def sequence(self, seq, sync=False):
        """
        Try to execute a sequence of updates.

        It's all-or-nothing: either all updates succeed, or they all fail.
        @type seq: Sequence
        """

        def convert_set(step):
            return sequence.Set(step._key, step._value)

        def convert_delete(step):
            return sequence.Delete(step._key)

        def convert_assert(step):
            return sequence.Assert(step._key, step._value)

        def convert_delete_prefix(step):
            return sequence.DeletePrefix(step._prefix)

        def convert_assert_exists(step):
            return sequence.AssertExists(step._key)

        def convert_replace(step):
            return sequence.Replace(step._key, step._wanted)

        def convert_sequence(sequence_):
            steps = []

            for step in sequence_._updates:
                if isinstance(step, Set):
                    steps.append(convert_set(step))
                elif isinstance(step, Delete):
                    steps.append(convert_delete(step))
                elif isinstance(step, DeletePrefix):
                    steps.append(convert_delete_prefix(step))
                elif isinstance(step, Assert):
                    steps.append(convert_assert(step))
                elif isinstance(step, AssertExists):
                    steps.append(convert_assert_exists(step))
                elif isinstance(step, Sequence):
                    steps.append(convert_sequence(step))
                elif isinstance(step, Replace):
                    steps.append(convert_replace(step))
                else:
                    raise TypeError

            return sequence.Sequence(steps)

        return self._client.sequence((convert_sequence(seq),), sync=sync)

    @utils.update_argspec('self', 'key')
    @_convert_exceptions
    @_validate_signature('string')
    def delete(self, key):
        """
        Remove a key-value pair from the store.

        @type key: string
        @param key: Remove this key and its associated value from the store

        @rtype: void
        """

        return self._client.delete(key)

    @utils.update_argspec('self', 'beginKey', 'beginKeyIncluded', 'endKey', 'endKeyIncluded', ('maxElements', -1))
    @_convert_exceptions
    @_validate_signature('string_option', 'bool', 'string_option', 'bool', 'int')
    def range(self, beginKey, beginKeyIncluded, endKey, endKeyIncluded, maxElements=-1):
        """
        Perform a range query on the store, retrieving the set of matching keys

        Retrieve a set of keys that lexographically fall between the beginKey and the endKey
        You can specify whether the beginKey and endKey need to be included in the result set
        Additionaly you can limit the size of the result set to maxElements. Default is to return all matching keys.

        @type beginKey: string option
        @type beginKeyIncluded: boolean
        @type endKey :string option
        @type endKeyIncluded: boolean
        @type maxElements: integer
        @param beginKey: Lower boundary of the requested range
        @param beginKeyIncluded: Indicates if the lower boundary should be part of the result set
        @param endKey: Upper boundary of the requested range
        @param endKeyIncluded: Indicates if the upper boundary should be part of the result set
        @param maxElements: The maximum number of keys to return. Negative means no maximum, all matches will be returned. Defaults to -1.

        @rtype: list of strings
        @return: Returns a list containing all matching keys
        """
        result = self._client.range(beginKey, beginKeyIncluded,
                                    endKey, endKeyIncluded,
                                    maxElements,
                                    consistency=self._determine_consistency(self._consistency))

        return result

    @utils.update_argspec('self', 'beginKey', 'beginKeyIncluded', 'endKey', 'endKeyIncluded', ('maxElements', -1))
    @_convert_exceptions
    @_validate_signature('string_option', 'bool', 'string_option', 'bool', 'int')
    def range_entries(self, beginKey, beginKeyIncluded, endKey, endKeyIncluded, maxElements=-1):
        """
        Perform a range query on the store, retrieving the set of matching key-value pairs

        Retrieve a set of keys that lexographically fall between the beginKey and the endKey
        You can specify whether the beginKey and endKey need to be included in the result set
        Additionaly you can limit the size of the result set to maxElements. Default is to return all matching keys.

        @type beginKey: string option
        @type beginKeyIncluded: boolean
        @type endKey :string option
        @type endKeyIncluded: boolean
        @type maxElements: integer
        @param beginKey: Lower boundary of the requested range
        @param beginKeyIncluded: Indicates if the lower boundary should be part of the result set
        @param endKey: Upper boundary of the requested range
        @param endKeyIncluded: Indicates if the upper boundary should be part of the result set
        @param maxElements: The maximum number of key-value pairs to return. Negative means no maximum, all matches will be returned. Defaults to -1.

        @rtype: list of strings
        @return: Returns a list containing all matching key-value pairs
        """
        result = self._client.range_entries(beginKey, beginKeyIncluded,
                                            endKey, endKeyIncluded,
                                            maxElements,
                                            consistency=self._determine_consistency(self._consistency))

        return result

    @utils.update_argspec('self', 'keyPrefix', ('maxElements', -1))
    @_convert_exceptions
    @_validate_signature('string', 'int')
    def prefix(self, keyPrefix, maxElements=-1):
        """
        Retrieve a set of keys that match with the provided prefix.

        You can indicate whether the prefix should be included in the result set if there is a key that matches exactly
        Additionaly you can limit the size of the result set to maxElements

        @type keyPrefix: string
        @type maxElements: integer
        @param keyPrefix: The prefix that will be used when pattern matching the keys in the store
        @param maxElements: The maximum number of keys to return. Negative means no maximum, all matches will be returned. Defaults to -1.

        @rtype: list of strings
        @return: Returns a list of keys matching the provided prefix
        """
        result = self._client.prefix(keyPrefix, maxElements, consistency=self._determine_consistency(self._consistency))

        return result

    @utils.update_argspec('self')
    @_convert_exceptions
    def whoMaster(self):
        self._client.determine_master()
        return self._client.master_id

    @utils.update_argspec('self', 'key', 'oldValue', 'newValue')
    @_convert_exceptions
    @_validate_signature('string', 'string_option', 'string_option')
    def testAndSet(self, key, oldValue, newValue):
        """
        Conditionaly update the value associcated with the provided key.

        The value associated with key will be updated to newValue if the current value in the store equals oldValue
        If the current value is different from oldValue, this is a no-op.
        Returns the value that was associated with key in the store prior to this operation. This way you can check if the update was executed or not.

        @type key: string
        @type oldValue: string option
        @type newValue: string
        @param key: The key whose value you want to updated
        @param oldValue: The expected current value associated with the key.
        @param newValue: The desired new value to be stored.

        @rtype: string
        @return: The value that was associated with the key prior to this operation
        """

        return self._client.test_and_set(key, oldValue, newValue)

    @utils.update_argspec('self', 'keys')
    @_convert_exceptions
    @_validate_signature('string_list')
    def multiGet(self, keys):
        """
        Retrieve the values for the keys in the given list.

        @type keys: string list
        @rtype: string list
        @return: the values associated with the respective keys
        """
        return self._client.multi_get(keys, consistency=self._determine_consistency(self._consistency))

    @utils.update_argspec('self', 'keys')
    @_convert_exceptions
    @_validate_signature('string_list')
    def multiGetOption(self, keys):
        """
        Retrieve the values for the keys in the given list.

        @type keys: string list
        @rtype: string option list
        @return: the values associated with the respective keys (None if no value corresponds)
        """
        return self._client.multi_get_option(keys, consistency=self._determine_consistency(self._consistency))

    @utils.update_argspec('self')
    @_convert_exceptions
    def expectProgressPossible(self):
        """
        @return: true if the master thinks progress is possible, false otherwise
        """
        try:
            message = protocol.ExpectProgressPossible()
            return self._client._process(message, retry=False)
        except ArakoonException:
            return False

    @utils.update_argspec('self')
    @_convert_exceptions
    def getKeyCount(self):
        """
        Retrieve the number of keys in the database on the master
        @rtype: int
        """
        return self._client.get_key_count()

    @utils.update_argspec('self', 'name', 'argument')
    @_convert_exceptions
    def userFunction(self, name, argument):
        """
        Call a user-defined function on the server
        @param name: Name of user function
        @type name: string
        @param argument: Optional function argument
        @type argument: string option

        @return: Function result
        @rtype: string option
        """
        return self._client.user_function(name, argument)

    @utils.update_argspec('self', 'key', 'value')
    @_convert_exceptions
    def confirm(self, key, value):
        """
        Do nothing if the value associated with the given key is this value;
        otherwise, behave as set(key,value)
        @rtype: void
        """

        self._client.confirm(key, value)

    @utils.update_argspec('self', 'key', 'vo')
    @_convert_exceptions
    def aSSert(self, key, vo):
        """
        verifies the value for key to match vo
        @type key: string
        @type vo: string_option
        @param key: the key to be verified
        @param vo: what the value should be (can be None)
        @rtype: void
        """
        self._client.assert_(key, vo)

    @utils.update_argspec('self', 'key')
    @_convert_exceptions
    def aSSert_exists(self, key):
        return self._client.assert_exists(key)

    @utils.update_argspec('self', 'beginKey', 'beginKeyIncluded', 'endKey', 'endKeyIncluded', ('maxElements', -1))
    @_convert_exceptions
    def rev_range_entries(self, beginKey, beginKeyIncluded, endKey, endKeyIncluded, maxElements=-1):
        """
        Performs a reverse range query on the store, returning a sorted (in reverse order) list of key value pairs.
        @type beginKey: string option
        @type endKey :string option
        @type beginKeyIncluded: boolean
        @type endKeyIncluded: boolean
        @type maxElements: integer
        @param beginKey: higher boundary of the requested range
        @param endKey: lower boundary of the requested range
        @param maxElements: maximum number of key-value pairs to return. Negative means 'all'. Defaults to -1
        @rtype : list of (string,string)
        """
        result = self._client.rev_range_entries(beginKey, beginKeyIncluded,
                                                endKey, endKeyIncluded,
                                                maxElements, consistency=self._determine_consistency(self._consistency))

        return result

    @utils.update_argspec('self')
    @_convert_exceptions
    def statistics(self):
        """
        @return a dictionary with some statistics about the master
        """
        return self._client.statistics()

    @utils.update_argspec('self', ('nodeId', None))
    @_convert_exceptions
    def getVersion(self, nodeId=None):
        """
        will return a tuple containing major, minor and patch level versions of the server side

        Note: The nodeId argument is currently not supported

        @type nodeId : String
        @param nodeId : id of the node you want to query (None if you want to query the master)
        @rtype : (int,int,int,string)
        @return : (major, minor, patch, info)
        """
        message = protocol.Version()
        r = self._client._process(message, node_id=nodeId)
        return r

    @utils.update_argspec('self')
    @_convert_exceptions
    def nop(self):
        """
        a nop is a paxos update that changes nothing to the database
        """
        return self._client.nop()

    @utils.update_argspec('self', 'nodeId')
    @_convert_exceptions
    def getCurrentState(self, nodeId):
        message = protocol.GetCurrentState()
        r = self._client._process(message, node_id=nodeId)
        return r

    @utils.update_argspec('self', 'key', 'wanted')
    @_convert_exceptions
    def replace(self, key, wanted):
        """
        assigns the wanted value to the key, and returns the previous assignment (if any) for that key.
        If wanted is None, the binding is deleted.
        @type key:string
        @type wanted: string option
        @rtype: string option
        @return: the previous binding (if any)
        """
        return self._client.replace(key, wanted)

    @utils.update_argspec('self', 'prefix')
    @_convert_exceptions
    def deletePrefix(self, prefix):
        """
        type prefix: string
        """
        return self._client.delete_prefix(prefix)

    @utils.update_argspec('self')
    @_convert_exceptions
    def get_txid(self):
        _res = self._client.get_tx_id()
        res = None
        if _res is consistency.CONSISTENT:
            res = Consistent()
        elif _res is consistency.INCONSISTENT:
            res = NoGuarantee()
        elif isinstance(_res, consistency.AtLeast):
            res = AtLeast(_res.i)
        else:
            raise ValueError('Unknown result: %r' % res)
        return res

    @utils.update_argspec('self', 'c')
    @_convert_exceptions
    @_validate_signature('consistency')
    def setConsistency(self, c):
        """
        Allows fine grained consistency constraints on subsequent reads
        @type c: `Consistency`
        """
        self._consistency = c

    @utils.update_argspec('self')
    @_convert_exceptions
    def allowDirtyReads(self):
        """
        Allow the client to read values from a slave or a node in limbo
        """
        self._consistency = NoGuarantee()

    def disallowDirtyReads(self):
        """
        Force the client to read from the master
        """
        self._consistency = Consistent()

    def makeSequence(self):
        return Sequence()

    def dropConnections(self):
        return self._client.drop_connections()

    _masterId = property(
        lambda self: self._client.master_id,
        lambda self, v: setattr(self._client, 'master_id', v))

    # Magic methods
    __setitem__ = set
    __getitem__ = get
    __delitem__ = delete
    __contains__ = exists


class ArakoonAdmin(ArakoonClient):
    @utils.update_argspec('self', 'node_id', 'n')
    @_convert_exceptions
    @_validate_signature('string', 'int')
    def collapse(self, node_id, n):

        """
        Tell the targeted node to collapse tlogs into a head database
        Will return the server node identifier and the version of arakoon it is running

        @type node_id  : string
        @type n : int
        @param node_id : id of targeted node
        """
        message = admin.CollapseTlogs(n)
        x = self._client._timeout
        try:
            self._client._timeout = None  # Don't timeout on this call
            self._client._process(message, node_id=node_id)
        finally:
            self._client._timeout = x
