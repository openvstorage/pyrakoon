# This file is part of Pyrakoon, a distributed key-value store client.
#
# Copyright (C) 2010 Incubaid BVBA
#
# Licensees holding a valid Incubaid license may use this file in
# accordance with Incubaid's Arakoon commercial license agreement. For
# more information on how to enter into this agreement, please contact
# Incubaid (contact details can be found on www.arakoon.org/licensing).
#
# Alternatively, this file may be redistributed and/or modified under
# the terms of the GNU Affero General Public License version 3, as
# published by the Free Software Foundation. Under this license, this
# file is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.
#
# See the GNU Affero General Public License for more details.
# You should have received a copy of the
# GNU Affero General Public License along with this program (file "COPYING").
# If not, see <http://www.gnu.org/licenses/>.

'''Tests for code in `pyrakoon.nursery`'''

import time
import logging
import unittest
import subprocess

from pyrakoon import compat, nursery, test

LOGGER = logging.getLogger(__name__)

CONFIG_TEMPLATE = '''
[global]
cluster = arakoon_0
cluster_id = %(CLUSTER_ID)s

[nursery]
cluster = arakoon_0
cluster_id = %(CLUSTER_ID)s

[arakoon_0]
ip = 127.0.0.1
client_port = %(CLIENT_PORT)d
messaging_port = %(MESSAGING_PORT)d
home = %(HOME)s
log_dir = %(LOG_DIR)s
log_level = debug
'''

class TestNurseryClient(unittest.TestCase, test.ArakoonEnvironmentMixin):
    '''Test the compatibility client against a real Arakoon server'''

    def setUp(self):
        client_config, config_path, base = self.setUpArakoon(
            'pyrakoon_test_nursery', CONFIG_TEMPLATE)
        self.client_config = compat.ArakoonClientConfig(*client_config)

        # Give server some time to get up
        ok = False
        for _ in xrange(5):
            LOGGER.info('Attempting hello call')
            try:
                client = self._create_client()
                client.hello('testsuite', 'pyrakoon_test')
                client._client.drop_connections()
            except:
                LOGGER.info('Call failed, sleeping')
                time.sleep(1)
            else:
                LOGGER.debug('Call succeeded')
                ok = True
                break

        if not ok:
            raise RuntimeError('Unable to start Arakoon server')

        subprocess.check_call([
            'arakoon', '-config', config_path, '--nursery-init',
            client_config[0]
        ], close_fds=True, cwd=base)

        time.sleep(5)

    def tearDown(self):
        self.tearDownArakoon()

    def _create_client(self):
        client = compat.ArakoonClient(self.client_config)
        client.hello('testsuite', self.client_config.clusterId)
        return client

    def _create_nursery_client(self):
        def morph(name, cluster_info):
            cluster_info2 = {}

            for node_id, (ips, port) in cluster_info.iteritems():
                cluster_info2[node_id] = (ips[0], port)

            return compat.ArakoonClient(
                compat.ArakoonClientConfig(name, cluster_info2))

        return nursery.NurseryClient(self._create_client()._client._process,
            morph)

    def test_scenario(self):
        client = self._create_nursery_client()

        client.set('key', 'value')
        self.assertEqual(client.get('key'), 'value')
        client.delete('key')