# -*- coding: UTF-8 -*-
"""Module containing the SddFactory class"""

import sys
from decimal import Decimal
from datetime import date, datetime
from lxml import etree
from .payment import Payment, SequenceTypeError
from .transaction import Transaction, MissingBICError
from .entity import IdHolder, Address, emit_id_tag, MissingICSError
from .account import Account
from .bank import Bank

if sys.version_info[0] >= 3:
    # pylint: disable=redefined-builtin
    # pylint: disable=invalid-name
    unicode = str
    basestring = str

class SddFactory(object):
    """Factory for the SDD request mode."""

    @staticmethod
    def get_payment():
        """Builds and returns the Payment class"""
        payment_allowed_args = ('msg_id', 'initiator', 'req_id', 'sequence_type',
                                'collection_date', 'creditor', 'account', 'bic',
                                'ultimate_creditor')
        setattr(Payment, 'allowed_args', payment_allowed_args)

        allowed_sequence_types = ('OOFF', 'FRST', 'RCUR', 'FNAL')
        setattr(Payment, 'allowed_sequence_types', allowed_sequence_types)

        def get_initiator(self):
            """
            Returns the entity designated as initiator for the transfer.
            """
            if hasattr(self, 'initiator'):
                return self.initiator
            else:
                return self.creditor
        setattr(Payment, 'get_initiator', get_initiator)

        def perform_checks(self):
            "Checks the validity of all supplied attributes."
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
        setattr(Payment, 'perform_checks', perform_checks)

        def emit_tag(self):
            """Returns the whole XML structure for the payment."""
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
            cdtrschmeid.append(self.creditor.emit_scheme_id_tag())

            # Transactions
            if len(self.transactions) == 0:
                raise NoTransactionsError
            for txr in self.transactions:
                info.append(txr.__tag__())
            return root
        setattr(Payment, 'emit_tag', emit_tag)

        return Payment

    @staticmethod
    def get_transaction():
        """Builds and returns the Transaction class"""
        transaction_allowed_args = ('eeid', 'amount', 'debtor', 'account',
                                    'bic', 'ultimate_debtor','payment_seq',
                                    'payment_id','register_eeid_function',
                                    'payment')
        setattr(Transaction, 'allowed_args', transaction_allowed_args)

        def perform_checks(self):
            "Checks the validity of all supplied attributes."
            if not hasattr(self, 'eeid'):
                self.gen_eeid()
            self.max_length('eeid', 35)
            if not self.eeid_registered:
                self.register_eeid_function(self.eeid)
                self.eeid_registered = True

            if not isinstance(self.amount, Decimal):
                self.amount = Decimal(str(self.amount)).quantize(Decimal('.01'))

            assert isinstance(self.debtor, IdHolder)

            if isinstance(self.account, basestring):
                self.account = Account(iban=self.account)
            assert isinstance(self.account, Account)

            if not hasattr(self, 'bic'):
                raise MissingBICError
            bic_length = len(self.bic)
            assert bic_length in (8, 11)
            bic = self.bic
            self.bank = Bank(bic=bic)

            if hasattr(self, 'ultimate_debtor'):
                assert isinstance(self.ultimate_debtor, IdHolder)
        setattr(Transaction, 'perform_checks', perform_checks)

        def emit_tag(self):
            """
            Returns the XML tag for the transaction.
            """
            root = etree.Element('DrctDbtTxInf')
            # Transaction ID
            pmtid = etree.SubElement(root, 'PmtId')
            etree.SubElement(pmtid, 'EndToEndId').text = self.eeid

            # Amount
            etree.SubElement(root, 'InstdAmt', attrib={'Ccy':"EUR"}).text = str(self.amount)

            # Mandate
            # drctdbttx = etree.SubElement(root, 'DrctDbtTx')

            # Debtor Agent
            agt = etree.SubElement(root, 'DbtrAgt')
            agt.append(self.bank.__tag__())

            # Debtor
            root.append(self.debtor.__tag__('Dbtr'))

            #Debtor Account
            root.append(self.account.__tag__('DbtrAcct'))

            # Ultimate Debtor
            if hasattr(self, 'ultimate_debtor'):
                root.append(self.ultimate_debtor.__tag__('UltmtDbtr'))

            return root
        setattr(Transaction, 'emit_tag', emit_tag)

        return Transaction

    @staticmethod
    def get_id_holder():
        """Builds and returns the IdHolder class"""
        id_holder_allowed_args = ('name', 'private', 'identifier', 'ics',
                                  'address', 'country')
        setattr(IdHolder, 'allowed_args', id_holder_allowed_args)

        def perform_checks(self):
            # pylint: disable=access-member-before-definition
            # pylint: disable=attribute-defined-outside-init
            "Check argument lengths."
            if hasattr(self, 'name'):
                self.max_length('name', 70)

            if hasattr(self, 'identifier'):
                self.max_length('identifier', 35)

            if hasattr(self, 'ics'):
                self.max_length('ics', 35)

            if hasattr(self, 'address'):
                if isinstance(self.address, (list, tuple)):
                    self.address = Address(*self.address)
                assert isinstance(self.address, Address)

            if hasattr(self, 'country'):
                self.length('country', 2)
        setattr(IdHolder, 'perform_checks', perform_checks)

        def emit_tag(self, tag=None):
            """
            Emit a subtree for an entity, using the supplied tag for the root
            element.
            """

            root = etree.Element(tag)

            # Name
            if hasattr(self, 'name'):
                name = etree.SubElement(root, 'Nm')
                name.text = self.name

            # Address
            if hasattr(self, 'address'):
                root.append(self.address.__tag__())

            # ID
            if hasattr(self, 'identifier'):
                idtag = etree.SubElement(root, 'Id')
                if self.private:
                    id_container = 'PrvtId'
                else:
                    id_container = 'OrgId'
                orgid = etree.SubElement(idtag, id_container)
                orgid.append(emit_id_tag(self.identifier, None))

            # Country
            if hasattr(self, 'country'):
                etree.SubElement(root, 'CtryOfRes').text = self.country
            return root
        setattr(IdHolder, 'emit_tag', emit_tag)

        def emit_scheme_id_tag(self):
            """
            For a creditor, emits the scheme id tag
            """
            if not hasattr(self, 'ics'):
                raise MissingICSError
            idtag = etree.Element('Id')
            prvtid = etree.SubElement(idtag, 'PrvtId')
            prvtid.append(emit_id_tag(self.ics, 'scheme_id'))
            return idtag
        setattr(IdHolder, 'emit_scheme_id_tag', emit_scheme_id_tag)


        return IdHolder
