# Copyright (C) iNuron - info@openvstorage.com
# This file is part of Open vStorage. For license information, see <LICENSE.txt>

from .__hash__ import __hash__

# Used by setup.py to compute the version
__version_info__ = 0, 0, 1
# Version with the added hash
__version_tuple__ = __version_info__ + (__hash__,)
__version__ = '.'.join(str(i) for i in __version_tuple__)
