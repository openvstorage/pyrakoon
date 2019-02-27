# Copyright (C) 2019 iNuron NV
#
# This file is part of Open vStorage Open Source Edition (OSE),
# as available from
#
#      http://www.openvstorage.org and
#      http://www.openvstorage.com.
#
# This file is free software; you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License v3 (GNU AGPLv3)
# as published by the Free Software Foundation, in version 3 as it comes
# in the LICENSE.txt file of the Open vStorage OSE distribution.
#
# Open vStorage is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY of any kind.

from __future__ import absolute_import

# When rewriting this, I don't know why the consistency classes were created once more but I did not want to break things
# Backwards compatibility
from .config import ArakoonClientConfig, ARA_CFG_CONN_BACKOFF, ARA_CFG_CONN_TIMEOUT, ARA_CFG_NO_MASTER_RETRY, ARA_CFG_TRY_CNT
from .consistency import Consistency, Consistent, AtLeast, NoGuarantee
from .errors import ArakoonException, ArakoonNotFound, ArakoonUnknownNode, ArakoonNodeNotLocal, ArakoonNotConnected,\
    ArakoonNoMaster, ArakoonNoMasterResult, ArakoonNodeNotMaster, ArakoonNodeNoLongerMaster, ArakoonGoingDown,\
    ArakoonSocketException, ArakoonSockReadNoBytes, ArakoonSockNotReadable, ArakoonSockRecvError, ArakoonSockRecvClosed,\
    ArakoonSockSendError, ArakoonInvalidArguments, ArakoonAssertionFailed, ArakoonBadInput
from .sequence import Update, Set, Delete, DeletePrefix, Assert, AssertExists, Replace, Sequence
from .utils import convert_exceptions as _convert_exceptions, validate_signature as _validate_signature
from .client import ArakoonAdmin, ArakoonClient, _ArakoonClient, _ClientConnection
