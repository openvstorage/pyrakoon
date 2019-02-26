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
Arakoon socket client
Communicates to the Arakoon server with sockets
"""

from __future__ import absolute_import

import ssl
import time
import random
import select
import socket
import logging
import threading

from ..config import ArakoonClientConfig
from ..errors import ArakoonNotConnected, ArakoonNoMaster, ArakoonSockReadNoBytes,\
    ArakoonSockNotReadable, ArakoonSockRecvError, ArakoonSockRecvClosed, ArakoonSockSendError
from ... import utils, protocol, errors, client
from ...constants.logging import PYRAKOON_COMPAT_LOGGER

logger = logging.getLogger(PYRAKOON_COMPAT_LOGGER)


class ArakoonSocketClient(client.AbstractClient, client.ClientMixin):
    def __init__(self, config, timeout=0, noMasterTimeout=0):
        self._config = config
        self.master_id = None

        self._lock = threading.RLock()
        self._connections = dict()
        self._timeout = timeout
        if (isinstance(timeout, (int, float)) and timeout > 0) or timeout is None:
            self._master_timeout = noMasterTimeout
        else:
            self._master_timeout = ArakoonClientConfig.getNoMasterRetryPeriod()

    @property
    def connected(self):
        return True

    def _process(self, message, node_id=None, retry=True):

        bytes_ = ''.join(message.serialize())

        self._lock.acquire()

        try:
            start = time.time()
            tryCount = 0.0
            backoffPeriod = 0.2
            deadline = start + self._master_timeout
            while True:
                try:
                    # Send on wire
                    if node_id is None:
                        connection = self._send_to_master(bytes_)
                    else:
                        connection = self._send_message(node_id, bytes_)
                    return utils.read_blocking(message.receive(),
                                               connection.read)
                except (errors.NotMaster,
                        ArakoonNoMaster,
                        ArakoonNotConnected,
                        ArakoonSockReadNoBytes):
                    self.master_id = None
                    self.drop_connections()

                    sleepPeriod = backoffPeriod * tryCount
                    if retry and time.time() + sleepPeriod <= deadline:
                        tryCount += 1.0
                        logger.warning('Master not found, retrying in %0.2f seconds' % sleepPeriod)
                        time.sleep(sleepPeriod)
                    else:
                        raise

        finally:
            self._lock.release()

    def _send_message(self, node_id, data, count=-1):
        result = None

        if count < 0:
            count = self._config.getTryCount()

        last_exception = None
        for i in xrange(count):
            if i > 0:
                max_sleep = i * ArakoonClientConfig.getBackoffInterval()
                time.sleep(random.randint(0, max_sleep))

            self._lock.acquire()
            try:
                connection = self._get_connection(node_id)
                connection.send(data)

                result = connection
                break
            except Exception as e:
                last_exception = e
                logger.exception('%s : Message exchange with node %s failed',
                                 e, node_id)
                try:
                    self._connections.pop(node_id).close()
                finally:
                    self.master_id = None
            finally:
                self._lock.release()

        if not result:
            raise last_exception

        return result

    def _send_to_master(self, data):
        self.determine_master()

        connection = self._send_message(self.master_id, data)

        return connection

    def drop_connections(self):
        for key in tuple(self._connections.iterkeys()):
            self._connections.pop(key).close()

    def determine_master(self):
        if self.master_id is None:
            node_ids = self._config.getNodes().keys()
            random.shuffle(node_ids)
            while self.master_id is None and node_ids:
                node = node_ids.pop()
                try:
                    self.master_id = self._get_master_id_from_node(node)
                    tmp_master = self.master_id
                    try:
                        if self.master_id is not None:
                            if self.master_id != node and not self._validate_master_id(self.master_id):
                                self.master_id = None
                                logger.warning(
                                    'Node "%s" thinks the master is "%s", but actually it isn\'t',
                                    node, tmp_master)
                    except Exception as e:
                        logger.exception(
                            '%s: Unable to validate master on node %s', e, tmp_master)
                        self.master_id = None

                except Exception as e:
                    logger.exception(
                        '%s: Unable to query node "%s" to look up master', e, node)

        if not self.master_id:
            logger.error('Unable to determine master node')
            raise ArakoonNoMaster

    def _get_master_id_from_node(self, node_id):
        command = protocol.WhoMaster()
        data = ''.join(command.serialize())

        connection = self._send_message(node_id, data)

        receiver = command.receive()
        return utils.read_blocking(receiver, connection.read)

    def _validate_master_id(self, master_id):
        if not master_id:
            return False

        other_master_id = self._get_master_id_from_node(master_id)

        return other_master_id == master_id

    def _get_connection(self, node_id):
        connection = None

        if node_id in self._connections:
            connection = self._connections[node_id]

        if not connection:
            node_location = self._config.getNodeLocation(node_id)
            connection = ArakoonSocketClientConnection(node_location,
                                                       self._config.getClusterId(),
                                                       self._config.tls, self._config.tls_ca_cert,
                                                       self._config.tls_cert,
                                                       self._timeout)
            connection.connect()

            self._connections[node_id] = connection

        return connection


class ArakoonSocketClientConnection(object):
    def __init__(self, address, cluster_id,
                 tls, tls_ca_cert, tls_cert,
                 timeout=0):
        self._address = address
        self._connected = False
        self._socket = None
        self._cluster_id = cluster_id
        self._tls = tls
        self._tls_ca_cert = tls_ca_cert
        self._tls_cert = tls_cert
        if (isinstance(timeout, (int, float)) and timeout > 0) or timeout is None:
            self._timeout = timeout
        else:
            self._timeout = ArakoonClientConfig.getConnectionTimeout()

    def connect(self):
        if self._socket:
            self._socket.close()
            self._socket = None

        try:
            self._socket = socket.create_connection(self._address, self._timeout)

            after_idle_sec = 20
            interval_sec = 20
            max_fails = 3
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, after_idle_sec)
            self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, interval_sec)
            self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, max_fails)

            if self._tls:
                kwargs = {
                    'ssl_version': ssl.PROTOCOL_TLSv1,
                    'cert_reqs': ssl.CERT_OPTIONAL,
                    'do_handshake_on_onnect': True
                }

                if self._tls_ca_cert:
                    kwargs['cert_reqs'] = ssl.CERT_REQUIRED
                    kwargs['ca_certs'] = self._tls_ca_cert

                if self._tls_cert:
                    cert, key = self._tls_cert
                    kwargs['keyfile'] = key
                    kwargs['certfile'] = cert

                self._socket = ssl.wap_socket(self._socket, **kwargs)

            data = protocol.build_prologue(self._cluster_id)
            self._socket.sendall(data)

            self._connected = True
        except Exception as e:
            logger.exception('%s: Unable to connect to %s', e, self._address)

    def send(self, data):
        if not self._connected:
            self.connect()

            if not self._connected:
                raise ArakoonNotConnected(self._address)

        try:
            self._socket.sendall(data)
        except Exception as e:
            logger.exception('%s:Error while sending data to %s', e, self._address)
            self.close()
            raise ArakoonSockSendError()

    def close(self):
        if self._connected and self._socket:
            try:
                self._socket.close()
            except Exception as e:
                logger.exception('%s: Error while closing socket to %s',
                                 e,
                                 self._address)
            finally:
                self._connected = False

    def read(self, count):
        if not self._connected:
            raise ArakoonSockRecvClosed()

        bytes_remaining = count
        result = []

        if isinstance(self._socket, ssl.SSLSocket):
            pending = self._socket.pending()
            if pending > 0:
                tmp = self._socket.recv(min(bytes_remaining, pending))
                result.append(tmp)
                bytes_remaining = bytes_remaining - len(tmp)

        while bytes_remaining > 0:
            reads, _, _ = select.select([self._socket], [], [], self._timeout)

            if self._socket in reads:
                try:
                    data = self._socket.recv(bytes_remaining)
                except Exception as e:
                    logger.exception('%s: Error while reading socket', e)
                    self._connected = False

                    raise ArakoonSockRecvError()

                if len(data) == 0:
                    try:
                        self.close()
                    except Exception as e:
                        logger.exception('%s: Error while closing socket', e)

                    self._connected = False

                    raise ArakoonSockReadNoBytes()

                result.append(data)
                bytes_remaining -= len(data)

            else:
                try:
                    self.close()
                except Exception as e:
                    logger.exception('%s: Error while closing socket', e)
                finally:
                    self._connnected = False

                raise ArakoonSockNotReadable()

        return ''.join(result)
