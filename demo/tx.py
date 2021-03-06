# Copyright (C) iNuron - info@openvstorage.com
# This file is part of Open vStorage. For license information, see <LICENSE.txt>

'''A demonstration of the Arakoon Twisted protocol'''

import logging

from twisted.internet import defer, protocol, reactor
from twisted.python import log

try:
    import pyrakoon
except ImportError:
    import sys
    import os.path as os_path

    path = os_path.abspath(os_path.join(os_path.dirname(__file__), '..'))
    if os_path.isdir(os_path.join(path, 'pyrakoon')):
        sys.path.append(path)

    del sys, os_path, path

from pyrakoon import errors, tx

# Some utility definitions
DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 4000
DEFAULT_CLUSTER_ID = 'ricky'
DEFAULT_KEY = 'demo_tx_%d'
DEFAULT_VALUE = 'demo_tx_value'

@defer.inlineCallbacks
def run(proto):
    '''Execute the actual commands

    :param proto: Connected protocol
    :type proto: `pyrakoon.tx.ArakoonProtocol`
    '''

    key = DEFAULT_KEY % 0

    master = yield proto.who_master()
    log.msg('Master is %s' % master)

    try:
        v = yield proto.get(key)
    except:
        log.err(None, 'Expected error while requesting key "%s"' % key)

    exists = yield proto.exists(key)
    log.msg('%s exists: %s' % (key, exists))

    log.msg('Set %s to %s' % (key, DEFAULT_VALUE))
    yield proto.set(key, DEFAULT_VALUE)

    exists = yield proto.exists(key)
    log.msg('%s exists: %s' % (key, exists))

    value = yield proto.get(key)
    log.msg('Value of %s is: %s' % (key, value))

    log.msg('Delete %s' % key)
    yield proto.delete(key)

    exists = yield proto.exists(key)
    log.msg('%s exists: %s' % (key, exists))

    log.msg('Generating 100 key-value pairs')
    for i in xrange(100):
        yield proto.set(DEFAULT_KEY % i, DEFAULT_VALUE)

    log.msg('Requesting range_items [%s, %s[, max 20' % \
        (DEFAULT_KEY % 10, DEFAULT_KEY % 20))
    entries = yield proto.range_entries(DEFAULT_KEY % 10, True,
        DEFAULT_KEY % 20, False, 20)

    for key, value in entries:
        log.msg('%s: %s' % (key, value))

    log.msg('Requesting %s and %s using multi_get' % \
        (DEFAULT_KEY % 10, DEFAULT_KEY % 20))
    values = yield proto.multi_get((DEFAULT_KEY % 10, DEFAULT_KEY % 20, ))
    log.msg('Result: %s' % (tuple(values), ))

    log.msg('Removing all keys matching %s' % DEFAULT_KEY[:-2])
    keys = yield proto.prefix(DEFAULT_KEY[:-2])

    for key in keys:
        yield proto.delete(key)

    # Concurrent actions
    log.msg('Performing concurrent actions')

    make_set = lambda i: \
        proto.set('multi%d' % i, 'value%d' % i).addCallback(
            lambda _: log.msg(
                'Finished set(\'multi%d\', \'value%d\')' % (i, i)))

    yield defer.DeferredList(
        [make_set(i) for i in xrange(12)],
        fireOnOneErrback=True
    )

    acts = [proto.get('multi10'),
            proto.delete('multi11'),
            proto.range_entries('multi5', True, 'multi7', False),
            proto.set('multi1', 'value2')]

    expected = ['value10',
                None,
                [('multi5', 'value5'), ('multi6', 'value6')],
                None]

    result = yield defer.DeferredList(acts, fireOnOneErrback=True)
    result = [v for (_, v) in result]

    assert result == expected

    multi1 = yield proto.get('multi1')
    assert multi1 == 'value2'

    cnt = yield proto.delete_prefix('foo_')
    log.msg('Deleted %d entries' % cnt)
    cnt = yield proto.delete_prefix('multi')
    log.msg('Deleted %d entries' % cnt)

    try:
        yield proto.assert_exists('foobar')
        assert False
    except errors.AssertionFailed:
        log.err(None, 'Expected assertion failure')

    yield proto.set('exists', '1')
    yield proto.assert_exists('exists')

    log.msg('Done')

def create_client(host, port):
    '''Create a client connection

    :param host: Host to connect to
    :type host: `str`
    :param port: Port to connect at
    :type port: `int`

    :return: A deferred which will fire once the connection is made
    :rtype: `defer.Deferred`
    '''

    client = protocol.ClientCreator(reactor,
        tx.ArakoonProtocol, DEFAULT_CLUSTER_ID)

    return client.connectTCP(host, port)

def main():
    '''Main entry point'''

    # Set up logging
    logging.basicConfig(level=logging.DEBUG)
    log.defaultObserver.stop()
    log.PythonLoggingObserver().start()

    # Set up our demo
    deferred = create_client(DEFAULT_HOST, DEFAULT_PORT)
    deferred.addCallback(run)
    deferred.addErrback(log.err)
    deferred.addBoth(lambda _: reactor.stop()) #pylint: disable-msg=E1101

    # Launch the reactor
    reactor.run() #pylint: disable-msg=E1101

if __name__ == '__main__':
    main()
