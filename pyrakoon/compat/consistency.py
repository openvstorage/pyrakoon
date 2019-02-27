# Copyright (C) iNuron - info@openvstorage.com
# This file is part of Open vStorage. For license information, see <LICENSE.txt>


# Unsure why the pyrakoon.consistency is not re-used
class Consistency(object):
    pass


class Consistent(Consistency):
    def __str__(self):
        return 'Consistent'


class NoGuarantee(Consistency):
    def __str__(self):
        return 'NoGuarantee'


class AtLeast(Consistency):
    def __init__(self, i):
        self.i = i

    def __str__(self):
        return 'AtLeast(%i)' % self.i
