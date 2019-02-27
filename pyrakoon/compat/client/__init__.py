# Copyright (C) iNuron - info@openvstorage.com
# This file is part of Open vStorage. For license information, see <LICENSE.txt>

# Backward compatibility
from .socket import ArakoonSocketClient as _ArakoonClient, ArakoonSocketClientConnection as _ClientConnection
from .functional import ArakoonClient, ArakoonAdmin
