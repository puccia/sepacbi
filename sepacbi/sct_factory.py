# -*- coding: UTF-8 -*-
"""
Module containing the SctFactory class.
"""


from .payment import Payment, sct_payment_attr_dict
from .transaction import Transaction, sct_transaction_attr_dict
from .entity import IdHolder, sct_idholder_attr_dict

class SctFactory(object):
    """
    Factory for the SCT request mode.
    """

    @staticmethod
    def get_payment():
        """
        Returns the Payment class configured for the SCT Mode.
        """

        modifiy_class_from_dict(Payment, sct_payment_attr_dict)

        return Payment

    @staticmethod
    def get_transaction():
        """
        Returns the Transaction class configured for the SCT Mode.
        """

        modifiy_class_from_dict(Transaction, sct_transaction_attr_dict)

        return Transaction

    @staticmethod
    def get_id_holder():
        """
        Returns the IdHolder class configured for the SCT Mode.
        """

        modifiy_class_from_dict(IdHolder, sct_idholder_attr_dict)

        return IdHolder

def modifiy_class_from_dict(mod_class, attr_dict):
    """
    Set attributes and methods to a class from a dictionary.
    """
    list([setattr(mod_class, x, attr_dict[x]) for x in \
        list(attr_dict.keys())])
