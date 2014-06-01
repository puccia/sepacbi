#!/usr/bin/python

"""
This module deals with IBAN codes and formal validity checks.
"""

__copyright__ = 'Copyright (c) 2014 Emanuele Pucciarelli, C.O.R.P. s.n.c.'
__license__ = '3-clause BSD'

import re
from .iban_structures import IBAN_STRUCTURES

# Identifies a single element of the IBAN structure
STR_ITEM_RE = re.compile(r'^(\d+)(!?)([nac])')


class InvalidIBANError(Exception):
    "Raised when an IBAN does not pass the formal checks."
    pass


def structure_to_re(structure):
    """
    Convert a SWIFT IBAN structure description to a regex that matches it.
    """
    # First part of the regex
    regex = ['^', structure[:2]]
    # Skip the first two characters
    idx = 2
    while idx < len(structure):
        # Get the next segment
        pattern = STR_ITEM_RE.search(structure[idx:])
        idx += len(pattern.group(0))

        # The part length
        length = int(pattern.group(1))

        # Whether it is fixed or a maximum length
        fixed = pattern.group(2) != ''

        # 'n' is a digit; 'a' an uppercase character;
        # 'c' an alphanumeric character
        item_type = pattern.group(3)

        # compose the next regex segment
        if item_type == 'n':
            sub_re = r'\d'
        elif item_type == 'a':
            sub_re = r'[A-Z]'
        elif item_type == 'c':
            sub_re = r'[\dA-Za-z]'
        else:
            raise Exception('Invalid structure: %s' % structure)

        if fixed:
            sub_re += r'{%s}' % length
        else:
            sub_re += r'{,%s}' % length
        regex.append(sub_re)
    regex.append('$')
    regex = ''.join(regex)
    # Return the finished and compiled regex
    return re.compile(regex)


# Fill a dictionary with the compiled regular expressions
COUNTRY_RE = dict([(x[:2], structure_to_re(x))
                   for x in IBAN_STRUCTURES])


def validate_check_digits(iban):
    "Validate the check digits of an IBAN."
    iban = iban[4:] + iban[:4]

    converted = int(''.join(str(int(ch, 36)) for ch in iban))

    if int(converted) % 97 != 1:
        raise InvalidIBANError('Invalid check digits')


def validate(iban):
    "Validate the structure and the check digits of an IBAN."

    # Do we know the country?
    country = iban[:2]
    if country not in COUNTRY_RE:
        raise InvalidIBANError('Invalid country code')

    # Is the formal structure valid?
    if not COUNTRY_RE[country].match(iban):
        raise InvalidIBANError('Invalid IBAN structure for country %s'
                               % country)

    # Are the check digits valid?
    validate_check_digits(iban)
