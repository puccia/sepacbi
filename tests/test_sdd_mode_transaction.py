# -*- coding: UTF-8 -*-
"""Contain test classes for the SDD mode Transaction class"""

from unittest import TestCase
from lxml import etree
from sepacbi import SddFactory
from sepacbi.transaction import Mandate
from sepacbi.account import Account
from sepacbi.bank import Bank

# pylint: disable=no-member

class TestEmitTransactionTag(TestCase):
    """
    Test class for the emit_tag() method
    """

    def setUp(self):
        Transaction = SddFactory.get_transaction()
        IdHolder = SddFactory.get_id_holder()
        self.transaction = Transaction()
        self.debtor = IdHolder(name="DEBTOR NAME")
        self.ultimate_debtor = IdHolder(name="ULTIMATE DEBTOR")
        self.bank = Bank(bic='ABCDEFGH')

    def test_emit_tag(self):
        """
        Check that the emited tag for a transaction without
        a mandate and an ultimate debotr is valid.
        """
        self.transaction.eeid = 'ID-TEST'
        self.transaction.account = Account(iban='FR0821227314820689509584984')
        self.transaction.bank = Bank(bic='ABCDEFGH')
        self.transaction.debtor = self.debtor
        self.transaction.amount = 666.66
        valid_tag = b'<DrctDbtTxInf><PmtId><EndToEndId>ID-TEST</EndToEndId></PmtId><InstdAmt Ccy="EUR">666.66</InstdAmt><DbtrAgt><FinInstnId><BIC>ABCDEFGH</BIC></FinInstnId></DbtrAgt><Dbtr><Nm>DEBTOR NAME</Nm></Dbtr><DbtrAcct><Id><IBAN>FR0821227314820689509584984</IBAN></Id></DbtrAcct></DrctDbtTxInf>'
        to_check_tag = etree.tostring(self.transaction.emit_tag())
        self.assertEqual(valid_tag, to_check_tag)

    def test_emit_tag_with_ultimate_debtor(self):
        """
        Check that the emited tag for a transaction with an ultimate debtor
        and without a mandate is valid.
        """
        self.transaction.eeid = 'ID-TEST'
        self.transaction.account = Account(iban='FR0821227314820689509584984')
        self.transaction.bank = Bank(bic='ABCDEFGH')
        self.transaction.debtor = self.debtor
        self.transaction.ultimate_debtor = self.ultimate_debtor
        self.transaction.amount = 666.66
        valid_tag = b'<DrctDbtTxInf><PmtId><EndToEndId>ID-TEST</EndToEndId></PmtId><InstdAmt Ccy="EUR">666.66</InstdAmt><DbtrAgt><FinInstnId><BIC>ABCDEFGH</BIC></FinInstnId></DbtrAgt><Dbtr><Nm>DEBTOR NAME</Nm></Dbtr><DbtrAcct><Id><IBAN>FR0821227314820689509584984</IBAN></Id></DbtrAcct><UltmtDbtr><Nm>ULTIMATE DEBTOR</Nm></UltmtDbtr></DrctDbtTxInf>'
        to_check_tag = etree.tostring(self.transaction.emit_tag())
        self.assertEqual(valid_tag, to_check_tag)

    def test_emit_tag_with_madate(self):
        """
        Check that the emited tag for a transaction with an ultimate debtor
        and without a mandate is valid.
        """
        self.transaction.eeid = 'ID-TEST'
        self.transaction.account = Account(iban='FR0821227314820689509584984')
        self.transaction.bank = Bank(bic='ABCDEFGH')
        self.transaction.debtor = self.debtor
        self.transaction.mandate = Mandate(rum='RUM-TEST', signature_date='2016-06-01')
        self.transaction.amount = 666.66
        valid_tag = b'<DrctDbtTxInf><PmtId><EndToEndId>ID-TEST</EndToEndId></PmtId><InstdAmt Ccy="EUR">666.66</InstdAmt><DrctDbtTx><MndtRltdInf><MndtId>RUM-TEST</MndtId><DtOfSgntr>2016-06-01</DtOfSgntr><AmdmntInd>false</AmdmntInd></MndtRltdInf></DrctDbtTx><DbtrAgt><FinInstnId><BIC>ABCDEFGH</BIC></FinInstnId></DbtrAgt><Dbtr><Nm>DEBTOR NAME</Nm></Dbtr><DbtrAcct><Id><IBAN>FR0821227314820689509584984</IBAN></Id></DbtrAcct></DrctDbtTxInf>'
        to_check_tag = etree.tostring(self.transaction.emit_tag())
        self.assertEqual(valid_tag, to_check_tag)
