Introduction
------------

The `sepacbi` module generates SEPA Credit Transfer requests in the XML format standardized by CBI and accepted by Italian banks. It can also generate very simple SEPA Direct Debit requests.

It is also capable of generating request streams in the legacy CBI-BON-001 fixed-length record legacy format, but only for domestic credit transfers.

The module does not currently support other requests (such as B2B), nor does it support status changes.

The development of this module is funded by `Linkspirit`_.

.. _Linkspirit: http://www.linkspirit.it/

Quick start
-----------

Each transfer request can include unlimited transactions and is prepared through the ``Payment``
class.

Debtors and creditors are instances of the ``IdHolder`` class.

Here is the generation of a very simple credit transfer request::

	from sepacbi import SctFactory

	Payment = SdctFactory.get_payment()
	Transaction = SctFactory.get_transaction()
	IdHolder = SctFactory.get_id_holder()

	payer = IdHolder(name='Sample Business S.P.A.', cf='12312312311', cuc='0123456A')

	payment = Payment(debtor=payer, account='IT 39P 06040 15400 000000138416')
	payment.add_transaction(
		creditor=IdHolder(name='John Smith'), account='IT83D 07601 01000 000010741106',
		amount=50.12, rmtinfo='Expense reimbursement'
	)

You will the obtain the generated XML request by invoking::

	payment.xml_text()
