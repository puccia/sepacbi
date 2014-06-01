from copy import copy

from sepacbi import IdHolder


biz = IdHolder(name='Test Business S.P.A.', cf='12312312311',
               country='IT', address=['Via Giuseppe Verdi, 15', '33100 Udine'])

pvt = IdHolder(name='Mario Rossi', cf='RSSMRA50C10F842H',
               country='IT', private=True)

biz_with_cuc = copy(biz)
biz_with_cuc.cuc = 'S0215325Z'
acct_86 = 'IT 86 U 07601 11500 000010117463'
acct_37 = 'IT37Z0760101600000028426203'
foreign_acct = 'ES38 2100 1579 8002 0025 5488'

alpha = IdHolder(
    name='Alpha s.r.l.', cf='IT01234567890', country='IT',
    address=('Piazza Rossini, 8/A', '44044 Xyz'))
beta = IdHolder(name='Beta s.n.c.', code='ESQ01231244')
