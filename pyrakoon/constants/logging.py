# Copyright (C) iNuron - info@openvstorage.com
# This file is part of Open vStorage. For license information, see <LICENSE.txt>

# Pyrakoon isn't packaged to be deployed anywhere. Set the logger to a fixed name
PYRAKOON_LOGGER = 'pyrakoon'

PYRAKOON_COMPAT_LOGGER = '{0}.compat'.format(PYRAKOON_LOGGER)
PYRAKOON_UTILS_LOGGER = '{0}.utils'.format(PYRAKOON_LOGGER)
