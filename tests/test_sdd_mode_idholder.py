# -*- coding: UTF-8 -*-
"""Contain test classes for the SDD mode IdHolder class"""

from unittest import TestCase
from types import FunctionType
from lxml import etree
from sepacbi import SddFactory
from sepacbi.entity import MissingICSError, Address

# pylint: disable=no-member

class TestEmitTag(TestCase):
    """
    Test class for the emit_tag() method.
    """

    def setUp(self):
        IdHolder = SddFactory.get_id_holder()
        self.id_holder = IdHolder()
        self.tag = "TestTag"

    def test_emit_tag_nm(self):
        """
        Check that the the emited tag for the Id holder's name is valid.
        """
        valid_name_tag = b'<TestTag><Nm>NAME TEST</Nm></TestTag>'
        self.id_holder.name = "NAME TEST"
        to_check_tag = etree.tostring(self.id_holder.emit_tag(self.tag))
        self.assertEqual(valid_name_tag, to_check_tag)

    def test_emit_tag_address(self):
        """
        Check that the the emited tag for the Id holder's
        postal address is valid.
        """
        valid_address_tag = b'<TestTag><PstlAdr><AdrLine>Addr Line 1</AdrLine><AdrLine>Addr Line 2</AdrLine></PstlAdr></TestTag>'
        address = Address("Addr Line 1", "Addr Line 2")
        self.id_holder.address = address
        to_check_tag = etree.tostring(self.id_holder.emit_tag(self.tag))
        self.assertEqual(valid_address_tag, to_check_tag)

    def test_emit_tag_id_with_private_true(self):
        """
        Check that the the emited tag for the Id holder's
        ID is valid with the attribute private set on True.
        """
        valid_id_tag = b'<TestTag><Id><PrvtId><Othr><Id>ID-TEST</Id></Othr></PrvtId></Id></TestTag>'
        self.id_holder.private = True
        self.id_holder.identifier = "ID-TEST"
        to_check_tag = etree.tostring(self.id_holder.emit_tag(self.tag))
        self.assertEqual(valid_id_tag, to_check_tag)

    def test_emit_tag_id_with_private_false(self):
        """
        Check that the the emited tag for the Id holder's
        ID is valid with the attribute private set on False.
        """
        valid_id_tag = b'<TestTag><Id><OrgId><Othr><Id>ID-TEST</Id></Othr></OrgId></Id></TestTag>'
        self.id_holder.private = False
        self.id_holder.identifier = "ID-TEST"
        to_check_tag = etree.tostring(self.id_holder.emit_tag(self.tag))
        self.assertEqual(valid_id_tag, to_check_tag)

    def test_emit_tag_country(self):
        """
        Check that the the emited tag for the Id holder's country is valid.
        """
        valid_country_tag = b'<TestTag><CtryOfRes>FR</CtryOfRes></TestTag>'
        self.id_holder.country = "FR"
        to_check_tag = etree.tostring(self.id_holder.emit_tag(self.tag))
        self.assertEqual(valid_country_tag, to_check_tag)


class TestEmitSchemeIdTag(TestCase):
    """
    Test class for the emit_scheme_id_tag() method.
    """

    def setUp(self):
        IdHolder = SddFactory.get_id_holder()
        self.creditor = IdHolder()
        self.valid_ics_id_tag = b'<Id><PrvtId><Othr><Id>FR00ZZ123456</Id><SchmeNm><Prtry>SEPA</Prtry></SchmeNm></Othr></PrvtId></Id>'
        self.valid_old_ics_id_tag = b'<Id><PrvtId><Othr><Id>FR00ZZ654321</Id><SchmeNm><Prtry>SEPA</Prtry></SchmeNm></Othr></PrvtId></Id>'

    def test_missing_ics_error(self):
        """
        Check that the MissingICSError exception
        is raised when a creditor has no ICS code.
        """
        with self.assertRaises(MissingICSError):
            self.creditor.emit_scheme_id_tag()

        self.creditor.ics = "FR00ZZ123456"
        with self.assertRaises(MissingICSError):
            self.creditor.emit_scheme_id_tag(mode='old')

    def test_ics_scheme_id(self):
        """
        Check that the emited tag for the ics is valid
        """
        self.creditor.ics = "FR00ZZ123456"
        to_check_tag = etree.tostring(self.creditor.emit_scheme_id_tag())
        self.assertEqual(self.valid_ics_id_tag, to_check_tag)

    def test_old_ics_scheme_id(self):
        """
        Check that the emited tag for the old ics is valid
        """
        self.creditor.ics = "FR00ZZ123456"
        self.creditor.old_ics = "FR00ZZ654321"
        to_check_tag = etree.tostring(self.creditor.emit_scheme_id_tag(mode='old'))
        self.assertEqual(self.valid_old_ics_id_tag, to_check_tag)
