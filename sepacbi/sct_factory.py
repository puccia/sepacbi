# -*- coding: UTF-8 -*-
"""Module containing the SctFactory class"""


from .payment import Payment, sct_payment_attr_dict
from .transaction import Transaction, sct_transaction_attr_dict
from .entity import IdHolder, sct_idholder_attr_dict

class SctFactory(object):
    """Factory for the SCT request mode"""

    @staticmethod
    def get_payment():
        """Returns the Payment class"""

        setattr(Payment, 'allowed_args', sct_payment_attr_dict['allowed_args'])
        setattr(Payment, 'envelope', False)

        setattr(Payment, 'get_initiator', sct_payment_attr_dict['get_initiator'])

        setattr(Payment, 'add_transaction', sct_payment_attr_dict['add_transaction'])

        setattr(Payment, 'perform_checks', sct_payment_attr_dict['perform_checks'])

        setattr(Payment, 'get_xml_root', sct_payment_attr_dict['get_xml_root'])

        setattr(Payment, 'emit_tag', sct_payment_attr_dict['emit_tag'])

        setattr(Payment, 'cbi_text', sct_payment_attr_dict['cbi_text'])

        return Payment

    @staticmethod
    def get_transaction():
        """Returns a STransaction object"""

        setattr(Transaction, 'allowed_args', sct_transaction_attr_dict['allowed_args'])

        setattr(Transaction, 'purpose', 'SUPP')

        setattr(Transaction, 'perform_checks', sct_transaction_attr_dict['perform_checks'])

        setattr(Transaction, 'emit_tag', sct_transaction_attr_dict['emit_tag'])

        setattr(Transaction, 'cbi_records', sct_transaction_attr_dict['cbi_records'])

        setattr(Transaction, 'rmtinfo_record', classmethod(sct_transaction_attr_dict['rmtinfo_record']))

        setattr(Transaction, 'rmt_cbi_records', sct_transaction_attr_dict['rmt_cbi_records'])

        return Transaction

    @staticmethod
    def get_id_holder():
        """returns an IdHolder object"""

        setattr(IdHolder, 'allowed_args', sct_idholder_attr_dict['allowed_args'])

        setattr(IdHolder, 'perform_checks', sct_idholder_attr_dict['perform_checks'])

        setattr(IdHolder, 'emit_tag', sct_idholder_attr_dict['emit_tag'])

        return IdHolder
