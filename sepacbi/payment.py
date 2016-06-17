#!/usr/bin/python

"""
This module emits the root tag for the credit transfer.
"""

import sys
from datetime import date, datetime
from lxml import etree
from .util import AttributeCarrier, booltext
from .entity import IdHolder
from .account import Account
from .bank import Bank
from .transaction import Transaction, MissingBICError
from .cbibon_dom import PCRecord, EFRecord

__copyright__ = 'Copyright (c) 2014 Emanuele Pucciarelli, C.O.R.P. s.n.c.'
__license__ = '3-clause BSD'



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

class SequenceTypeError(Exception):
    """
    Raised when the sequence type for a payment is wrong or missing
    """

class Payment(AttributeCarrier):
    # pylint: disable=attribute-defined-outside-init
    # pylint: disable=access-member-before-definition
    """
    Payment represents the root tag for the credit transfer and holds
    all the associated information in its attributes, including the list
    of transactions to be performed.
    """

    ID_PREFIX = 'DistintaXml-'

    def __init__(self, **kwargs):
        self.transactions = []
        self.eeid_set = set()
        super(Payment, self).__init__(**kwargs)

    def add_eeid(self, txid):
        """
        Add a transaction's end-to-end ID to check for uniqueness.
        """
        if txid in self.eeid_set:
            raise InvalidEndToEndIDError('Duplicate end-to-end ID: %r' % txid)
        self.eeid_set.add(txid)

    def gen_id(self):
        """
        Generate a unique ID for the payment
        """
        self.req_id = '%s%s' % (self.ID_PREFIX, datetime.now().strftime(
            '%Y%m%d-%H%M%S'))

    def amount_sum(self):
        """
        Return the sum of the transactions amounts.
        """
        return sum([tx.amount for tx in self.transactions])

    def xml(self):
        """
        Return the lxml tree.
        """
        return self.__tag__()

    def xml_text(self, **kwargs):
        """
        Return the XML structure as a string.
        """
        # pylint: disable=no-member
        return etree.tostring(self.xml(), **kwargs)

# SCT Mode Payment attrributes and methods

sct_allowed_args = (
    'req_id', 'batch', 'high_priority', 'execution_date',
    'debtor', 'account', 'abi', 'ultimate_debtor', 'charges_account',
    'envelope', 'initiator')

def sct_get_initiator(self):
    """
    Returns the entity designated as initiator for the transfer.
    """
    if hasattr(self, 'initiator'):
        return self.initiator
    else:
        return self.debtor

def sct_add_transaction(self, **kwargs):
    """
    Adds a transaction to the internal list. Does not return anything.
    """
    # pylint: disable=no-member
    kwargs['payment_seq'] = len(self.transactions)+1
    if not hasattr(self, 'req_id'):
        self.gen_id()
    kwargs['payment_id'] = self.req_id
    kwargs['register_eeid_function'] = self.add_eeid
    kwargs['payment'] = self
    txr = Transaction(**kwargs)
    txr.perform_checks()
    self.transactions.append(txr)

def sct_perform_checks(self):
    """
    Checks the validity of all supplied attributes.
    """
    if not hasattr(self, 'req_id'):
        self.gen_id()
    self.max_length('req_id', 35)

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

    # for CBI text files
    self.cab = self.account.iban[10:15]
    self.cc = self.account.iban[15:27]

    if hasattr(self, 'ultimate_debtor'):
        assert isinstance(self.ultimate_debtor, IdHolder)

    if hasattr(self, 'charges_account'):
        if isinstance(self.charges_account, basestring):
            self.charges_account = Account(iban=self.charges_account)
        assert isinstance(self.charges_account, Account)

def sct_get_xml_root(self):
    """
    Builds the XML structure for the payment instruction, as dictated by the
    relevant standard.

    Returns a pair consisting of the root tag and the tag to which the
    Payment information should be appended. This allows the function to
    pick a different outer structure according to the value of the
    `envelope` attribute.
    """
    # pylint: disable=no-member
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

def sct_emit_tag(self):
    """
    Returns the whole XML structure for the payment.
    """
    # pylint: disable=no-member
    # Outer XML structure
    outer, root = self.get_xml_root()
    xmlns = 'urn:CBI:xsd:CBIPaymentRequest.00.04.00'

    # Header
    header = etree.SubElement(root, 'GrpHdr', nsmap={None: xmlns})
    etree.SubElement(header, 'MsgId').text = self.req_id
    etree.SubElement(header, 'CreDtTm').text = datetime.now().isoformat()
    etree.SubElement(header, 'NbOfTxs').text = str(len(self.transactions))
    etree.SubElement(header, 'CtrlSum').text = str(self.amount_sum())
    initiator = self.get_initiator()
    header.append(initiator.__tag__(as_initiator=True))

    # Payment info
    info = etree.SubElement(root, 'PmtInf', nsmap={None: xmlns})

    # TRF: no status requested
    etree.SubElement(info, 'PmtInfId').text = self.req_id
    etree.SubElement(info, 'PmtMtd').text = 'TRF'

    # Batch booking
    if hasattr(self, 'batch'):
        etree.SubElement(info, 'BtchBookg').text = booltext(self.batch)

    # Priority
    if hasattr(self, 'high_priority'):
        tp_info = etree.SubElement(info, 'PmtTpInf')
        if hasattr(self, 'high_priority'):
            priority_text = 'NORM'
            if self.high_priority:
                priority_text = 'HIGH'
            etree.SubElement(tp_info, 'InstrPrty').text = priority_text
        svclvl = etree.SubElement(tp_info, 'SvcLvl')
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

def sct_cbi_text(self):
    self.perform_checks()

    if self.account.is_foreign():
        raise Exception('Cannot use foreign accounts with CBI text files')

    today = date.today()

    header = PCRecord()
    footer = EFRecord()

    sia_code = self.get_initiator().sia_code
    header.sender = sia_code
    footer.sender = sia_code
    header.recipient = self.bank.abi
    footer.recipient = self.bank.abi
    header.creation = today
    footer.creation = today
    header.name = 'Distinta'
    footer.name = 'Distinta'
    if hasattr(self, 'high_priority'):
        if self.high_priority:
            header.prio = 'U'
            footer.prio = 'U'

    footer.orders = len(self.transactions)
    footer.negative_amounts = 0
    footer.positive_amounts = self.amount_sum()

    records = [header.format()]
    for transaction, i in zip(self.transactions,
                              range(len(self.transactions))):
        records += transaction.cbi_records(i+1)
    footer.records = len(records)+1
    records.append(footer.format())
    records.append(u'')
    return '\n'.join(records)

sct_payment_attr_dict = {'allowed_args' : sct_allowed_args,
                         'envelope' : False,
                         'get_initiator' : sct_get_initiator,
                         'add_transaction' : sct_add_transaction,
                         'perform_checks' : sct_perform_checks,
                         'get_xml_root' : sct_get_xml_root,
                         'emit_tag' : sct_emit_tag,
                         'cbi_text' : sct_cbi_text
                        }

# SDD Mode attributes and methods

sdd_allowed_args = ('msg_id', 'initiator', 'req_id', 'sequence_type',
                    'collection_date', 'creditor', 'account', 'bic',
                    'ultimate_creditor')

allowed_sequence_types = ('OOFF', 'FRST', 'RCUR', 'FNAL')

def sdd_get_initiator(self):
    """
    Returns the entity designated as initiator for the transfer.
    """
    if hasattr(self, 'initiator'):
        return self.initiator
    else:
        return self.creditor

def sdd_add_transaction(self, **kwargs):
    """
    Adds a transaction to the internal list. Does not return anything.
    """
    # pylint: disable=no-member
    kwargs['payment_seq'] = len(self.transactions)+1
    if not hasattr(self, 'req_id'):
        self.gen_id()
    kwargs['payment_id'] = self.req_id
    kwargs['register_eeid_function'] = self.add_eeid
    kwargs['payment'] = self
    if hasattr(self.creditor, 'old_name') or hasattr(self.creditor, 'old_ics'):
        kwargs['creditor'] = self.creditor
    txr = Transaction(**kwargs)
    txr.perform_checks()
    self.transactions.append(txr)

def sdd_perform_checks(self):
    """
    Checks the validity of all supplied attributes.
    """
    if not hasattr(self, 'msg_id'):
        self.gen_id()
    self.max_length('msg_id', 35)

    if not hasattr(self, 'req_id'):
        self.gen_id()
    self.max_length('req_id', 35)

    if hasattr(self, 'initiator'):
        assert isinstance(self.initiator, IdHolder)

    if not hasattr(self, 'sequence_type'):
        raise SequenceTypeError('Sequence type must be provided')
    elif self.sequence_type not in self.allowed_sequence_types:
        raise SequenceTypeError('Sequence type must be : OOFF, FRST, RCUR or FNAL')

    if hasattr(self, 'collection_date'):
        if isinstance(self.collection_date, basestring):
            self.max_length('collection_date', 10)
            self.collection_date = datetime.strptime(self.collection_date, '%Y-%m-%d').date()

    assert isinstance(self.creditor, IdHolder)

    if isinstance(self.account, basestring):
        self.account = Account(iban=self.account)
    assert isinstance(self.account, Account)

    if not hasattr(self, 'bic'):
        raise MissingBICError
    bic_length = len(self.bic)
    assert bic_length in (8, 11)
    bic = self.bic
    self.bank = Bank(bic=bic)

    if hasattr(self, 'ultimate_creditor'):
        assert isinstance(self.ultimate_creditor, IdHolder)

def sdd_emit_tag(self):
    """
    Returns the whole XML structure for the payment.
    """
    # pylint: disable=no-member
    root = etree.Element('Document', nsmap={None : "urn:iso:std:iso:20022:tech:xsd:pain.008.001.02",
                                            'xsi' : "http://www.w3.org/2001/XMLSchema-instance"})
    cstmrdrctdtinitn = etree.SubElement(root, 'CstmrDrctDbtInitn')

    # Group Header
    grphdr = etree.SubElement(cstmrdrctdtinitn, 'GrpHdr')
    etree.SubElement(grphdr, 'MsgId').text = self.msg_id
    etree.SubElement(grphdr, 'CreDtTm').text = datetime.now().isoformat()
    etree.SubElement(grphdr, 'NbOfTxs').text = str(len(self.transactions))
    etree.SubElement(grphdr, 'CtrlSum').text = str(self.amount_sum())
    initiator = self.get_initiator()
    grphdr.append(initiator.__tag__('InitgPty'))

    # Payment Information
    info = etree.SubElement(cstmrdrctdtinitn, 'PmtInf')

    # Payment ID
    etree.SubElement(info, 'PmtInfId').text = self.req_id

    # Payment Method
    etree.SubElement(info, 'PmtMtd').text = 'DD'

    # Payment Type Information
    pmttpinf = etree.SubElement(info, 'PmtTpInf')
    svclvl = etree.SubElement(pmttpinf, 'SvcLvl')
    etree.SubElement(svclvl, 'Cd').text = 'SEPA'
    lclinstrm = etree.SubElement(pmttpinf, 'LclInstrm')
    etree.SubElement(lclinstrm, 'Cd').text = 'CORE'
    etree.SubElement(pmttpinf, 'SeqTp').text = self.sequence_type

    # Payment Requested Collection Date
    collection_date = date.today()
    if hasattr(self, 'collection_date'):
        collection_date = self.collection_date
    etree.SubElement(info, 'ReqdColltnDt').text = collection_date.isoformat()

    # Creditor Informations
    info.append(self.creditor.__tag__('Cdtr'))

    # Creditor Account
    info.append(self.account.__tag__('CdtrAcct'))

    agent = etree.SubElement(info, 'CdtrAgt')
    agent.append(self.bank.__tag__())

    # Ultimate Creditor
    if hasattr(self, 'ultimate_creditor'):
        info.append(self.ultimate_creditor.__tag__('UltmtCdtr'))

    # Charge Bearer
    etree.SubElement(info, 'ChrgBr').text = 'SLEV'

    # Creditor Scheme ID
    cdtrschmeid = etree.SubElement(info, 'CdtrSchmeId')
    cdtrschmeid.append(self.creditor.emit_scheme_id_tag(self.creditor.ics))

    # Transactions
    if len(self.transactions) == 0:
        raise NoTransactionsError
    for txr in self.transactions:
        info.append(txr.__tag__())
    return root

sdd_payment_attr_dict = {'allowed_args' : sdd_allowed_args,
                         'allowed_sequence_types' : allowed_sequence_types,
                         'get_initiator' : sdd_get_initiator,
                         'add_transaction' : sdd_add_transaction,
                         'perform_checks' : sdd_perform_checks,
                         'emit_tag' : sdd_emit_tag
                        }
