# Copyright (C) iNuron - info@openvstorage.com
# This file is part of Open vStorage. For license information, see <LICENSE.txt>

from __future__ import absolute_import

from .steps import Step, Step, Set, Delete, Assert, AssertExists, Replace, DeletePrefix, AssertRange
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
