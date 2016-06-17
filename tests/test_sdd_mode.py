# -*- coding: UTF-8 -*-

from unittest import TestCase
from lxml import etree
from sepacbi import SddFactory
from sepacbi.entity import MissingICSError


# Payment = SddFactory.get_payment()
# Transaction = SddFactory.get_transaction()
IdHolder = SddFactory.get_id_holder()

# initiator = IdHolder(name="Initiator Name")
#
# creditor = IdHolder(name="Creditor Name")
#
# ultimate_debtor = IdHolder(name="Ultimate Creditor")
#
# debtor_1 = IdHolder(name="Debtor One")
# debtor_2 = IdHolder(name="Debtor Two")
#
# ultimate_debtor = IdHolder(name="Ultimate Debtor")

# class TestEmitTag(Testcase):
#     """
#     Test class for the perform_checks() method.
#     """
#
#     id_holder = IdHolder()
#
#     def test_name_check(self):
#         """
#         Check that the length of the name of an ID holder is Tested.
#         """
#         self.id_holder.name = ""


class TestEmitSchemeIdTag(TestCase):
    """
    Test class for the emit_scheme_id_tag() method.
    """

    creditor = IdHolder()
    valid_ics_id_tag = b'<Id><PrvtId><Othr><Id>FR00ZZ123456</Id><SchmeNm><Prtry>SEPA</Prtry></SchmeNm></Othr></PrvtId></Id>'
    valid_old_ics_id_tag = b'<Id><PrvtId><Othr><Id>FR00ZZ654321</Id><SchmeNm><Prtry>SEPA</Prtry></SchmeNm></Othr></PrvtId></Id>'

    def test_missing_ics_error(self):
        """
        Check that the MissingICSError exception
        is raised when a creditor has no ICS code.
        """
        if hasattr(self.creditor, 'ics'):
            delattr(self.creditor, 'ics')
        with self.assertRaises(MissingICSError):
            self.creditor.emit_scheme_id_tag()

        self.creditor.ics = "FR00ZZ123456"
        if hasattr(self.creditor, 'old_ics'):
            delattr(self.creditor, 'old_ics')
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



# if __name__ == '__main__':
#     unittest.main()
