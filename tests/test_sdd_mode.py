# -*- coding: UTF-8 -*-

from unittest import TestCase
from lxml import etree
from sepacbi import SddFactory
from sepacbi.entity import MissingICSError


Payment = SddFactory.get_payment()
Transaction = SddFactory.get_transaction()
IdHolder = SddFactory.get_id_holder()

initiator = IdHolder(name="Initiator Name")

creditor = IdHolder(name="Creditor Name")

ultimate_debtor = IdHolder(name="Ultimate Creditor")

debtor_1 = IdHolder(name="Debtor One")
debtor_2 = IdHolder(name="Debtor Two")

ultimate_debtor = IdHolder(name="Ultimate Debtor")

class TestEmitSchemeIdTag(TestCase):

    valid_ics_id_tag = b'<Id><PrvtId><Othr><Id>FR00ZZ123456</Id><SchmeNm><Prtry>SEPA</Prtry><SchmeNm></Othr></PrvtId></Id>'

    def test_missing_ics_error(self):
        """
        Check that the MissingICSError exception
        is raised when a creditor has no ICS code.
        """
        with self.assertRaises(MissingICSError):
            creditor.emit_scheme_id_tag()

        creditor.ics="FR00ZZ123456"
        with self.assertRaises(MissingICSError):
            creditor.emit_scheme_id_tag(mode='old')

    def test_ics_scheme_id(self):
        """
        Check that the emited tag for the ics is valid
        """
        creditor.ics="FR00ZZ123456"
        to_check_tag = etree.tostring(creditor.emit_scheme_id_tag())
        self.assertEqual(self.valid_ics_id_tag, to_check_tag)


# if __name__ == '__main__':
#     unittest.main()
