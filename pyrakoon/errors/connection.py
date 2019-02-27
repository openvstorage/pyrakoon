# Copyright (C) iNuron - info@openvstorage.com
# This file is part of Open vStorage. For license information, see <LICENSE.txt>

"""
Connection errors module
Definitions of errors that happen when connecting with the Arakoon
"""

from .base import ArakoonError


class NoHello(ArakoonError):
    """
    No *Hello* message was sent to the server after connecting
    """

    CODE = 0x0003


class NotMaster(ArakoonError):
    """
    This node is not a master node
    """

    CODE = 0x0004


class WrongCluster(ValueError, ArakoonError):
    """
    Wrong cluster ID passed
    """

    CODE = 0x0006


class GoingDown(ArakoonError):
    """
    Node is going down
    """

    CODE = 0x0010


class NoLongerMaster(ArakoonError):
    """
    No longer master
    """

    CODE = 0x0021


class MaxConnections(ArakoonError):
    """
    Connection limit reached
    """

    CODE = 0x00fe


class TooManyDeadNodes(ArakoonError):
    """
    Too many nodes in the cluster are unavailable to process the request
    """
    CODE = 0x0002
