# -*- coding: UTF-8 -*-
"""Module containing the SddFactory class"""

from .payment import Payment, sdd_payment_attr_dict
from .transaction import Transaction, sdd_transaction_attr_dict
from .entity import IdHolder, sdd_idholder_attr_dict
from .sct_factory import modifiy_class_from_dict

class SddFactory(object):
    """Factory for the SDD request mode."""

    @staticmethod
    def get_payment():
        """
        Returns the Payment class configured for the SDD Mode
        """

        modifiy_class_from_dict(Payment, sdd_payment_attr_dict)

        return Payment

    @staticmethod
    def get_transaction():
        """
        Returns the Transaction class configured for the SDD Mode
        """

        modifiy_class_from_dict(Transaction, sdd_transaction_attr_dict)

        return Transaction

    @staticmethod
    def get_id_holder():
        """
        Returns the IdHolder class configured for the SDD Mode
        """

        modifiy_class_from_dict(IdHolder, sdd_idholder_attr_dict)

        return IdHolder
