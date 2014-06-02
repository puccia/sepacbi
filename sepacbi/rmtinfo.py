#!/usr/bin/python

"""
This module automatically prepares unstructured remittance information
according to the EACT standard.
"""

__copyright__ = 'Copyright (c) 2014 Emanuele Pucciarelli, C.O.R.P. s.n.c.'
__license__ = '3-clause BSD'


from decimal import Decimal
from .util import AttributeCarrier


class Document(AttributeCarrier):
    """
    The Document class represents a financial document that can be mentioned
    in the unstructured remittance information of a transaction.

    Please see the EACT Standard for Remittance Information:
    http://www.eact.eu/main.php?page=SEPA
    """

    tag = '/DOC/'

    def __init__(self, number, amount=None, date=None):
        """
        Argument processing is not based on keyword parameters, so we can't call
        `AttributeCarrier`'s `__init__()` method.
        """
        # pylint: disable=super-init-not-called
        self.number = number
        if amount:
            self.amount = amount
        if date:
            self.date = date

    def perform_checks(self):
        "Check the document number and, optionally, the date and amount."
        assert int(self.number) is not None
        if hasattr(self, 'date'):
            assert hasattr(self.date, 'strftime')
            assert hasattr(self, 'amount')
        if hasattr(self, 'amount'):
            if not isinstance(self.amount, Decimal):
                self.amount = Decimal(str(self.amount))

    def __str__(self):
        self.perform_checks()
        items = [str(self.number)]
        if hasattr(self, 'amount'):
            items += [str(self.amount.quantize(Decimal('.01')))]
        if hasattr(self, 'date'):
            items += [self.date.strftime('%Y%m%d')]
        return self.tag + '/ '.join(items)


class Invoice(Document):
    "Commercial invoice."
    tag = '/CINV/'


class CreditNote(Document):
    "Credit note."
    tag = '/CREN/'


class DebitNote(Document):
    "Debit note."
    tag = '/DEBN/'


class Text(Document):
    "Free text."
    # pylint: disable=super-init-not-called
    tag = '/TXT/'

    def __init__(self, text):
        self.text = text

    def perform_checks(self):
        assert hasattr(self, 'text')

    def __str__(self):
        # pylint: disable=no-member
        self.perform_checks()
        return self.tag + self.text
