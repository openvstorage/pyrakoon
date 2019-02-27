# Copyright (C) iNuron - info@openvstorage.com
# This file is part of Open vStorage. For license information, see <LICENSE.txt>

"""
Client request result consistency definitions
"""


class Consistency(object):
    """
    Abstract base class for consistency definition types
    """


class Consistent(Consistency):
    """
    Representation of the 'Consistent' consistency policy
    """

    def __repr__(self):
        return 'CONSISTENT'


class Inconsistent(Consistency):
    """
    Representation of the 'Inconsistent' consistency policy
    """

    def __repr__(self):
        return 'INCONSISTENT'


class AtLeast(Consistency):
    """
    Representation of an 'at least' consistency policy
    """

    __slots__ = '_i',

    def __init__(self, i):
        """
        Create an 'at least' consistency policy definition
        :param i: Minimal required `i` value. I representing the Paxos value.
        Guarantee that the value retrieved is at least on the 'i' value
        :type i: `int`
        """
        self._i = i

    def __repr__(self):
        return 'AtLeast(%d)' % self.i

    @property
    def i(self):
        """
        Minimal \'i\'
        :return:
        """
        return self._i


# Instances
# The `CONSISTENT` consistency policy
CONSISTENT = Consistent()
# The `INCONSISTENT` consistency policy
INCONSISTENT = Inconsistent()

# Removal of the classes. I don't know why though. Supposedly to only have one instance of it laying around
del Consistent
del Inconsistent
