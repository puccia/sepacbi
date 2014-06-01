#!/usr/bin/python

"""
This module emits the root tag for the credit transfer.
"""

__copyright__ = 'Copyright (c) 2014 Emanuele Pucciarelli, C.O.R.P. s.n.c.'
__license__ = '3-clause BSD'

import sys

from lxml import etree
from .util import AttributeCarrier, booltext
from .entity import IdHolder
from .account import Account
from .bank import Bank
from .transaction import Transaction
from datetime import date, datetime

if sys.version_info[0] >= 3:
    # pylint: disable=redefined-builtin
    # pylint: disable=invalid-name
    basestring = str


class MissingABIError(Exception):
    """
    Raised when the debtor's ABI is not specified and cannot be inferred from
    the account.
    """

class NoTransactionsError(Exception):
    """
    Raised when trying to generate a credit transfer request containing no
    transactions.
    """
    pass

class InvalidEndToEndIDError(Exception):
    """
    Raised when a transaction has a non-unique end-to-end ID.
    """


class Payment(AttributeCarrier):
    # pylint: disable=no-member
    # pylint: disable=attribute-defined-outside-init
    # pylint: disable=access-member-before-definition
    """
    Payment represents the root tag for the credit transfer and holds
    all the associated information in its attributes, including the list
    of transactions to be performed.
    """
    allowed_args = (
        'id', 'batch', 'high_priority', 'execution_date',
        'debtor', 'account', 'abi', 'ultimate_debtor', 'charges_account',
        'envelope', 'initiator')

    ID_PREFIX = 'DistintaXml-'

    def __init__(self, **kwargs):
        self.envelope = False
        self.transactions = []
        self.eeid_set = set()
        super(Payment, self).__init__(**kwargs)

    def add_eeid(self, txid):
        "Add a transaction's end-to-end ID to check for uniqueness."
        if txid in self.eeid_set:
            raise InvalidEndToEndIDError('Duplicate end-to-end ID: %r' % txid)
        self.eeid_set.add(txid)

    def add_transaction(self, **kwargs):
        "Adds a transaction to the internal list. Does not return anything."
        kwargs['payment_seq'] = len(self.transactions)+1
        if not hasattr(self, 'id'):
            self.gen_id()
        kwargs['payment_id'] = self.id
        kwargs['register_eeid_function'] = self.add_eeid
        txr = Transaction(**kwargs)
        txr.perform_checks()
        self.transactions.append(txr)

    def gen_id(self):
        """Generate a unique ID for the payment"""
        self.id = '%s%s' % (self.ID_PREFIX, datetime.now().strftime(
            '%Y%m%d-%H%M%S'))

    def perform_checks(self):
        "Checks the validity of all supplied attributes."
        if not hasattr(self, 'id'):
            self.gen_id()
        self.max_length('id', 35)

        assert isinstance(self.debtor, IdHolder)

        if isinstance(self.account, basestring):
            self.account = Account(iban=self.account)
        assert isinstance(self.account, Account)

        if hasattr(self, 'abi'):
            abi = self.abi
        elif self.account.iban[:2] == 'IT':
            abi = self.account.iban[5:10]
        else:
            raise MissingABIError('The payment needs an \'abi\' attribute')
        self.bank = Bank(abi=abi)

        if hasattr(self, 'ultimate_debtor'):
            assert isinstance(self.ultimate_debtor, IdHolder)

        if hasattr(self, 'charges_account'):
            if isinstance(self.charges_account, basestring):
                self.charges_account = Account(iban=self.charges_account)
            assert isinstance(self.charges_account, Account)

        # Todo: if there is an initiator, check that it has a CUC
        # Todo: if there is no initiator, check that the debtor has a CUC

    def get_xml_root(self):
        """
        Builds the XML structure for the payment instruction, as dictated by the
        relevant standard.

        Returns a pair consisting of the root tag and the tag to which the
        Payment information should be appended. This allows the function to
        pick a different outer structure according to the value of the
        `envelope` attribute.
        """
        xsi = 'http://www.w3.org/2001/XMLSchema-instance'
        if self.envelope:
            tag = 'CBIBdyPaymentRequest'
        else:
            tag = 'CBIPaymentRequest'
        schema = tag + '.00.04.00'
        xmlns = 'urn:CBI:xsd:' + schema
        schema_location = xmlns + ' ' + schema + '.xsd'
        root = etree.Element(
            '{%s}%s' % (xmlns, tag),
            attrib={'{%s}schemaLocation' % xsi: schema_location},
            nsmap={'xsi': xsi, None: xmlns})
        outer = root
        if self.envelope:
            root = etree.SubElement(root, 'CBIEnvelPaymentRequest')
            root = etree.SubElement(root, 'CBIPaymentRequest')
        return outer, root

    def emit_tag(self):
        "Returns the whole XML structure for the payment."
        # Outer XML structure
        outer, root = self.get_xml_root()
        xmlns = 'urn:CBI:xsd:CBIPaymentRequest.00.04.00'

        # Header
        header = etree.SubElement(root, 'GrpHdr', nsmap={None: xmlns})
        etree.SubElement(header, 'MsgId').text = self.id
        etree.SubElement(header, 'CreDtTm').text = datetime.now().isoformat()
        etree.SubElement(header, 'NbOfTxs').text = str(len(self.transactions))
        etree.SubElement(header, 'CtrlSum').text = str(sum([
            tx.amount for tx in self.transactions]))
        if hasattr(self, 'initiator'):
            initiator = self.initiator
        else:
            initiator = self.debtor
        header.append(initiator.__tag__(as_initiator=True))

        # Payment info
        info = etree.SubElement(root, 'PmtInf', nsmap={None: xmlns})

        # TRF: no status requested
        etree.SubElement(info, 'PmtInfId').text = self.id
        etree.SubElement(info, 'PmtMtd').text = 'TRF'

        # Batch booking
        if hasattr(self, 'batch'):
            etree.SubElement(info, 'BtchBookg').text = booltext(self.batch)

        # Priority
        if hasattr(self, 'high_priority'):
            info = etree.SubElement(root, 'PmtTpInf')
            if hasattr(self, 'high_priority'):
                priority_text = 'NORM'
                if self.high_priority:
                    priority_text = 'HIGH'
                etree.SubElement(info, 'InstrPrty').text = priority_text
            svclvl = etree.SubElement(info, 'SvcLvl')
            etree.SubElement(svclvl, 'Cd').text = 'SEPA'

        # Execution date: either today or specified date
        execution_date = date.today()
        if hasattr(self, 'execution_date'):
            execution_date = self.execution_date
        etree.SubElement(info, 'ReqdExctnDt').text = execution_date.isoformat()

        # Debtor information
        info.append(self.debtor.__tag__('Dbtr'))

        # Debtor account
        info.append(self.account.__tag__('DbtrAcct'))

        agent = etree.SubElement(info, 'DbtrAgt')
        agent.append(self.bank.__tag__(output_abi=True))

        # Ultimate debtor
        if hasattr(self, 'ultimate_debtor'):
            info.append(self.ultimate_debtor.__tag__('UltmtDbtr'))
        etree.SubElement(info, 'ChrgBr').text = 'SLEV'

        # Charges account
        if hasattr(self, 'charges_account'):
            info.append(self.charges_account.__tag__('ChrgsAcct'))

        # Transactions
        if len(self.transactions) == 0:
            raise NoTransactionsError
        for txr in self.transactions:
            info.append(txr.__tag__())

        return outer

    def xml(self):
        return self.__tag__()

    def text(self, **kwargs):
        return etree.tostring(self.xml(), **kwargs)
