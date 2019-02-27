# Copyright (C) iNuron - info@openvstorage.com
# This file is part of Open vStorage. For license information, see <LICENSE.txt>

import logging
from .constants.logging import PYRAKOON_LOGGER

"""
pyrakoon, an Arakoon_ client for Python

.. _Arakoon: http://www.arakoon.org
"""

__version_info__ = 0, 0, 1
__version__ = '.'.join(str(i) for i in __version_info__)
__author__ = u'OpenvStorage'
__license__ = u'LGPL2'

__docformat__ = 'restructuredtext en'

# Setup NullHandler
logger = logging.getLogger()
logger.addHandler(logging.NullHandler())
