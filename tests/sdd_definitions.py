# -*- coding:UTF-8 -*-

from sepacbi import SddFactory

IdHolder = SddFactory.get_id_holder()

creditor = IdHolder(name='Creditor Name', ics='FRZZZ123456',
                    address=('Cr Addr Line 1', 'Cr Addr Line 2'), country='FR')

ultimate_creditor = IdHolder(name='Ultimate Creditor', identifier='UC-ID')

debtor1 = IdHolder(name='Debtor 1')
debtor2 = IdHolder(name='Debtor 2', address=('D2 Addr Line 1'), country='FR')

ultimate_debtor = IdHolder(name='Ultimate Debtor')
