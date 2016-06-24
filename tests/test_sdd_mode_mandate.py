# -*- coding: UTF-8 -*-
"""Contain test classes for the SDD mode Mandate class"""

from unittest import TestCase
from lxml import etree
from sepacbi import SddFactory
from sepacbi.transaction import Mandate
from sepacbi.account import Account
from sepacbi.bank import Bank

# pylint: disable=no-member

class TestEmitMandateTag(TestCase):
    """
    Test class for the emit_tag() method
    """

    def setUp(self):
        self.mandate = Mandate(rum='RUM-TEST', signature_date='2016-06-20')

    def test_emit_tag_without_amendment(self):
        """
        Check that the emited tag for a mandate without
        amendement is valid.
        """
        valid_tag = b'<MndtRltdInf><MndtId>RUM-TEST</MndtId><DtOfSgntr>2016-06-20</DtOfSgntr><AmdmntInd>false</AmdmntInd></MndtRltdInf>'
        to_check_tag = etree.tostring(self.mandate.emit_tag())
        self.assertEqual(valid_tag, to_check_tag)

    def test_emit_tag_with_old_rum_amendment(self):
        """
        Check that the emited tag for a mandate with old rum
        amendement is valid.
        """
        self.mandate.old_rum = 'OLD-RUM-TEST'
        valid_tag = b'<MndtRltdInf><MndtId>RUM-TEST</MndtId><DtOfSgntr>2016-06-20</DtOfSgntr><AmdmntInd>true</AmdmntInd><AmdmntInfDtls><OrgnlMndtId>OLD-RUM-TEST</OrgnlMndtId></AmdmntInfDtls></MndtRltdInf>'
        to_check_tag = etree.tostring(self.mandate.emit_tag())
        self.assertEqual(valid_tag, to_check_tag)

    def test_emit_tag_with_creditor_old_name_amendment(self):
        """
        Check that the emited tag for a mandate with old name
        amendement is valid.
        """
        IdHolder = SddFactory.get_id_holder()
        self.mandate.creditor = IdHolder(name='CREDITOR NAME', ics='ABCDEFGH',
                                         old_name='CREDITOR OLD NAME')
        valid_tag = b'<MndtRltdInf><MndtId>RUM-TEST</MndtId><DtOfSgntr>2016-06-20</DtOfSgntr><AmdmntInd>true</AmdmntInd><AmdmntInfDtls><OrgnlCdtrSchmeId><Nm>CREDITOR OLD NAME</Nm></OrgnlCdtrSchmeId></AmdmntInfDtls></MndtRltdInf>'
        to_check_tag = etree.tostring(self.mandate.emit_tag())
        self.assertEqual(valid_tag, to_check_tag)

    def test_emit_tag_with_creditor_old_ics_amendment(self):
        """
        Check that the emited tag for a mandate with old ics
        amendement is valid.
        """
        IdHolder = SddFactory.get_id_holder()
        self.mandate.creditor = IdHolder(name='CREDITOR NAME', ics='ABCDEFGH',
                                         old_ics='IJKLMNOP')
        valid_tag = b'<MndtRltdInf><MndtId>RUM-TEST</MndtId><DtOfSgntr>2016-06-20</DtOfSgntr><AmdmntInd>true</AmdmntInd><AmdmntInfDtls><OrgnlCdtrSchmeId><Id><PrvtId><Othr><Id>IJKLMNOP</Id><SchmeNm><Prtry>SEPA</Prtry></SchmeNm></Othr></PrvtId></Id></OrgnlCdtrSchmeId></AmdmntInfDtls></MndtRltdInf>'
        to_check_tag = etree.tostring(self.mandate.emit_tag())
        self.assertEqual(valid_tag, to_check_tag)

    def test_emit_tag_with_creditor_old_account_amendment(self):
        """
        Check that the emited tag for a mandate with old account
        amendement is valid.
        """
        self.mandate.old_account = Account(iban='FR2115583793123088059006193')
        valid_tag = b'<MndtRltdInf><MndtId>RUM-TEST</MndtId><DtOfSgntr>2016-06-20</DtOfSgntr><AmdmntInd>true</AmdmntInd><AmdmntInfDtls><OrgnlDbtrAcct><Id><IBAN>FR2115583793123088059006193</IBAN></Id></OrgnlDbtrAcct></AmdmntInfDtls></MndtRltdInf>'
        to_check_tag = etree.tostring(self.mandate.emit_tag())
        self.assertEqual(valid_tag, to_check_tag)

    def test_emit_tag_with_creditor_old_bank_amendment(self):
        """
        Check that the emited tag for a mandate with old bank
        amement is valid.
        """
        self.mandate.old_bank = Bank(bic='ABCDEFGH')
        valid_tag = b'<MndtRltdInf><MndtId>RUM-TEST</MndtId><DtOfSgntr>2016-06-20</DtOfSgntr><AmdmntInd>true</AmdmntInd><AmdmntInfDtls><OrgnlDbtrAgt><FinInstnId><Othr><Id>ABCDEFGH</Id></Othr></FinInstnId></OrgnlDbtrAgt></AmdmntInfDtls></MndtRltdInf>'
        to_check_tag = etree.tostring(self.mandate.emit_tag())
        self.assertEqual(valid_tag, to_check_tag)
