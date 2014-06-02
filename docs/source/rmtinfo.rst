EACT-compliant remittance information
=====================================

The module provides the ``Document``, ``Invoice``, ``CreditNote``, ``DebitNote`` and ``Text`` classes to help format the remittance information for a transaction.

This is done by specifying a tuple or list of one, or more, instances of these classes for the ``docs`` attribute of the ``Payment.add_transaction`` method.

.. class:: Document

	An instance of ``Document`` represents a single commercial document for which the transaction is issued. Its subclasses ``Invoice``, ``CreditNote`` and ``DebitNote`` are used in exactly the same way; only the rendered tag changes.

	..method:: __init__(self, number, amount=None, date=None)

		.. data:: number

			The document number, as specified by its issuer.

		.. data:: amount

			*(optional)* The amount paid for this document in the transaction. Used for partial payments.

		.. data:: date

			*(optional)* The document's date.

