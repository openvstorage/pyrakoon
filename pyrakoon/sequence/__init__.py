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

from .steps import Step, Step, Set, Delete, Assert, AssertExists, Replace, DeletePrefix
from .. import protocol


class Sequence(Step):
    """
    "Sequence" operation
    This is a container for a list of other operations.
    """
    TAG = 5
    ARGS = ()

    def __init__(self, steps):
        super(Sequence, self).__init__()

        self._steps = steps

    @property
    def steps(self):
        # type: () -> Iterator[Step]
        """
        Sequence steps
        :return: Iterable of of class step
        :rtype: Iterator[Step]
        """
        return self._steps

    def serialize(self):
        for bytes_ in protocol.UINT32.serialize(self.TAG):
            yield bytes_

        for bytes_ in protocol.UINT32.serialize(len(self.steps)):
            yield bytes_

        for step in self.steps:
            for bytes_ in step.serialize():
                yield bytes_
