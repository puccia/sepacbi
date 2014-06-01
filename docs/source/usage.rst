
Usage
=====

The module exports the ``IdHolder``, ``Payment`` and ``Transaction`` classes. They are the building blocks for the SEPA credit transfer (SCT) requests.

Each of these classes' constructors takes optional keyword arguments.  You can supply the attributes either via the constructors, or by setting them on the instances. In other words::

	payment = Payment(account='ITxxxx')

and::

	payment = Payment()
	payment.account = 'ITxxxx'

accomplish the same thing.

The module also exports the ``Document``, ``Invoice``, ``CreditNote``, ``DebitNote``, ``Text`` classes that can be used to build the unstructured remittance information field according to the EACT standard.

