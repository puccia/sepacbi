#!/usr/bin/python

"""
Import classes exposed as the API to consumer modules.
"""

__copyright__ = 'Copyright (c) 2014 Emanuele Pucciarelli, C.O.R.P. s.n.c.'
__license__ = '3-clause BSD'

from .entity import IdHolder
from .payment import Payment
from .rmtinfo import Document, Invoice, CreditNote, DebitNote, Text
from .transaction import Transaction

from lxml import etree

pr_prefix = 'urn:CBI:xsd:CBIPaymentRequest.00.04.00'

etree.register_namespace('pr', pr_prefix)
