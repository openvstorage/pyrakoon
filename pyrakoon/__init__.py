# Copyright (C) iNuron - info@openvstorage.com
# This file is part of Open vStorage. For license information, see <LICENSE.txt>

import logging
from .constants.logging import PYRAKOON_LOGGER
from .__version__ import __version__, __version_tuple__
from .__author__ import __author__
from .__license__ import __license__

"""
pyrakoon, an Arakoon_ client for Python

.. _Arakoon: http://www.arakoon.org
"""

__docformat__ = 'restructuredtext en'

# Setup NullHandler
logger = logging.getLogger()
logger.addHandler(logging.NullHandler())
