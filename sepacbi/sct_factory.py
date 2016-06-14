# -*- coding: UTF-8 -*-
"""Module containing the SctFactory and SddFactory classes"""

import sys
from lxml import etree
from decimal import Decimal
from .util import booltext
from .payment import Payment, MissingABIError, NoTransactionsError, InvalidEndToEndIDError
from .transaction import Transaction, MissingBICError, CATEGORY_CBI_MAP
from .entity import IdHolder, Address, MissingCUCError, AddressFormatError, emit_id_tag
from .account import Account
from .bank import Bank
from .cbibon_dom import TransferInfo, PayerIBANInfo, PayeeIBANInfo, \
    PayerInfo, PayeeInfo, PayeeAddress, PurposeInfo, StatusRequest, \
    PCRecord, EFRecord
from datetime import date, datetime

if sys.version_info[0] >= 3:
    # pylint: disable=redefined-builtin
    # pylint: disable=invalid-name
    unicode = str
    basestring = str

class SctFactory(object):
    """Factory for the SCT request mode"""

    @staticmethod
    def get_payment():
        """Returns the Payment class"""

        payment_allowed_args = (
            'req_id', 'batch', 'high_priority', 'execution_date',
            'debtor', 'account', 'abi', 'ultimate_debtor', 'charges_account',
            'envelope', 'initiator')
        setattr(Payment, 'allowed_args', payment_allowed_args)

        setattr(Payment, 'envelope', False)

        def perform_checks(self):
            "Checks the validity of all supplied attributes."
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
        setattr(Payment, 'perform_checks', perform_checks)

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
        setattr(Payment, 'get_xml_root', get_xml_root)

        def emit_tag(self):
            "Returns the whole XML structure for the payment."
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
        setattr(Payment, 'emit_tag', emit_tag)

        def cbi_text(self):
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
        setattr(Payment, 'cbi_text', cbi_text)

        return Payment

    @staticmethod
    def get_transaction():
        """Returns a STransaction object"""
        transaction_allowed_args = (
            'tx_id', 'eeid', 'category', 'rmtinfo', 'amount',
            'ultimate_debtor', 'bic', 'account', 'creditor', 'ultimate_creditor',
            'docs', 'purpose', 'payment_seq', 'payment_id',
            'register_eeid_function', 'payment', 'cbi_purpose')
        setattr(Transaction, 'allowed_args', transaction_allowed_args)

        setattr(Transaction, 'purpose', 'SUPP')

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
        setattr(Transaction, 'perform_checks', perform_checks)

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
        setattr(Transaction, 'emit_tag', emit_tag)

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

            # The status request record is empty
            status_req = StatusRequest()
            status_req.prog_number = prog
            records.append(status_req.format())

            return records
        setattr(Transaction, 'cbi_records', cbi_records)

        def rmtinfo_record(cls, record_type, prog, line):
            record = PurposeInfo()
            record.prog_number = prog
            record.record_type = record_type
            record.desc = line
            return record
        setattr(Transaction, 'rmtinfo_record', classmethod(rmtinfo_record))

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
        setattr(Transaction, 'rmt_cbi_records', rmt_cbi_records)

        return Transaction

    @staticmethod
    def get_id_holder():
        """returns an IdHolder object"""
        id_holder_allowed_args = ('name', 'cf', 'code', 'private', 'cuc',
                                  'address', 'country', 'sia_code')
        setattr(IdHolder, 'allowed_args', id_holder_allowed_args)

        def perform_checks(self):
            # pylint: disable=access-member-before-definition
            # pylint: disable=attribute-defined-outside-init
            "Check argument lengths."
            if hasattr(self, 'name'):
                self.max_length('name', 70)
            if hasattr(self, 'cf'):
                assert not hasattr(self, 'code')
                self.max_length('cf', 16)
            if hasattr(self, 'cuc'):
                self.max_length('cuc', 35)
            if hasattr(self, 'address'):
                if isinstance(self.address, (list, tuple)):
                    self.address = Address(*self.address)
                assert isinstance(self.address, Address)
            if hasattr(self, 'country'):
                self.length('country', 2)
        setattr(IdHolder, 'perform_checks', perform_checks)

        def emit_tag(self, tag=None, as_initiator=False):
            """
            Emit a subtree for an entity, using the supplied tag for the root
            element. If the identity is the Initiator's, emit the CUC as well.
            """
            if as_initiator:
                tag = 'InitgPty'
            root = etree.Element(tag)

            # Name
            if hasattr(self, 'name'):
                name = etree.SubElement(root, 'Nm')
                name.text = self.name

            # Address
            if hasattr(self, 'address') and not as_initiator:
                root.append(self.address.__tag__())

            # ID
            idtag = etree.SubElement(root, 'Id')
            if self.private:
                id_container = 'PrvtId'
            else:
                id_container = 'OrgId'
            orgid = etree.SubElement(idtag, id_container)

            # CUC
            if as_initiator:
                if not hasattr(self, 'cuc'):
                    raise MissingCUCError
                orgid.append(emit_id_tag(self.cuc, 'CBI'))

            # Tax code
            if hasattr(self, 'cf'):
                orgid.append(emit_id_tag(self.cf, 'ADE'))

            if hasattr(self, 'code'):
                orgid.append(emit_id_tag(self.code, None))

            if not as_initiator and hasattr(self, 'country'):
                etree.SubElement(root, 'CtryOfRes').text = self.country

            return root
        setattr(IdHolder, 'emit_tag', emit_tag)

        return IdHolder
