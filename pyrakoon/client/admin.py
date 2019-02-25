# This file is part of Pyrakoon, a distributed key-value store client.
#
# Copyright (C) 2013, 2014 Incubaid BVBA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Administrative client interface
"""

from pyrakoon.client import utils
from pyrakoon.protocol import admin


class ClientMixin(object):
    """
    Mixin providing client actions for node administration
    This can be mixed into any class implementing
    :class:`pyrakoon.client.AbstractClient`.
    """

    @utils.call(admin.OptimizeDB)
    def optimize_db(self):
        assert False

    @utils.call(admin.DefragDB)
    def defrag_db(self):
        assert False

    @utils.call(admin.DropMaster)
    def drop_master(self):
        assert False

    @utils.call(admin.CollapseTlogs)
    def collapse_tlogs(self):
        assert False

    @utils.call(admin.FlushStore)
    def flush_store(self):
        assert False
