import pytest

from sepacbi import IdHolder, Payment

from sepacbi.payment import NoTransactionsError, MissingABIError, \
    InvalidEndToEndIDError
from sepacbi.entity import MissingCUCError, AddressFormatError
from sepacbi.transaction import MissingBICError
from sepacbi.rmtinfo import Invoice
from sepacbi.iban import InvalidIBANError

from .definitions import *


def test_empty_payment():
    "Payments without any transaction must raise an exception."
    with pytest.raises(NoTransactionsError):
        payment = Payment(
            debtor=biz_with_cuc,
            account=acct_86,
            abi='01101',
            envelope=False
        )
        payment.xml()


def test_missing_attrs_payment():
    "Payments must always have a `debtor` and an `account` attribute."
    payment = Payment()
    with pytest.raises(AttributeError):
        payment.xml()

    payment.debtor = biz_with_cuc
    with pytest.raises(AttributeError):
        payment.xml()

    payment.account = acct_37

    # No exception must be raised
    payment.add_transaction(amount=1, account=acct_86,
                            rmtinfo='Test', creditor=biz)
    payment.xml()


def gen_dictionaries_with_one_missing_item(full_dictionary):
    """
    Takes an input dictionary and yields all possible dictionaries
    with the same data, except for one single key/value pair.
    """
    for item in full_dictionary:
        incomplete = dict([(key, full_dictionary[key])
                           for key in full_dictionary if key != item])
        yield incomplete


def simple_payment():
    return Payment(debtor=biz_with_cuc, account=acct_37)


def test_missing_attr_transaction():
    """
    Transactions must always have `amount`, `account`, `rmtinfo`,
    `creditor`.
    """
    basic_data = {
        'amount': 1,
        'account': acct_86,
        'creditor': biz,
    }
    for params in gen_dictionaries_with_one_missing_item(basic_data):
        payment = Payment(debtor=biz_with_cuc, account=acct_37)
        params['rmtinfo'] = 'Test'
        with pytest.raises(AttributeError):
            payment.add_transaction(**params)
            payment.xml()
    
    payment = simple_payment()
    with pytest.raises(AssertionError):
        payment.add_transaction(**basic_data)
        

def test_missing_CUC():
    "The `debtor` entity must always have a CUC."
    payment = Payment(debtor=biz, account=acct_37)
    payment.add_transaction(amount=1, account=acct_86, creditor=biz,
                            rmtinfo='Test')
    with pytest.raises(MissingCUCError):
        payment.xml()


def test_wrong_address_format():
    "Address must be a list or tuple of at most two lines."
    holder = IdHolder(
        name='Test Business S.P.A.', cf='12312312311',
        country='IT', address=['Xyz', 'Via Giuseppe Verdi, 15', '33100 Udine'],
        cuc='XYZZZZ')

    payment = Payment(debtor=holder, account=acct_37)
    payment.add_transaction(amount=1, account=acct_86, docs=(Invoice(1),),
                            creditor=alpha)
    with pytest.raises(AddressFormatError):
        payment.xml()
    holder.address = [
        'A single line which is too long to fit in the holder address '
        'field, which can hold at most 70 characters per line',
        'test'
    ]
    with pytest.raises(AddressFormatError):
        payment.xml()


def test_missing_abi():
    "If the debtor has a foreign account, the ABI must be supplied."
    payment = Payment(debtor=biz_with_cuc, account=foreign_acct)
    payment.add_transaction(amount=1, account=acct_86, rmtinfo='Test')
    with pytest.raises(MissingABIError):
        payment.xml()


def test_missing_bic():
    "If the creditor has a foreign account, the BIC must be supplied."
    payment = simple_payment()
    with pytest.raises(MissingBICError):
        payment.add_transaction(amount=1, account=foreign_acct, creditor=biz,
                                rmtinfo='Test')


def test_invalid_iban():
    payment = Payment(debtor=biz_with_cuc, account='ITINVALIDIBAN')
    with pytest.raises(InvalidIBANError):
        payment.xml()

    payment.account = 'XXINVALIDIBAN'
    payment.abi = '01234'
    with pytest.raises(InvalidIBANError):
        payment.xml()

    payment.account = acct_37.replace('IT37', 'IT99')
    with pytest.raises(InvalidIBANError):
        payment.xml()


def test_invalid_docs():
    payment = simple_payment()
    with pytest.raises(TypeError):
        payment.add_transaction(amount=100, account=acct_86, creditor=biz,
                                docs=[Invoice()])


def test_dup_e2eid():
    payment = simple_payment()
    payment.add_transaction(amount=1, creditor=alpha, account=acct_37,
                            eeid='Test1', rmtinfo='A')
    with pytest.raises(InvalidEndToEndIDError):
        payment.add_transaction(amount=2, creditor=beta, account=acct_37,
                                eeid='Test1', rmtinfo='B')
