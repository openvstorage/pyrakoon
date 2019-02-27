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

from __future__ import absolute_import

import socket
import threading
from .utils import call
from .. import errors, protocol, utils


class ClientMixin(object):
    """
    Mixin providing client actions for standard cluster functionality

    This can be mixed into any class implementing :class:`AbstractClient`.
    """

    @call(protocol.Hello)
    def hello(self):
        assert False

    @call(protocol.Exists)
    def exists(self):
        assert False

    @call(protocol.WhoMaster)
    def who_master(self):
        assert False

    @call(protocol.Get)
    def get(self):
        assert False

    @call(protocol.Set)
    def set(self):
        assert False

    @call(protocol.Delete)
    def delete(self):
        assert False

    @call(protocol.PrefixKeys)
    def prefix(self):
        assert False

    @call(protocol.TestAndSet)
    def test_and_set(self):
        assert False

    @call(protocol.Sequence)
    def sequence(self):
        assert False

    @call(protocol.Range)
    def range(self):
        assert False

    @call(protocol.RangeEntries)
    def range_entries(self):
        assert False

    @call(protocol.MultiGet)
    def multi_get(self):
        assert False

    @call(protocol.MultiGetOption)
    def multi_get_option(self):
        assert False

    @call(protocol.ExpectProgressPossible)
    def expect_progress_possible(self):
        assert False

    @call(protocol.GetKeyCount)
    def get_key_count(self):
        assert False

    @call(protocol.UserFunction)
    def user_function(self):
        assert False

    @call(protocol.Confirm)
    def confirm(self):
        assert False

    @call(protocol.Assert)
    def assert_(self):
        assert False

    @call(protocol.RevRangeEntries)
    def rev_range_entries(self):
        assert False

    @call(protocol.Statistics)
    def statistics(self):
        assert False

    @call(protocol.Version)
    def version(self):
        assert False

    @call(protocol.AssertExists)
    def assert_exists(self):
        assert False

    @call(protocol.DeletePrefix)
    def delete_prefix(self):
        assert False

    @call(protocol.Replace)
    def replace(self):
        assert False

    @call(protocol.Nop)
    def nop(self):
        assert False

    @call(protocol.GetCurrentState)
    def get_current_state(self):
        assert False

    @call(protocol.GetTxID)
    def get_tx_id(self):
        assert False

    __getitem__ = get
    __setitem__ = set
    __delitem__ = delete
    __contains__ = exists


class NotConnectedError(RuntimeError):
    """
    Error used when a call on a not-connected client is made
    """


class AbstractClient(object):
    """
    Abstract base class for implementations of Arakoon clients
    """
    # Flag to denote whether the client is connected
    # If this is False, a NotConnectedError will be raised when a call is issued.
    connected = False

    def _process(self, message):
        """
        Submit a message to the server, parse the result and return it

        The given `message` should be serialized using its
        :meth:`~pyrakoon.protocol.Message.serialize` method and submitted to
        the server. Then the :meth:`~pyrakoon.protocol.Message.receive`
        coroutine of the `message` should be used to retrieve and parse a
        result from the server. The result value should be returned by this
        method, or any exceptions should be rethrown if caught.

        :param message: Message to handle
        :type message: :class:`pyrakoon.protocol.Message`

        :return: Server result value
        :rtype: :obj:`object`

        :see: :func:`pyrakoon.utils.process_blocking`
        """

        raise NotImplementedError()


class SocketClient(AbstractClient):
    """
    Arakoon client using TCP to contact a cluster node
    :warning: Due to the lack of resource and exception management, this is not intended to be used in real-world code.
    """
    AFTER_IDLE_SEC = 20
    INTERVAL_SEC = 20
    MAX_FAILS = 3

    def __init__(self, address, cluster_id):
        """
        :param address: Node address (host & port)
        :type address: (str, int)
        :param cluster_id: Identifier of the cluster
        :type cluster_id: str
        """
        super(SocketClient, self).__init__()

        self._lock = threading.Lock()

        self._socket = None
        self._address = address
        self._cluster_id = cluster_id

    def connect(self):
        """
        Create client socket and connect to server
        """
        self._socket = socket.create_connection(self._address)

        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, self.AFTER_IDLE_SEC)
        self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, self.INTERVAL_SEC)
        self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, self.MAX_FAILS)

        prologue = protocol.build_prologue(self._cluster_id)
        self._socket.sendall(prologue)

    @property
    def connected(self):
        """
        Check whether a connection is available
        """
        return self._socket is not None

    def _process(self, message):
        self._lock.acquire()
        try:
            for part in message.serialize():
                self._socket.sendall(part)

            return utils.read_blocking(message.receive(), self._socket.recv)
        except Exception as exc:
            if not isinstance(exc, errors.ArakoonError):
                try:
                    if self._socket:
                        self._socket.close()
                finally:
                    self._socket = None

            raise
        finally:
            self._lock.release()
