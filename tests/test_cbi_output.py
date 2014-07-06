from sepacbi import Payment, Invoice, DebitNote, Text
from .definitions import *
import re
import sys
from datetime import datetime, date

from lxml import etree

PYTHON3 = False
if sys.version_info[0] >= 3:
    PYTHON3 = True

def canonicalize_cbi(text):
    today = date.today().strftime('%d%m%Y')
    return text.replace(today, '999999')

def compare_cbi(text, filename, save=False):
    """
    Compare a generated XML tree with the content of a specific file.
    """
    from os.path import dirname, join
    full_path = join(dirname(__file__), filename)
    if save:
        open(full_path, 'w').write(canonicalize_cbi(text))
        #raise Exception('saved!')
    file_content = open(full_path, 'r').read()
    assert text == file_content


def test_payment_basic():
    payment = Payment(debtor=biz_with_sia, account=acct_37, req_id='StaticId',
                      execution_date=date(2014, 5, 15))
    payment.add_transaction(amount=198.25, account=acct_86, creditor=beta,
                            rmtinfo='Causale 1')
    compare_cbi(payment.cbi_text(), 'payment_basic.txt')


def test_payment_multitrans():
    payment = Payment(debtor=biz_with_sia, account=acct_37, req_id='StaticId',
                      execution_date=date(2014, 5, 15))
    payment.add_transaction(amount=198.25, account=acct_86, creditor=beta,
                            rmtinfo='Causale 1')
    payment.add_transaction(amount=350.00, account=acct_37,
                            creditor=biz_with_sia,
                            rmtinfo='Altra causale')
    payment.add_transaction(amount=9532.21, account=acct_86,
                            bic='ABCDESNN', creditor=alpha,
                            docs=[Invoice(18512, 4500),
                                  DebitNote(1048, 5032.21,
                                            date(1995, 4, 21))])
    payment.add_transaction(
        amount=1242.80, creditor=pvt, account=acct_86,
        category='SALA', rmtinfo='Salary')

    compare_cbi(payment.cbi_text(), 'payment_multitrans.txt')


def test_payment_misc_features():
    payment = Payment(
        debtor=biz, account=acct_37, req_id='StaticId',
        execution_date=date(2014, 5, 15),
        ultimate_debtor=beta, charges_account=acct_86, envelope=True,
        initiator=biz_with_sia, batch=True, high_priority=True)
    payment.add_transaction(amount=198.25, account=acct_86, creditor=beta,
                            rmtinfo='Causale 1')
    compare_cbi(payment.cbi_text(), 'payment_misc_1.txt')

    payment.high_priority = False
    payment.add_transaction(amount=350.00, account=acct_37,
                            creditor=biz_with_cuc,
                            rmtinfo='Altra causale')
    payment.add_transaction(amount=9532.21, account=acct_86,
                            bic='ABCDESNN', creditor=alpha,
                            docs=[Invoice(18512, 4500, date(2009, 7, 17)),
                                  DebitNote(1048, 5032.21,
                                            date(1995, 4, 21))])
    payment.add_transaction(
        amount=1242.80, creditor=pvt, account=acct_86,
        category='SALA', docs=[Text('Salary payment')])

    compare_cbi(payment.cbi_text(), 'payment_misc_2.txt')
