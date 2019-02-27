# Copyright (C) iNuron - info@openvstorage.com
# This file is part of Open vStorage. For license information, see <LICENSE.txt>

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
