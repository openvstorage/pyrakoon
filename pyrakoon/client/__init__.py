# Copyright (C) iNuron - info@openvstorage.com
# This file is part of Open vStorage. For license information, see <LICENSE.txt>

"""
Arakoon client interface
"""

from __future__ import absolute_import

# Backwards compatibility
from .interfaces import AbstractClient, SocketClient, ClientMixin
from .errors import NotConnectedError
