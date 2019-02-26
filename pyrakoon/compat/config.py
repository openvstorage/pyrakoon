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

import os

# This is copied from the ArakoonProtocol module
ARA_CFG_TRY_CNT = 1
ARA_CFG_CONN_TIMEOUT = 60
ARA_CFG_CONN_BACKOFF = 5
ARA_CFG_NO_MASTER_RETRY = 60


class ArakoonClientConfig(object):
    def __init__(self, clusterId, nodes, tls=False, tls_ca_cert=None, tls_cert=None):
        """
        Constructor of an ArakoonClientConfig object

        The constructor takes one optional parameter 'nodes'.
        This is a dictionary containing info on the arakoon server nodes. It contains:

          - nodeids as keys
          - ([ip], port) as values
        e.g. ::
            cfg = ArakoonClientConfig ( 'ricky',
                { "myFirstNode" : ( ["127.0.0.1"], 4000 ),
                  "mySecondNode" : (["127.0.0.1", "192.168.0.1"], 5000 ) ,
                  "myThirdNode"  : (["127.0.0.1"], 6000 )
                })

        Note: This client only supports TLSv1 when connecting to nodes,
        due to Python 2.x.

        @type clusterId: string
        @param clusterId: name of the cluster
        @type nodes: dict
        @param nodes: A dictionary containing the locations for the server nodes
        @param tls: Use a TLS connection
            If `tls_ca_cert` is given, this *must* be `True`, otherwise
            a `ValueError` will be raised
        @type tls: 'bool'
        @param tls_cert: Path of client certificate & key files
            These should be passed as a tuple. When provided, `tls_ca_cert`
            *must* be provided as well, otherwise a `ValueError` will be raised.
        @type tls_cert: '(str, str)'
        """
        self._clusterId = clusterId

        sanitize = lambda s: s if not isinstance(s, str) else [a.strip() for a in s.split(',')]
        nodes = dict((node_id, (sanitize(addr), port)) for (node_id, (addr, port)) in nodes.iteritems())

        self._nodes = nodes

        if tls_ca_cert and not tls:
            raise ValueError('tls_ca_cert passed, but tls is False')
        if tls_cert and not tls_ca_cert:
            raise ValueError('tls_cert passed, but tls_ca_cert not given')

        if tls_ca_cert is not None and not os.path.isfile(tls_ca_cert):
            raise ValueError('Invalid TLS CA cert path: %s' % tls_ca_cert)

        if tls_cert:
            cert, key = tls_cert
            if not os.path.isfile(cert):
                raise ValueError('Invalid TLS cert path: %s' % cert)
            if not os.path.isfile(key):
                raise ValueError('Invalid TLS key path: %s' % key)

        self._tls = tls
        self._tls_ca_cert = tls_ca_cert
        self._tls_cert = tls_cert

    @property
    def tls(self):
        return self._tls

    @property
    def tls_ca_cert(self):
        return self._tls_ca_cert

    @property
    def tls_cert(self):
        return self._tls_cert

    @staticmethod
    def getNoMasterRetryPeriod():
        """
        Retrieve the period messages to the master should be retried when a master re-election occurs

        This period is specified in seconds

        @rtype: integer
        @return: Returns the retry period in seconds
        """
        return ARA_CFG_NO_MASTER_RETRY

    def getNodeLocations(self, nodeId):
        return self._nodes[nodeId]

    def getNodeLocation(self, nodeId):
        """
        Retrieve location of the server node with give node identifier

        A location is a pair consisting of a hostname or ip address as first element.
        The second element of the pair is the tcp port

        @type nodeId: string
        @param nodeId: The node identifier whose location you are interested in

        @rtype: pair(string,int)
        @return: Returns a pair with the nodes hostname or ip and the tcp port, e.g. ("127.0.0.1", 4000)
        """
        ips, port = self.getNodeLocations(nodeId)
        return ips[0], port

    def getTryCount(self):
        """
        Retrieve the number of attempts a message should be tried before giving up

        Can be controlled by changing the global variable L{ARA_CFG_TRY_CNT}

        @rtype: integer
        @return: Returns the max retry count.
        """
        return ARA_CFG_TRY_CNT

    def getNodes(self):
        """
        Retrieve the dictionary with node locations
        @rtype: dict
        @return: Returns a dictionary mapping the node identifiers (string) to its location ( pair<string,integer> )
        """
        return self._nodes

    @staticmethod
    def getConnectionTimeout():
        """
        Retrieve the tcp connection timeout

        Can be controlled by changing the global variable L{ARA_CFG_CONN_TIMEOUT}

        @rtype: integer
        @return: Returns the tcp connection timeout
        """
        return ARA_CFG_CONN_TIMEOUT

    @staticmethod
    def getBackoffInterval():
        """
        Retrieves the backoff interval.

        If an attempt to send a message to the server fails,
        the client will wait a random number of seconds. The maximum wait time is n*getBackoffInterVal()
        with n being the attempt counter.
        Can be controlled by changing the global variable L{ARA_CFG_CONN_BACKOFF}

        @rtype: integer
        @return: The maximum backoff interval
        """
        return ARA_CFG_CONN_BACKOFF

    def getClusterId(self):
        return self._clusterId
