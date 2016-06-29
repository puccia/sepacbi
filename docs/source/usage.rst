
Usage
=====

The module exports the ``SctFactory`` and ``SddFactory`` classes. The first thing to do is to import one, and only one, of them, depending on the mode you need to run.

For the SCT mode::

	from sepacbi import SctFactory

For the SDD mode::

	from sepacbi import SddFactory

They provide three methods :  ``get_payment``, ``get_transaction`` and ``get_id_holder``. Each of these methods returns the ``IdHolder``, ``Payment`` and ``Transaction`` classes. They are the building blocks for the SEPA requests, in credit transfer (SCT) or direct debit (SDD) mode.
To load these classes in SCT mode, do as follow::

	Payment = SdctFactory.get_payment()
	Transaction = SctFactory.get_transaction()
	IdHolder = SctFactory.get_id_holder()

Each of these classes' constructors takes optional keyword arguments.  You can supply the attributes either via the constructors, or by setting them on the instances. In other words::

	payment = Payment(account='ITxxxx')

and::

	payment = Payment()
	payment.account = 'ITxxxx'

accomplish the same thing.

In SCT mode, the module also exports the ``Document``, ``Invoice``, ``CreditNote``, ``DebitNote``, ``Text`` classes that can be used to build the unstructured remittance information field according to the EACT standard.
In SDD mode, the purpose and remittance informations are not supported
