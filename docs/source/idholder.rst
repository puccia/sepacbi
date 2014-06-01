The ``IdHolder`` class
======================

.. class:: IdHolder

	An instance of the ``IdHolder`` class represents a single person. (By "person" we mean a natural person, a juridical person or another such entity.) It can be used as an initiator (the entity who requests the credit transfer), as the debtor for the request (whose account will be debited), or the creditor for a single transaction.

	..	data:: name

		The name of the person.

	..	data:: address

		A tuple of one or two strings representing the postal address for the person.

	.. data:: cf

		The Italian "codice fiscale" for the person (government-issued tax code). Either ``cf`` or ``code`` must be used, but not both, for the same person.

	.. data:: code

		Another code for the person – usually a government-assigned one, but *not* the Italian "codice fiscale". Used for non-Italian persons. Do not use along with ``cf`` for the same person.

	.. data:: country

		The two-letter ISO code for the person's country of residence.

	.. data:: cuc

		The CBI-issued CUC for the person. This is only used when the person is the initiator of a transfer, otherwise it is ignored.

		The CUC is usually communicated by the bank to the customer who wants to issue SEPA credit transfer requests.

