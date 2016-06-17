#!/usr/bin/python

"""
Bank accounts.
"""

from lxml import etree
from .util import AttributeCarrier

__copyright__ = 'Copyright (c) 2014 Emanuele Pucciarelli, C.O.R.P. s.n.c.'
__license__ = '3-clause BSD'


class MissingCUCError(Exception):
    """
    Raised when an Entity without a `cuc` attribute is used as an initiator.
    """
    pass

class MissingICSError(Exception):
    """
    Raised when an Entity whitout an 'ICS' attribute is used as a creditor.
    """
    pass

class AddressFormatError(Exception):
    """
    Raised when an Address is created with unsuitable arguments.
    """

class Address(AttributeCarrier):
    """
    The postal address of an entity for the SEPA SCT request mode.
    """
    def __init__(self, *args):
        """
        The argument processing is NOT based on keyword parameters, so we
        cannot inherit from AttributeCarrier.
        """
        # pylint: disable=super-init-not-called
        self.lines = args

    def perform_checks(self):
        """
        Check the length of each line.
        """
        line_count = len(self.lines)
        if line_count < 1 or line_count > 2:
            raise AddressFormatError('Must have either 1 or 2 address lines')
        for line in self.lines:
            if len(line) < 1 or len(line) > 70:
                raise AddressFormatError('Line must have length '
                                         'between 1 and 70 characters')

    def emit_tag(self):
        """
        Emit the postal address with each of its lines.
        """
        # pylint: disable=no-member
        root = etree.Element('PstlAdr')
        for line in self.lines:
            etree.SubElement(root, 'AdrLine').text = line
        return root


def emit_id_tag(id_code, id_type=None):
    """
    Emit a single ID subtree, with root <Othr>.
    """
    # pylint: disable=no-member
    othr = etree.Element('Othr')
    id_tag = etree.SubElement(othr, 'Id')
    id_tag.text = id_code
    if id_type is not 'scheme_id' and id_type is not None:
        issuer = etree.SubElement(othr, 'Issr')
        issuer.text = id_type
    elif id_type is 'scheme_id':
        schmenm = etree.SubElement(othr, 'SchmeNm')
        etree.SubElement(schmenm, 'Prtry').text = 'SEPA'
    return othr


class IdHolder(AttributeCarrier):
    """
    Describes an Initiator.
    Must have a CUC; may have an Italian tax code.
    """

    def __init__(self, **kwargs):
        self.private = False
        super(IdHolder, self).__init__(**kwargs)

#SCT Mode attributes and methods

sct_allowed_args = ('name', 'cf', 'code', 'private', 'cuc',
                    'address', 'country', 'sia_code')

def sct_perform_checks(self):
    # pylint: disable=access-member-before-definition
    # pylint: disable=attribute-defined-outside-init
    """
    Check argument lengths.
    """
    if hasattr(self, 'name'):
        self.max_length('name', 70)
    if hasattr(self, 'cf'):
        assert not hasattr(self, 'code')
        self.max_length('cf', 16)
    if hasattr(self, 'cuc'):
        self.max_length('cuc', 35)
    if hasattr(self, 'address'):
        if isinstance(self.address, (list, tuple)):
            self.address = Address(*self.address)
        assert isinstance(self.address, Address)
    if hasattr(self, 'country'):
        self.length('country', 2)

def sct_emit_tag(self, tag=None, as_initiator=False):
    """
    Emit a subtree for an entity, using the supplied tag for the root
    element. If the identity is the Initiator's, emit the CUC as well.
    """
    # pylint: disable=no-member
    if as_initiator:
        tag = 'InitgPty'
    root = etree.Element(tag)

    # Name
    if hasattr(self, 'name'):
        name = etree.SubElement(root, 'Nm')
        name.text = self.name

    # Address
    if hasattr(self, 'address') and not as_initiator:
        root.append(self.address.__tag__())

    # ID
    idtag = etree.SubElement(root, 'Id')
    if self.private:
        id_container = 'PrvtId'
    else:
        id_container = 'OrgId'
    orgid = etree.SubElement(idtag, id_container)

    # CUC
    if as_initiator:
        if not hasattr(self, 'cuc'):
            raise MissingCUCError
        orgid.append(emit_id_tag(self.cuc, 'CBI'))

    # Tax code
    if hasattr(self, 'cf'):
        orgid.append(emit_id_tag(self.cf, 'ADE'))

    if hasattr(self, 'code'):
        orgid.append(emit_id_tag(self.code, None))

    if not as_initiator and hasattr(self, 'country'):
        etree.SubElement(root, 'CtryOfRes').text = self.country

    return root

sct_idholder_attr_dict = {'allowed_args' : sct_allowed_args,
                          'perform_checks' : sct_perform_checks,
                          'emit_tag' : sct_emit_tag,
                         }

# SDD Mode attributes and methods

sdd_allowed_args = ('name', 'old_name', 'private', 'identifier',
                    'ics', 'old_ics', 'address', 'country')

def sdd_perform_checks(self):
    # pylint: disable=access-member-before-definition
    # pylint: disable=attribute-defined-outside-init
    """
    Check argument lengths.
    """
    if hasattr(self, 'name'):
        self.max_length('name', 70)

    if hasattr(self, 'old_name'):
        self.max_length('old_name', 70)

    if hasattr(self, 'identifier'):
        self.max_length('identifier', 35)

    if hasattr(self, 'ics'):
        self.max_length('ics', 35)

    if hasattr(self, 'old_ics'):
        self.max_length('old_ics', 35)

    if hasattr(self, 'address'):
        if isinstance(self.address, (list, tuple)):
            self.address = Address(*self.address)
        assert isinstance(self.address, Address)

    if hasattr(self, 'country'):
        self.length('country', 2)

def sdd_emit_tag(self, tag=None):
    """
    Emit a subtree for an entity, using the supplied tag for the root
    element.
    """
    # pylint: disable=no-member

    root = etree.Element(tag)

    # Name
    if hasattr(self, 'name'):
        name = etree.SubElement(root, 'Nm')
        name.text = self.name

    # Address
    if hasattr(self, 'address'):
        root.append(self.address.__tag__())

    # ID
    if hasattr(self, 'identifier'):
        idtag = etree.SubElement(root, 'Id')
        if self.private:
            id_container = 'PrvtId'
        else:
            id_container = 'OrgId'
        orgid = etree.SubElement(idtag, id_container)
        orgid.append(emit_id_tag(self.identifier, None))

    # Country
    if hasattr(self, 'country'):
        etree.SubElement(root, 'CtryOfRes').text = self.country
    return root

def sdd_emit_scheme_id_tag(self, mode=None):
    """
    For a creditor, emits the scheme id tag
    """
    # pylint: disable=no-member
    if not hasattr(self, 'ics'):
        raise MissingICSError
    idtag = etree.Element('Id')
    prvtid = etree.SubElement(idtag, 'PrvtId')
    if mode is 'old':
        if not hasattr(self, 'old_ics'):
            raise MissingICSError("The old ICS is needed here")
        prvtid.append(emit_id_tag(self.old_ics, 'scheme_id'))
    else:
        prvtid.append(emit_id_tag(self.ics, 'scheme_id'))
    return idtag

sdd_idholder_attr_dict = {'allowed_args' : sdd_allowed_args,
                          'perform_checks' : sdd_perform_checks,
                          'emit_tag' : sdd_emit_tag,
                          'emit_scheme_id_tag' : sdd_emit_scheme_id_tag
                         }
