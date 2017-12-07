# -*- coding: utf-8 -*-

from string import ascii_letters
from datetime import datetime
from xml.etree import cElementTree as ET


# -----------------------------------------------------------------------------------------------------------------------
# Constants

VALID_ID_CHARS = ascii_letters + '_'


# -----------------------------------------------------------------------------------------------------------------------
# Utilities


def now_to_iso8601():
    """Returns NOW date/time as a UTC date/time formated as iso8601 string"""
    utc_date = datetime.utcnow()
    return dt_to_iso8601(utc_date)


def dt_to_iso8601(dt):
    """Turn a datetime into an ISO8601 formatted string"""
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def bool_to_yes_no(val):
    """Convert True/False to Yes/No"""
    return 'Yes' if val else 'No'


def bool_to_true_false(val):
    """Convert True/False to TRUE / FALSE"""
    return 'TRUE' if val else 'FALSE'


def indent(elem, level=0):
    """Indent a elementree structure"""
    i = "\n" + level * "  "
    if len(elem) > 0:
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def make_element(builder, tag, content):
    """Make an element with this tag and text content"""
    builder.start(tag, {})
    builder.data(content)  # Must be UTF-8 encoded
    builder.end(tag)


# -----------------------------------------------------------------------------------------------------------------------
# Classes

class ODMElement(object):
    """Base class for ODM XML element classes"""

    def __call__(self, *args):
        """Collect all children passed in call"""
        for child in args:
            self << child
        return self

    def __lshift__(self, other):
        """__lshift__ should be overridden in descendant classes to accept child elements and incorporate them.
           By default takes no child elements
        """
        raise ValueError("%s takes no child elements" % self.__class__.__name__)

    def add(self, *args):
        """Like call but adds a set of args"""
        for child in args:
            self << child
        return self

    def __str__(self):
        """Return string representation"""
        builder = ET.TreeBuilder()
        self.build(builder)
        return ET.tostring(builder.close(), encoding='utf-8').decode('utf-8')

    def set_single_attribute(self, other, trigger_klass, property_name):
        """Used to set guard the setting of an attribute which is singular and can't be set twice"""

        if isinstance(other, trigger_klass):

            # Check property exists
            if not hasattr(self, property_name):
                raise AttributeError("%s has no property %s" % (self.__class__.__name__, property_name))

            if getattr(self, property_name) is None:
                setattr(self, property_name, other)
            else:
                raise ValueError(
                    '%s already has a %s element set.' % (self.__class__.__name__, other.__class__.__name__,))

    def set_list_attribute(self, other, trigger_klass, property_name):
        """Used to set guard the setting of a list attribute, ensuring the same element is not added twice."""
        # Check property exists
        if isinstance(other, trigger_klass):

            if not hasattr(self, property_name):
                raise AttributeError("%s has no property %s" % (self.__class__.__name__, property_name))

            val = getattr(self, property_name, [])
            if other in val:
                raise ValueError("%s already exists in %s" % (other.__class__.__name__, self.__class__.__name__))
            else:
                val.append(other)
                setattr(self, property_name, val)


class TransactionalElement(ODMElement):
    """
    Models an ODM Element that is allowed a transaction type. Different elements have different
    allowed transaction types
    """
    ALLOWED_TRANSACTION_TYPES = []

    def __init__(self, transaction_type):
        self._transaction_type = None
        self.transaction_type = transaction_type

    @property
    def transaction_type(self):
        """returns the TransactionType attribute"""
        return self._transaction_type

    @transaction_type.setter
    def transaction_type(self, value):
        """Set the TransactionType (with Input Validation)"""
        if value is not None:
            if value not in self.ALLOWED_TRANSACTION_TYPES:
                raise AttributeError('%s transaction_type element must be one of %s not %s' % (
                    self.__class__.__name__, ','.join(self.ALLOWED_TRANSACTION_TYPES), value,))
        self._transaction_type = value


