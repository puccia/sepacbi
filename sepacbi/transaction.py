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
from .cbibon_dom import TransferInfo, PayerIBANInfo, PayeeIBANInfo, \
    PayerInfo, PayeeInfo, PayeeAddress, PurposeInfo, StatusRequest
import sys

if sys.version_info[0] >= 3:
    # pylint: disable=redefined-builtin
    # pylint: disable=invalid-name
    basestring = str


# Categories to CBI purpose mapping:

CATEGORY_CBI_MAP = {
    'SALA': '27020',
    'PENS': '27010',
    'SUPP': '48000',
}


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
        'register_eeid_function', 'payment', 'cbi_purpose')

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

    def cbi_records(self, prog=None):
        if self.account.is_foreign():
            raise Exception('Cannot use a foreign IBAN with CBI text files')

        records = []

        xinfo = TransferInfo()
        xinfo.prog_number = prog
        if hasattr(self.payment, 'execution_date'):
            xinfo.execution_date = self.payment.execution_date
        # TODO: allow generic codes for salaries, pensions
        if hasattr(self, 'cbi_purpose'):
            xinfo.purpose = self.cbi_purpose
        elif hasattr(self, 'category'):
            if self.category in CATEGORY_CBI_MAP:
                xinfo.purpose = CATEGORY_CBI_MAP[self.category]
            else:
                raise Exception('Cannot map cateogry %r; please supply the '
                                '\'cbi_purpose\' attribute' % self.category)
        else:
            xinfo.purpose = '48000'

        xinfo.amount = self.amount
        xinfo.ord_abi = self.payment.bank.abi
        xinfo.ord_cab = self.payment.cab
        xinfo.ord_account = self.payment.cc
        if hasattr(self.payment, 'high_priority'):
            if self.payment.high_priority:
                xinfo.prio = 'U'
        records.append(xinfo.format())

        ord_iban = PayerIBANInfo()
        ord_iban.prog_number = prog
        ord_iban.iban = self.payment.account.iban
        records.append(ord_iban.format())

        ben_iban = PayeeIBANInfo()
        ben_iban.prog_number = prog
        ben_iban.iban = self.account.iban
        records.append(ben_iban.format())

        ord_info = PayerInfo()
        ord_info.prog_number = prog
        ord_info.name = self.payment.debtor.name
        ord_info.tax_code = self.payment.debtor.cf
        records.append(ord_info.format())

        ben_info = PayeeInfo()
        ben_info.prog_number = prog
        ben_info.name = self.creditor.name
        if hasattr(self.creditor, 'cf'):
            ben_info.tax_code = self.creditor.cf
        records.append(ben_info.format())

        # Record 40 is not written
        records += self.rmt_cbi_records(prog=prog)

        return records

    @classmethod
    def rmtinfo_record(cls, record_type, prog, line):
        record = PurposeInfo()
        record.prog_number = prog
        record.record_type = record_type
        record.desc = line
        return record

    def rmt_cbi_records(self, prog):
        records = []
        if hasattr(self, 'rmtinfo'):
            if len(self.rmtinfo) <= 90:
                record = PurposeInfo()
                record.prog_number = prog
                record.desc = self.rmtinfo
                records += [record.format()]
            else:
                start = 0
                while start < len(self.rmtinfo):
                    records += [self.rmtinfo_record('60', prog,
                        self.rmtinfo[start:start+90]).format()]
        else:
            record_type = '60'
            if len(self.docs) <= 3:
                record_type = '50'
            i = 0
            line = ''
            while i < len(self.docs):
                line += self.docs[i].cbi()
                if i % 3 == 2:
                    records.append(self.rmtinfo_record(record_type, prog, line
                        ).format())
                    line = ''
                i += 1
            if line != '':
                records.append(self.rmtinfo_record(record_type, prog, line
                    ).format())
            if len(records) > 5:
                raise Exception('Too many documents for remittance info')
        return records


            





