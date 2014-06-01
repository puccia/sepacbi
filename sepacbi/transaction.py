#!/usr/bin/python

"""
This module deals with the information related to a single transaction.
"""

__copyright__ = 'Copyright (c) 2014 Emanuele Pucciarelli, C.O.R.P. s.n.c.'
__license__ = '3-clause BSD'

from lxml import etree
from decimal import Decimal
from .util import AttributeCarrier
from .bank import Bank
from .account import Account
import sys

if sys.version_info[0] >= 3:
    # pylint: disable=redefined-builtin
    # pylint: disable=invalid-name
    basestring = str


class MissingBICError(Exception):
    """
    Raised when a BIC code is needed but not specified.
    """

class Transaction(AttributeCarrier):
    """
    Transaction describes a single credit transfer from the debtor's account
    (specified in the global payment data) to a creditor account.
    """
    # pylint: disable=no-member

    allowed_args = (
        'tx_id', 'eeid', 'category', 'rmtinfo', 'amount',
        'ultimate_debtor', 'bic', 'account', 'creditor', 'ultimate_creditor',
        'docs', 'purpose', 'payment_seq', 'payment_id',
        'register_eeid_function')

    def __init__(self, *args, **kwargs):
        self.purpose = 'SUPP'
        self.eeid_registered = False
        super(Transaction, self).__init__(*args, **kwargs)

    def gen_id(self):
        "Generate a sequential ID, if not supplied, for the `InstrId` element."
        self.tx_id = str(self.payment_seq)

    def gen_eeid(self):
        "Generate a unique ID for the `EndToEndId` element."
        self.eeid = '%s-%06d' % (self.payment_id, self.payment_seq)

    def perform_checks(self):
        "Check lengths and types for the attributes."
        # pylint: disable=access-member-before-definition
        # pylint: disable=attribute-defined-outside-init
        if not hasattr(self, 'tx_id'):
            self.gen_id()
        self.max_length('tx_id', 35)

        if not hasattr(self, 'eeid'):
            self.gen_eeid()
        self.max_length('eeid', 35)
        if not self.eeid_registered:
            self.register_eeid_function(self.eeid)
            self.eeid_registered = True

        self.length('purpose', 4)
        if not hasattr(self, 'category'):
            self.category = self.purpose

        self.length('category', 4)

        if not isinstance(self.amount, Decimal):
            self.amount = Decimal(str(self.amount)).quantize(Decimal('.01'))
        if isinstance(self.account, basestring):
            self.account = Account(iban=self.account)
        if self.account.is_foreign():
            if not hasattr(self, 'bic'):
                raise MissingBICError
            bic_length = len(self.bic)
            assert bic_length in (8, 11)

        if hasattr(self, 'rmtinfo'):
            assert not hasattr(self, 'docs')
            assert len(self.rmtinfo) <= 140

        if hasattr(self, 'docs'):
            for item in self.docs:
                assert hasattr(item, '__str__')

        assert hasattr(self, 'docs') or hasattr(self, 'rmtinfo')

    def emit_tag(self):
        """
        Returns the XML tag for the transaction.
        """
        root = etree.Element('CdtTrfTxInf')
        pmtid = etree.SubElement(root, 'PmtId')
        etree.SubElement(pmtid, 'InstrId').text = self.tx_id
        etree.SubElement(pmtid, 'EndToEndId').text = self.eeid
        info = etree.SubElement(root, 'PmtTpInf')
        purp = etree.SubElement(info, 'CtgyPurp')
        etree.SubElement(purp, 'Cd').text = self.category
        amt = etree.SubElement(root, 'Amt')
        etree.SubElement(
            amt, 'InstdAmt', attrib={'Ccy': 'EUR'}).text = str(self.amount)
        if hasattr(self, 'ultimate_debtor'):
            root.append(self.ultimate_debtor.__tag__('UltmtDbtr'))
        if self.account.is_foreign():
            agt = etree.SubElement(root, 'CdtrAgt')
            agt.append(Bank(bic=self.bic).__tag__())
        root.append(self.creditor.__tag__('Cdtr'))
        root.append(self.account.__tag__('CdtrAcct'))
        if hasattr(self, 'ultimate_creditor'):
            root.append(self.ultimate_creditor.__tag__('UltmtCdtr'))
        rmtinf = etree.SubElement(root, 'RmtInf')
        if hasattr(self, 'rmtinfo'):
            etree.SubElement(rmtinf, 'Ustrd').text = self.rmtinfo
        else:
            etree.SubElement(rmtinf, 'Ustrd').text = ''.join(
                [str(doc) for doc in self.docs])
        return root
