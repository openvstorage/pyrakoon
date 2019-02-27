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

"""
Compat utils module
Contains utility functions
"""

from __future__ import absolute_import

import inspect
import logging
import functools
from .consistency import Consistency
from .errors import ArakoonException, ArakoonNotFound, ArakoonNodeNotMaster, ArakoonNodeNoLongerMaster, ArakoonGoingDown,\
    ArakoonInvalidArguments, ArakoonAssertionFailed, ArakoonBadInput
from .. import errors
from ..constants.logging import PYRAKOON_COMPAT_LOGGER


logger = logging.getLogger(PYRAKOON_COMPAT_LOGGER)
PARAM_NATIVE_TYPE_MAPPING = {
    'int': int,
    'string': str,
    'bool': bool,
}


def validate(arg, arg_type):
    # Avoid circular import
    from .sequence import Sequence

    # type: (any, any) -> bool
    if arg_type in PARAM_NATIVE_TYPE_MAPPING:
        r = isinstance(arg, PARAM_NATIVE_TYPE_MAPPING[arg_type])
    elif arg_type == 'string_option':
        r = isinstance(arg, str) or arg is None
    elif arg_type == 'string_list':
        r = all(isinstance(value, str) for value in arg)
    elif arg_type == 'sequence':
        r = isinstance(arg, Sequence)
    elif arg_type == 'consistency_option':
        r = isinstance(arg, Consistency) or arg is None
    elif arg_type == 'consistency':
        r = isinstance(arg, Consistency)
    else:
        raise RuntimeError('Invalid argument type supplied: %s' % arg_type)
    return r


def validate_signature(*signature_args):
    """
    Validate signature decorator.
    Validates if the arguments supplied match the signature of the function
    """
    def validate_signature_wrap(fun):

        @functools.wraps(fun)
        def validate_signature_inner(*args, **kwargs):
            _ = args

            new_args = [None] * (len(signature_args) + 1)
            missing_args = inspect.getargs(fun.func_code).args

            for (idx, missing_arg) in enumerate(missing_args):
                if missing_arg in kwargs:
                    new_args[idx] = kwargs[missing_arg]
                    del kwargs[missing_arg]

            if kwargs:
                raise ArakoonInvalidArguments(fun.func_name,
                                              list(kwargs.iteritems()))

            i = 0
            error_key_values = []

            for arg, arg_type in zip(new_args[1:], signature_args):
                if not validate(arg, arg_type):
                    error_key_values.append(
                        (fun.func_code.co_varnames[i + 1], new_args[i]))
                i += 1

            if error_key_values:
                raise ArakoonInvalidArguments(fun.func_name, error_key_values)

            return fun(*new_args)
        return validate_signature_inner
    return validate_signature_wrap


def _convert_exception(exception):
    # type: (Exception) -> Exception
    """
    Convert an exception to a suitable `ArakoonException`

    This function converts several types of `errors.ArakoonError` instances
    into `ArakoonException` instances, for compatibility reasons.

    If no suitable conversion can be performed, the original exception is
    returned.

    :param exception: Exception to convert
    :type exception: Exception
    :return: New exception
    :rtype: Exception
    """
    converted_exception = None
    if isinstance(exception, errors.NotFound):
        converted_exception = ArakoonNotFound(exception.message)
    elif isinstance(exception, errors.NotMaster):
        converted_exception = ArakoonNodeNotMaster(exception.message)
    elif isinstance(exception, (TypeError, ValueError)):
        converted_exception = ArakoonInvalidArguments(exception.message, None)
        logger.exception(exception)
    elif isinstance(exception, errors.AssertionFailed):
        converted_exception = ArakoonAssertionFailed(exception.message)
    elif isinstance(exception, errors.BadInput):
        converted_exception = ArakoonBadInput(exception.message)
    elif isinstance(exception, errors.ArakoonError):
        converted_exception = ArakoonException(exception.message)
    elif isinstance(exception, errors.NoLongerMaster):
        converted_exception = ArakoonNodeNoLongerMaster(exception.message)
    elif isinstance(exception, errors.GoingDown):
        converted_exception = ArakoonGoingDown(exception.message)
    elif isinstance(exception, errors.ReadOnly):
        converted_exception = ArakoonException(exception.message)

    if converted_exception:
        converted_exception.inner = exception
        return converted_exception
    return exception


def convert_exceptions(fun):
    """
    Wrap a function to convert `pyrakoon` exceptions into suitable
    `ArakoonException` instances
    """

    @functools.wraps(fun)
    def convert_exceptions_inner(*args, **kwargs):
        try:
            return fun(*args, **kwargs)
        except Exception, exc:
            new_exception = _convert_exception(exc)

            if new_exception is exc:
                raise

            raise new_exception

    return convert_exceptions_inner
