# -*- coding: UTF-8 -*-
"""Module containing the SctFactory and SddFactory classes"""

from .payment import SctPayment
from .transaction import SctTransaction
from .entity import SctIdHolder

class SctFactory(object):
    """Factory for the SCT request mode"""

    @staticmethod
    def get_payment():
        """Returns a SctPayment object"""
        return SctPayment

    @staticmethod
    def get_transaction():
        """Returns a SctTransaction object"""
        return SctTransaction

    @staticmethod
    def get_id_holder():
        """returns an SctIdHolder object"""
        return SctIdHolder
