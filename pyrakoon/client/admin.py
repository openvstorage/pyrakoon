# Copyright (C) iNuron - info@openvstorage.com
# This file is part of Open vStorage. For license information, see <LICENSE.txt>

"""
Administrative client interface
"""

from __future__ import absolute_import
from . import utils
from ..protocol import admin


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
