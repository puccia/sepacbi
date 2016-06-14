# -*- coding: UTF-8 -*-
"""Module containing the SddFactory class"""

from decimal import Decimal
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
        payment_allowed_args = ('msg_id', 'initiator', 'req_id', 'sequence_tye',
                                'collection_date', 'creditor', 'account', 'bic',
                                'ultimate_creditor')
        setattr(Payment, 'allowed_args', payment_allowed_args)

        allowed_sequence_types = ('OOFF', 'FRST', 'RCUR', 'FNAL')
        setattr(Payment, 'allowed_sequence_types', allowed_sequence_types)

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

            if not hasattr(self, 'sequence_tye'):
                raise SequenceTypeError('Sequence type must be provided')
            elif self.sequence_tye not in self.allowed_sequence_types:
                raise SequenceTypeError('Sequence type must be : OOFF, FRST, RCUR or FNAL')

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
            
        setattr(Payment, 'emit_tag', emit_tag)

        return Payment

    @staticmethod
    def get_transaction():
        """Builds and returns the Transaction class"""
        transaction_allowed_args = ('eeid', 'amount', 'debtor', 'account',
                                    'bic', 'ultimate_debtor')
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
            pmtid = etree.SubElement(root, 'PmtId')
            etree.SubElement(pmtid, 'EndToEndId').text = self.eeid
            etree.SubElement(root, 'InstdAmt', attrib={'Ccy':"EUR"}).text = self.amount
            # drctdbttx = etree.SubElement(root, 'DrctDbtTx')
            agt = etree.SubElement(root, 'DbtrAgt')
            agt.append(self.Bank.__tag__())
            root.append(self.creditor.__tag__('Cdtr'))
            root.append(self.account.__tag__('CdtrAcct'))
            if hasattr(self, 'ultimate_debtor'):
                root.append(self.ultimate_creditor.__tag__('UltmtDbtr'))
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
        setattr(IdHolder, 'emit_tag', emit_tag)

        def emit_scheme_id_tag(self):
            """
            For a creditor, emits the scheme id tag
            """
            if not hasattr(self, 'ics'):
                raise MissingICSError
            idtag = etree.Element('Id')
            prvtid = etree.SubElement(idtag, 'PrvtId')
            orgid.append(emit_id_tag(self.ics, None))
        setattr(IdHolder, 'emit_scheme_id_tag', emit_scheme_id_tag)


        return IdHolder
