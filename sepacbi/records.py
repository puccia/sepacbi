import copy
from unidecode import unidecode
from datetime import date
from decimal import Decimal
from six import add_metaclass


class Ordered(object):
    def set_order(self, order):
        self.order = order


class BaseField(Ordered):
    """
    A field in a (fixed-size) text record.
    """
    @classmethod
    def newfield(cls, recordcls, pos, **fields):
        """
        Creates a field with the given name and length, then binds it
        with the given containing record or composite field.
        """
        if len(fields) > 1:
            raise Exception('Multiple k/w values not supported')
        items = list(fields.items())
        name = items[0][0]
        flen = items[0][1]
        instance = cls(pos, name, flen)
        recordcls.bind(instance)

    @classmethod
    def alt_newfield(cls, recordcls, flen, name, pos, **kwargs):
        """
        Alternate method to create and bind a field.
        """
        instance = cls(pos, name, flen, **kwargs)
        recordcls.bind(instance)

    def __init__(self, pos, name, flen, default=None):
        """
        Fields and records have fixed positions and sizes.
        Position, name, field length are the same for every record, so
        they belong to the descriptor.
        The stored value changes, so it belongs to the instance.
        """
        self.name = name
        self.pos = pos
        self._flen = flen

        if default is not None:
            self.__dict__['_default_value'] = default

    def __get__(self, obj, type=None):
        """
        Fields never store the original value; they just delegate the instance
        so that it can store their exported representation.
        """
        raise NotImplementedError('Error: self=%r, obj=%r, type=%r' % (self, obj, type))

    def __set__(self, obj, value):
        """
        Ask the instance to store the exported representation of the value.
        """
        obj.write_field(self.order, self.format(value))

    def format(self, value):
        """
        Format the value; raise an exception if the size is wrong, as every
        exported field has a fixed size.
        """
        s = self._specialized_format(value)
        if len(s) != self.size:
            raise Exception('Could not format properly value %r' % value)
        return s

    @property
    def size(self):
        "Return the exported field size in characters."
        return self._flen

    def get_default(self):
        "Return the exported representation of the default value."
        return [self.format(self._default_value)]

    slot_count = 1


class FieldContainerMeta(type):
    """
    A class containing a field, such as a record or a composite field,
    must perform this procedure upon initialization.
    """
    def __new__(*args, **kwargs):
        c = type.__new__(*args, **kwargs)
        c.pos = 1
        c.field_count = 0
        c.fields = []
        c.define_fields()
        c.set_defaults()
        return c


class FieldContainerMixin(object):
    "Common methods for all field containers (records and composite fields)."
    @classmethod
    def bind(cls, field):
        """
        Bind a field instance with this class.
        """
        if field.name in cls.__dict__:
            raise 'Already has a field with this name'
        #if field.pos != cls.pos:
        #   raise Exception('Offset error: field %r is defined at position %s,'
        #       ' but class %r is at position %s' % (field.name, field.pos,
        #           cls.__name__, cls.pos))
        setattr(cls, field.name, field)
        cls.fields.append(field)
        field.set_order(cls.field_count)
        cls.field_count += field.slot_count
        cls.pos += field.size

    @classmethod
    def set_defaults(cls):
        lofl = [f.get_default() for f in cls.fields]
        cls._defaults = [val for subl in lofl for val in subl]

    @classmethod
    def define_fields(cls):
        pass

    @classmethod
    def builders(cls, nf=None):
        class Builder(object):
            pass
        o = Builder()
        if nf is None:
            nf = lambda fcls: lambda *a, **kw: fcls.alt_newfield(cls, *a, **kw)
        o.an = nf(AlphaNumericField)
        o.nu = nf(NumericField)
        o.dc = nf(DecimalField)
        o.dt = nf(DateField)
        o.sn = nf(SNField)
        return o

    @classmethod
    def kw_builders(cls):
        return cls.builders(
            nf=lambda fcls: lambda *a, **kw:
            fcls.newfield(cls, *a, **kw))


class SubfieldAccessor(object):
    def __init__(self, itemaccessor, num):
        self.__dict__['record'] = itemaccessor.record
        self.__dict__['compositefield'] = itemaccessor.compositefield
        self.num = num

    def __setattr__(self, name, value):
        if name in self.compositefield.__class__.__dict__:
            field = self.compositefield.__class__.__dict__[name]
            offset = self.compositefield.field_count*self.num + \
                field.order + self.compositefield.order
            self.record.write_field(offset, field.format(value))
        else:
            object.__setattr__(self, name, value)


class ItemAccessor(object):
    def __init__(self, compositefield, record):
        self.compositefield = compositefield
        self.record = record

    def __getitem__(self, num):
        if num > self.compositefield.repetitions:
            raise IndexError
        return SubfieldAccessor(self, num)


@add_metaclass(FieldContainerMeta)
class CompositeField(FieldContainerMixin, Ordered):
    """
    A field that can be repeated and contain multiple compositefields.
    """

    __metaclass__ = FieldContainerMeta

    def __get__(self, obj, type=None):
        return ItemAccessor(self, obj)

    def __set__(self, obj, value):
        raise NotImplementedError

    def __init__(self, name, repetitions, offset):
        self.name = name
        self.repetitions = repetitions
        self.pos = offset
        self._total_size = sum([f.size for f in self.fields])*repetitions

    @property
    def slot_count(self):
        return self.field_count*self.repetitions

    @property
    def size(self):
        return self._total_size

    def get_default(self):
        lofl = self.repetitions*[f.get_default() for f in self.fields]
        m = [val for subl in lofl for val in subl]
        return m


@add_metaclass(FieldContainerMeta)
class BaseRecord(FieldContainerMixin):
    __metaclass__ = FieldContainerMeta

    def __init__(self):
        """
        Copy default values from class when creating instance.
        Then, prepare compositefield accessors.
        """
        self._values = copy.copy(self._defaults)

    def write_field(self, field, value):
        self._values[field] = value

    def format(self):
        return ''.join(self._values)

    def debug_format(self):
        return '%r' % self._values


##########################
# Useful implementations #
##########################


class AlphaNumericField(BaseField):
    def _specialized_format(self, value):
        r = unidecode(value).strip().replace(
            '\x0d\x0a', '\x0a').replace('\x0a', ' / ').ljust(self._flen)
        if len(r) > self._flen:
            r = r[:self._flen]
        return r

    _default_value = u''


class NumericField(BaseField):
    def _specialized_format(self, value):
        if value is None:
            return u' '*self._flen
        return str(int(value)).rjust(self._flen)

    _default_value = None


class SNField(BaseField):
    def _specialized_format(self, value):
        v = bool(value)
        if v:
            return 'S'
        else:
            return 'N'

    _default_value = False


class DateField(BaseField):
    def __init__(self, *args, **kwargs):
        super(DateField, self).__init__(*args, **kwargs)
        if self._flen != 8:
            raise Exception('Invalid length for DateField')

    def _specialized_format(self, value):
        if value is None:
            return '00000000'
        elif isinstance(value, date):
            return value.strftime('%d%m%Y')
        else:
            raise Exception('Invalid type for date: %s' % type(value))

    _default_value = None


class CBIDateField(BaseField):
    def __init__(self, *args, **kwargs):
        super(CBIDateField, self).__init__(*args, **kwargs)
        if self._flen != 6:
            raise Exception('Invalid length for CBIDateField: %s' % self._flen)

    def _specialized_format(self, value):
        if value is None:
            return '      '
        elif hasattr(value, 'strftime'):
            return value.strftime('%d%m%y')
        else:
            raise Exception('Invalid type for date: %r' % value)

    _default_value = None

class DecimalField(BaseField):
    def __init__(self, len, name, cint, cdec, pos):
        if cint+cdec != len:
            raise Exception('Invalid lengths for field')
        super(DecimalField, self).__init__(pos, name, len)
        self.cint = cint
        self.cdec = cdec
        self.multiplier = Decimal(10**self.cdec)

    @classmethod
    def alt_newfield(cls, recordcls, *args):
        instance = cls(*args)
        recordcls.bind(instance)

    def _specialized_format(self, value):
        if value is None:
            value = Decimal(0)
        return str((value * self.multiplier).to_integral()).rjust(self._flen)

    _default_value = None


class CBIDecimalField(DecimalField):
    def __init__(self, pos, name, flen, default=None):
        super(CBIDecimalField, self).__init__(flen, name, flen-2, 2, pos)

######################
# Examples and tests #
######################


class ExampleCompositeField(CompositeField):
    @classmethod
    def define_fields(cls):
        f = lambda *a, **k: AlphaNumericField.newfield(cls, *a, **k)
        f(31, hi=3)
        f(35, earth=5)


class ExampleRecord(BaseRecord):
    @classmethod
    def define_fields(cls):
        f = cls.kw_builders()
        f.an(1, hello=10)
        f.an(11, world=20)
        cls.bind(ExampleCompositeField('repeat', 5, 31))
        f.an(71, ending=8)


if __name__ == '__main__':
    r = ExampleRecord()
    r.world = u'myWorld'
    r.repeat[0].hi = u'a'
    r.repeat[0].earth = u'b'
    r.repeat[1].hi = u'c'
    r.repeat[4].hi = u'm'
    r.ending = u'mw'
    print(r.debug_format())
    print('%r' % r.format())
