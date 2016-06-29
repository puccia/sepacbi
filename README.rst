.. image:: https://travis-ci.org/yhillion/sepacbi.svg?branch=sdd-support
    :target: https://travis-ci.org/yhillion/sepacbi
.. image:: https://coveralls.io/repos/github/yhillion/sepacbi/badge.svg?branch=sdd-support
    :target: https://coveralls.io/github/yhillion/sepacbi?branch=sdd-support
.. image:: https://landscape.io/github/yhillion/sepacbi/sdd-support/landscape.svg?style=flat
   :target: https://landscape.io/github/yhillion/sepacbi/sdd-support
   :alt: Code Health

SEPA Credit Transfer (CBI) request generator
--------------------------------------------

The `sepacbi` module generates SEPA Credit Transfer requests in the XML format standardized by CBI and accepted by Italian banks. It can also generate very simple SEPA Direct Debit requests.

It is also capable of generating request streams in the legacy CBI-BON-001 fixed-length record legacy format, but only for domestic credit transfers.

The module does not currently support other requests (such as B2B), nor does it support status changes.

The development of this module is funded by `Linkspirit`_.

.. _Linkspirit: http://www.linkspirit.it/
