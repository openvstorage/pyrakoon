# Copyright (C) iNuron - info@openvstorage.com
# This file is part of Open vStorage. For license information, see <LICENSE.txt>

# This is mostly a copy from the ArakoonExceptions module, with some cosmetic
# changes and some code simplifications


class ArakoonException(Exception):
    _msg = None

    def __init__(self, msg=''):
        if self._msg is not None and msg == '':
            msg = self._msg

        super(ArakoonException, self).__init__(msg)


class ArakoonNotFound(ArakoonException, KeyError):
    _msg = 'Key not found'


class ArakoonUnknownNode(ArakoonException):
    _msgF = 'Unknown node identifier: %s'

    def __init__(self, nodeId):
        self._msg = ArakoonUnknownNode._msgF % nodeId
        super(ArakoonUnknownNode, self).__init__(self._msg)


class ArakoonNodeNotLocal(ArakoonException):
    _msgF = "Unknown node identifier: %s"

    def __init__(self, nodeId):
        self._msg = ArakoonNodeNotLocal._msgF % nodeId
        super(ArakoonNodeNotLocal, self).__init__(self._msg)


class ArakoonNotConnected(ArakoonException):
    _msgF = 'No connection available to node at \'%s:%s\''

    def __init__(self, location):
        self._msg = ArakoonNotConnected._msgF % location
        super(ArakoonNotConnected, self).__init__(self._msg)


class ArakoonNoMaster(ArakoonException):
    _msg = 'Could not determine the Arakoon master node'


class ArakoonNoMasterResult(ArakoonException):
    _msg = 'Master could not be contacted.'


class ArakoonNodeNotMaster(ArakoonException):
    _msg = 'Cannot perform operation on non-master node'


class ArakoonNodeNoLongerMaster(ArakoonException):
    _msg = 'Operation might or might not have been performed on node which is no longer master'


class ArakoonGoingDown(ArakoonException):
    _msg = 'Server is going down'


class ArakoonSocketException(ArakoonException):
    pass


class ArakoonSockReadNoBytes(ArakoonException):
    _msg = 'Could not read a single byte from the socket. Aborting.'


class ArakoonSockNotReadable(ArakoonSocketException):
    _msg = 'Socket is not readable. Aborting.'


class ArakoonSockRecvError(ArakoonSocketException):
    _msg = 'Error while receiving data from socket'


class ArakoonSockRecvClosed(ArakoonSocketException):
    _msg = 'Cannot receive on a not-connected socket'


class ArakoonSockSendError(ArakoonSocketException):
    _msg = 'Error while sending data on socket'


class ArakoonInvalidArguments(ArakoonException, TypeError):
    _msgF = 'Invalid argument(s) for %s: %s'

    def __init__(self, fun_name, invalid_args):
        # Allow passing single argument, used by _convert_exception
        msg = fun_name
        if invalid_args:
            error_string = ', '.join('%s=%s' % arg for arg in invalid_args)
            self._msg = ArakoonInvalidArguments._msgF % (fun_name, error_string)
            super(ArakoonInvalidArguments, self).__init__(self._msg)
            return

        super(ArakoonInvalidArguments, self).__init__(msg)


class ArakoonAssertionFailed(ArakoonException):
    _msg = 'Assert did not yield expected result'


class ArakoonBadInput(ArakoonException):
    _msg = "Bad input for arakoon operation"

