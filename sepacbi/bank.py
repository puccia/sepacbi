#!/usr/bin/python
#pylint: disable=no-member

"""
Bank class.
"""

__copyright__ = 'Copyright (c) 2014 Emanuele Pucciarelli, C.O.R.P. s.n.c.'
__license__ = '3-clause BSD'

from .util import AttributeCarrier
from lxml import etree
import re

ABI_RE = re.compile(r'\d{5}')


class Bank(AttributeCarrier):
    """
    Represents a bank. It can show either a BIC code (for creditor banks)
    or an ABI code (for the debtor bank).
    """
    allowed_args = ('bic', 'abi')

    def perform_checks(self):
        'Checks that the BIC or the ABI are present, and that they are valid.'
        if hasattr(self, 'bic'):
            code_length = len(self.bic)
            # TODO: more formal checks (ISO 9362)
            assert code_length in (8, 11)
        if hasattr(self, 'abi'):
            assert ABI_RE.match(self.abi) is not None

    def emit_tag(self, output_abi=False):
        "Returns a XML tree for the bank, optionally providing the ABI code."
        root = etree.Element('FinInstnId')
        if hasattr(self, 'bic'):
            etree.SubElement(root, 'BIC').text = self.bic
        if output_abi:
            clearing = etree.SubElement(root, 'ClrSysMmbId')
            etree.SubElement(clearing, 'MmbId').text = self.abi
        return root
