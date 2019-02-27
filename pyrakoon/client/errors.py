# Copyright (C) iNuron - info@openvstorage.com
# This file is part of Open vStorage. For license information, see <LICENSE.txt>


class NotConnectedError(RuntimeError):
    """
    Error used when a call on a not-connected client is made
    """
