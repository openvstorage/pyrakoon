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
Misc message module
Contains varias messages used to contact the Arakoon
"""

from __future__ import absolute_import

from ... import utils
from .base import Message
from ..types import Option, Product, STRING, UINT64, INT32, BOOL, UNIT, STATISTICS, CONSISTENCY


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

    @property
    def client_id(self):
        return self._client_id

    @property
    def cluster_id(self):
        return self._cluster_id


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

    @property
    def function(self):
        return self._function

    @property
    def argument(self):
        return self._argument


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
