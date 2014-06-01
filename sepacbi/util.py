#!/usr/bin/python

"""
This module provides a base class for the attribute-carrying objects
and other common utility functions.
"""

__copyright__ = 'Copyright (c) 2014 Emanuele Pucciarelli, C.O.R.P. s.n.c.'
__license__ = '3-clause BSD'

from warnings import warn
import sys


if sys.version_info[0] >= 3:
    # pylint: disable=redefined-builtin
    # pylint: disable=invalid-name
    unicode = str
    basestring = str


class AttributeCarrier(object):
    """
    Base class that provides utility methods.

    Each derived class has an allowed_args attribute, listing all instance
    attributes that can be set at initialization time by providing them
    as keyword arguments.

    Also, utility methods are provided to check the validity of the attributes
    and emit XML trees for the represented objects.
    """
    # pylint: disable=no-member

    allowed_args = ()  # Always redefined by derived classes.

    def __init__(self, **kwargs):
        self.process(kwargs, self.allowed_args)

    def process(self, kwargs, allowed_args, final=True):
        """
        Set allowed attributes on the object instance. Return dictionary without
        the processed attributes.
        """
        for arg in allowed_args:
            if arg in kwargs:
                setattr(self, arg, kwargs.pop(arg))
        if final and len(kwargs) > 0:
            raise TypeError('Invalid keyword arguments: %s' % kwargs.keys())
        return kwargs

    def __tag__(self, *args, **kwargs):
        """
        Return a XML tag for the object, after performing all the validity
        checks.
        """
        self.perform_checks()
        return self.emit_tag(*args, **kwargs)

    def max_length(self, attribute_name, length, obj=None):
        "Check that an attribute fits into the field length."
        if obj is None:
            obj = self
        value = unicode(getattr(obj, attribute_name))
        if len(value) < 1:
            raise Exception('Attribute %r cannot be empty' % attribute_name)
        if len(value) > length:
            warn('Attribute %r too long; truncating' % attribute_name,
                 stacklevel=4)
            setattr(obj, attribute_name, value[:length])
        else:
            setattr(obj, attribute_name, value)

    def length(self, attribute_name, length):
        "Check that an attribute has exactly the specified length."
        value = unicode(getattr(self, attribute_name))
        if len(value) != length:
            raise Exception(
                'Attribute %r must be %s characters long '
                '(supplied value: %r' % (attribute_name, length, value))
        setattr(self, attribute_name, value)

def booltext(param):
    "Returns a string suitable to represent a boolean value in a XML file."
    if param:
        return 'true'
    else:
        return 'false'
