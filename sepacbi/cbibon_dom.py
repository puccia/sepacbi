
from .records import BaseRecord, AlphaNumericField, NumericField, \
    CBIDateField, CBIDecimalField


class CBIRecord(BaseRecord):
    @classmethod
    def builders(cls, nf=None):
        def nnf(fcls):
            def start(*a, **kw):
                m = fcls(*a, **kw)
                cls.bind(m)
            return start
        if nf is None:
            nf = nnf
        o = super(CBIRecord, cls).builders(nf=nf)
        o.dt = nf(CBIDateField)
        #     def __init__(self, len, name, cint, cdec, pos):
        o.cur = nf(CBIDecimalField)
        return o


class PCRecord(CBIRecord):
    @classmethod
    def define_fields(cls):
        f = cls.builders()
        f.an(1, 'filler', 1)
        f.an(2, 'record_type', 2, default=u'PC')
        f.an(4, 'sender', 5)
        f.nu(9, 'recipient', 5)
        f.dt(14, 'creation', 6)
        f.an(20, 'name', 20)
        f.an(40, 'available', 6)
        f.an(46, 'filler2', 61)
        f.an(105, 'flow_qualifier', 7)
        f.an(112, 'filler3', 1)
        f.an(113, 'prio', 1)
        f.an(114, 'currency_code', 1, default=u'E')
        f.an(115, 'filler4', 1)
        f.an(116, 'not_available', 5)


class EFRecord(CBIRecord):
    @classmethod
    def define_fields(cls):
        f = cls.builders()
        f.an(1, 'filler', 1)
        f.an(2, 'record_type', 2, default=u'EF')
        f.an(4, 'sender', 5)
        f.nu(9, 'recipient', 5)
        f.dt(14, 'creation', 6)
        f.an(20, 'name', 20)
        f.an(40, 'available', 6)
        f.nu(46, 'orders', 7)
        f.cur(52, 'negative_amounts', 15)
        f.cur(68, 'positive_amounts', 15)
        f.nu(83, 'records', 7)
        f.an(90, 'filler2', 23)
        f.an(113, 'prio', 1)
        f.an(114, 'currency_code', 1, default=u'E')
        f.an(115, 'not_available', 6)

# Record 10

class TransferInfo(CBIRecord):
    @classmethod
    def define_fields(cls):
        f = cls.builders()
        f.an(1, 'filler', 1)
        f.an(2, 'record_type', 2, default=u'10')
        f.nu(4, 'prog_number', 7)
        f.an(11, 'filler2', 6)
        f.dt(17, 'execution_date', 6)
        f.dt(23, 'payee_date', 6)
        f.an(29, 'purpose', 5)
        f.cur(34, 'amount', 13)
        f.an(47, 'sign', 1, default=u'+')
        f.nu(48, 'ord_abi', 5)
        f.nu(53, 'ord_cab', 5)
        f.an(58, 'ord_account', 12)
        f.nu(70, 'rec_abi', 5)
        f.nu(75, 'rec_cab', 5)
        f.nu(80, 'rec_account', 12)
        f.an(92, 'filler3', 22)
        f.nu(114, 'payment_method', 1, default=1)
        f.an(115, 'filler4', 4)
        f.an(119, 'prio', 1)
        f.an(120, 'currency_code', 1, default=u'E')


class PayerIBANInfo(CBIRecord):
    @classmethod
    def define_fields(cls):
        f = cls.builders()
        f.an(1, 'filler', 1)
        f.an(2, 'record_type', 2, default=u'16')
        f.nu(4, 'prog_number', 7)
        f.an(11, 'iban', 27)
        f.an(38, 'filler2', 83)


class PayeeIBANInfo(CBIRecord):
    @classmethod
    def define_fields(cls):
        f = cls.builders()
        f.an(1, 'filler', 1)
        f.an(2, 'record_type', 2, default=u'17')
        f.nu(4, 'prog_number', 7)
        f.an(11, 'iban', 27)
        f.an(38, 'filler2', 83)


class PayerInfo(CBIRecord):
    @classmethod
    def define_fields(cls):
        f = cls.builders()
        f.an(1, 'filler', 1)
        f.an(2, 'record_type', 2, default=u'20')
        f.nu(4, 'prog_number', 7)
        f.an(11, 'name', 30)
        f.an(41, 'address', 30)
        f.an(71, 'city', 30)
        f.an(101, 'tax_code', 16)
        f.an(117, 'filler2', 4)


class PayeeInfo(CBIRecord):
    @classmethod
    def define_fields(cls):
        f = cls.builders()
        f.an(1, 'filler', 1)
        f.an(2, 'record_type', 2, default=u'30')
        f.nu(4, 'prog_number', 7)
        f.an(11, 'name', 90)        
        f.an(101, 'tax_code', 16)
        f.an(117, 'filler2', 4)


class PayeeAddress(CBIRecord):
    @classmethod
    def define_fields(cls):
        f = cls.builders()
        f.an(1, 'filler', 1)
        f.an(2, 'record_type', 2, default=u'40')
        f.nu(4, 'prog_number', 7)
        f.an(11, 'address', 30)
        f.an(41, 'postal_code', 5)
        f.an(46, 'town', 25)
        f.an(71, 'bank', 50)


class PurposeInfo(CBIRecord):
    @classmethod
    def define_fields(cls):
        f = cls.builders()
        f.an(1, 'filler', 1)
        f.an(2, 'record_type', 2, default=u'50')  # may become 60
        f.nu(4, 'prog_number', 7)
        f.an(11, 'desc', 90)
        f.an(101, 'filler2', 20)


class StatusRequest(CBIRecord):
    @classmethod
    def define_fields(cls):
        f = cls.builders()
        f.an(1, 'filler', 1)
        f.an(2, 'record_type', 2, default=u'70')
        f.nu(4, 'prog_number', 7)
        f.an(11, 'filler2', 15)
        f.an(16, 'not_available', 15)
        f.an(31, 'flow_qualifier', 7)
        f.an(38, 'mp_code', 5)
        f.an(43, 'filler3', 26)
        f.an(70, 'status_request_flag', 1)
        f.an(71, 'unique_code', 30)
        f.an(101, 'filler4', 10)
        f.an(111, 'payee_cin', 1)
        f.an(112, 'filler5', 1)
        f.an(113, 'check_keys', 8)


