#!/usr/bin/python

"""
Bank accounts.
"""

__copyright__ = 'Copyright (c) 2014 Emanuele Pucciarelli, C.O.R.P. s.n.c.'
__license__ = '3-clause BSD'

from .util import AttributeCarrier
from lxml import etree


class Account(AttributeCarrier):
    """
    The Account class represents a bank account, identified by an IBAN.
    """
    allowed_args = ('iban',)

    def __init__(self, *args, **kwargs):
        self.iban = ''
        super(Account, self).__init__(*args, **kwargs)
        self.clean_iban()

    def clean_iban(self):
        "Canonicalize the IBAN."
        self.iban = self.iban.upper().replace(' ', '')

    def is_foreign(self):
        """
        Return a boolean value telling whether the IBAN designates a foreign
        account (from the viewpoint by the Italian banking system).
        """
        return self.iban[:2] not in ('IT', 'SM')

    def perform_checks(self):
        "Validates the IBAN."
        from . import iban
        self.clean_iban()
        iban.validate(self.iban)

    def emit_tag(self, tag):
        "Emit a XML tag using the provided string for the root element."
        root = etree.Element(tag)
        acct_id = etree.SubElement(root, 'Id')
        etree.SubElement(acct_id, 'IBAN').text = self.iban
        return root
