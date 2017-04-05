# -*- coding: utf-8 -*-

__author__ = 'isparks'

import uuid
import re
from xml.etree import cElementTree as ET
from datetime import datetime
from string import ascii_letters
from rwslib.builder_constants import *
from collections import OrderedDict

"""
builders.py provides convenience classes for building ODM documents for clinical data and metadata post messages.
"""

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


class UserRef(ODMElement):
    """
    Reference to a :class:`User`
    """

    def __init__(self, oid):
        """
        :param str oid: OID for referenced :class:`User`
        """
        self.oid = oid

    def build(self, builder):
        """
        Build XML by appending to builder
        """
        builder.start("UserRef", dict(UserOID=self.oid))
        builder.end("UserRef")


class LocationRef(ODMElement):
    """
    Reference to a :class:`Location`
    """

    def __init__(self, oid):
        """
        :param str oid: OID for referenced :class:`Location`
        """
        self.oid = oid

    def build(self, builder):
        """
        Build XML by appending to builder
        """
        builder.start("LocationRef", dict(LocationOID=self.oid))
        builder.end("LocationRef")


class SignatureRef(ODMElement):
    """
    Reference to a Signature
    """

    def __init__(self, oid):
        """
        :param str oid: OID for referenced :class:`Signature`
        """
        self.oid = oid

    def build(self, builder):
        """
        Build XML by appending to builder
        """
        builder.start("SignatureRef", dict(SignatureOID=self.oid))
        builder.end("SignatureRef")


class ReasonForChange(ODMElement):
    """
    A user-supplied reason for a data change.
    """

    def __init__(self, reason):
        """
        :param str reason: Supplied Reason for change
        """
        self.reason = reason

    def build(self, builder):
        """
        Build XML by appending to builder
        """
        builder.start("ReasonForChange", {})
        builder.data(self.reason)
        builder.end("ReasonForChange")


class DateTimeStamp(ODMElement):
    """
    The date/time that the data entry, modification, or signature was performed.
    This applies to the initial occurrence of the action, not to subsequent transfers between computer systems.
    """

    def __init__(self, date_time):
        #: specified DateTime for event
        self.date_time = date_time

    def build(self, builder):
        """
        Build XML by appending to builder
        """
        builder.start("DateTimeStamp", {})
        if isinstance(self.date_time, datetime):
            builder.data(dt_to_iso8601(self.date_time))
        else:
            builder.data(self.date_time)
        builder.end("DateTimeStamp")


class Signature(ODMElement):
    """
    An electronic signature applies to a collection of clinical data.
    This indicates that some user accepts legal responsibility for that data.
    See 21 CFR Part 11.
    The signature identifies the person signing, the location of signing,
    the signature meaning (via the referenced SignatureDef),
    the date and time of signing,
    and (in the case of a digital signature) an encrypted hash of the included data.
    """

    def __init__(self, signature_id=None, user_ref=None, location_ref=None, signature_ref=None, date_time_stamp=None):
        #: Unique ID for Signature
        """
        :param UserRef user_ref: :class:`UserRef` for :class:`User` signing Data
        :param LocationRef location_ref: :class:`LocationRef` for :class:`Location` of signing
        :param SignatureRef signature_ref: :class:`SignatureRef` for :class:`SignatureDef` providing signature meaning
        :param date_time_stamp: :class:`DateTimeStamp` for the time of Signature
        """
        self._id = None
        if signature_id:
            self.signature_id = signature_id
        self.user_ref = user_ref
        self.location_ref = location_ref
        self.signature_ref = signature_ref
        self.date_time_stamp = date_time_stamp

    @property
    def signature_id(self):
        """
        The ID for the Signature

        .. note:: If a Signature element is contained within a Signatures element, the ID attribute is required.
        """
        return self._id

    @signature_id.setter
    def signature_id(self, id):
        """Set the ID for the Signature"""
        self._id = id

    def build(self, builder):
        """
        Build XML by appending to builder
        """

        params = {}
        if self.signature_id is not None:
            # If a Signature element is contained within a Signatures element, the ID attribute is required.
            params['ID'] = self.signature_id

        builder.start("Signature", params)

        if self.user_ref is None:
            raise ValueError("User Reference not set.")
        self.user_ref.build(builder)

        if self.location_ref is None:
            raise ValueError("Location Reference not set.")
        self.location_ref.build(builder)

        if self.signature_ref is None:
            raise ValueError("Signature Reference not set.")
        self.signature_ref.build(builder)

        if self.date_time_stamp is None:
            raise ValueError("DateTime not set.")
        self.date_time_stamp.build(builder)

        builder.end("Signature")

    def __lshift__(self, other):
        if not isinstance(other, (UserRef, LocationRef, SignatureRef, DateTimeStamp,)):
            raise ValueError("Signature cannot accept a child element of type %s" % other.__class__.__name__)

        # Order is important, apparently
        self.set_single_attribute(other, UserRef, 'user_ref')
        self.set_single_attribute(other, LocationRef, 'location_ref')
        self.set_single_attribute(other, SignatureRef, 'signature_ref')
        self.set_single_attribute(other, DateTimeStamp, 'date_time_stamp')
        return other


class Annotation(TransactionalElement):
    """
    A general note about clinical data.
    If an annotation has both a comment and flags, the flags should be related to the comment.

    .. note:: Annotation is not supported by Medidata Rave
    """
    ALLOWED_TRANSACTION_TYPES = ["Insert", "Update", "Remove", "Upsert", "Context"]

    def __init__(self, annotation_id=None, seqnum=1,
                 flags=None, comment=None,
                 transaction_type=None):
        """
        :param id: ID for this Annotation (required if contained within an Annotations element)
        :type id: str or None
        :param int seqnum: :attr:`SeqNum` for Annotation
        :param flags: one or more :class:`Flag` for the Annotation
        :type flags: Flag or list(Flag)
        :param comment: one or more :class:`Comment` for the Annotation
        :type comment: Comment
        :param transaction_type: :attr:`TransactionType` for Annotation (one of **Insert**, **Update**, *Remove*, **Upsert**, **Context**)
        """
        super(Annotation, self).__init__(transaction_type=transaction_type)
        # initialise the flags collection
        self.flags = []
        if flags:
            if isinstance(flags, (list, tuple)):
                for flag in flags:
                    self << flag
            elif isinstance(flags, Flag):
                self << flags
            else:
                raise AttributeError("Flags attribute should be an iterable or Flag")
        self._id = None
        if annotation_id is not None:
            self.annotation_id = annotation_id
        self._seqnum = None
        if seqnum is not None:
            # validate the input
            self.seqnum = seqnum
        self.comment = comment

    @property
    def annotation_id(self):
        """
        ID for annotation

        .. note:: If an Annotation is contained with an Annotations element, the ID attribute is required.
        """
        return self._id

    @annotation_id.setter
    def annotation_id(self, value):
        """Set ID for Annotation"""
        if value in [None, ''] or str(value).strip() == '':
            raise AttributeError("Invalid ID value supplied")
        self._id = value

    @property
    def seqnum(self):
        """
        SeqNum attribute (a small positive integer) uniquely identifies the annotation within its parent entity.
        """
        return self._seqnum

    @seqnum.setter
    def seqnum(self, value):
        """
        Set SeqNum for Annotation
        :param value: SeqNum value
        :type value: int
        """
        if not re.match(r'\d+', str(value)) or value < 0:
            raise AttributeError("Invalid SeqNum value supplied")
        self._seqnum = value

    def build(self, builder):
        """
        Build XML by appending to builder
        """
        params = {}

        # Add in the transaction type
        if self.transaction_type is not None:
            params["TransactionType"] = self.transaction_type

        if self.seqnum is None:
            # SeqNum is not optional (and defaulted)
            raise ValueError("SeqNum is not set.")  # pragma: no cover
        params["SeqNum"] = self.seqnum

        if self.annotation_id is not None:
            # If an Annotation is contained with an Annotations element,
            # the ID attribute is required.
            params["ID"] = self.annotation_id

        builder.start("Annotation", params)

        if self.flags in (None, []):
            raise ValueError('Flag is not set.')

        # populate the flags
        for flag in self.flags:
            flag.build(builder)

        # add the Comment, if it exists
        if self.comment is not None:
            self.comment.build(builder)

        builder.end("Annotation")

    def __lshift__(self, other):
        if not isinstance(other, (Flag, Comment,)):
            raise ValueError("Annotation cannot accept a child element of type %s" % other.__class__.__name__)

        self.set_single_attribute(other, Comment, 'comment')
        self.set_list_attribute(other, Flag, 'flags')
        return other


class Comment(ODMElement):
    """
    A free-text (uninterpreted) comment about clinical data.
    The comment may have come from the Sponsor or the clinical Site.

    .. note:: Comment is not supported by Medidata Rave
    """

    VALID_SPONSOR_OR_SITE_RESPONSES = ["Sponsor", "Site"]

    def __init__(self, text=None, sponsor_or_site=None):
        """
        :param str text: Text for Comment
        :param str sponsor_or_site: Originator flag for Comment (either _Sponsor_ or _Site_)
        """
        self._text = text
        self._sponsor_or_site = sponsor_or_site

    @property
    def text(self):
        """Text content of Comment"""
        return self._text

    @text.setter
    def text(self, value):
        """Set Text content for Comment (validation of input)"""
        if value in (None, '') or value.strip() == "":
            raise AttributeError("Empty text value is invalid.")
        self._text = value

    @property
    def sponsor_or_site(self):
        """Originator of comment (either Sponsor or Site)"""
        return self._sponsor_or_site

    @sponsor_or_site.setter
    def sponsor_or_site(self, value):
        """Set Originator with validation of input"""
        if value not in Comment.VALID_SPONSOR_OR_SITE_RESPONSES:
            raise AttributeError("%s sponsor_or_site value of %s is not valid" % (self.__class__.__name__,
                                                                                  value))
        self._sponsor_or_site = value

    def build(self, builder):
        """
        Build XML by appending to builder
        """
        if self.text is None:
            raise ValueError("Text is not set.")
        params = {}
        if self.sponsor_or_site is not None:
            params['SponsorOrSite'] = self.sponsor_or_site

        builder.start("Comment", params)
        builder.data(self.text)
        builder.end("Comment")


class Flag(ODMElement):
    """
    A machine-processable annotation on clinical data.

    .. note:: Flag is not supported by Rave
    """

    def __init__(self, flag_type=None, flag_value=None):
        """
        :param FlagType flag_type: Type for Flag
        :param FlagValue flag_value: Value for Flag
        """
        self.flag_type = None
        self.flag_value = None
        if flag_type is not None:
            self << flag_type
        if flag_value is not None:
            self << flag_value

    def build(self, builder):
        """
        Build XML by appending to builder
        """
        builder.start("Flag", {})

        if self.flag_type is not None:
            self.flag_type.build(builder)

        if self.flag_value is None:
            raise ValueError('FlagValue is not set.')
        self.flag_value.build(builder)

        builder.end("Flag")

    def __lshift__(self, other):
        if not isinstance(other, (FlagType, FlagValue,)):
            raise ValueError("Flag cannot accept a child element of type %s" % other.__class__.__name__)

        # Order is important, apparently
        self.set_single_attribute(other, FlagType, 'flag_type')
        self.set_single_attribute(other, FlagValue, 'flag_value')
        return other


class FlagType(ODMElement):
    """
    The type of flag. This determines the purpose and semantics of the flag.
    Different applications are expected to be interested in different types of flags.
    The actual value must be a member of the referenced CodeList.

    .. note:: FlagType is not supported by Rave
    """

    def __init__(self, flag_type, codelist_oid=None):
        """
        :param flag_type: Type for :class:`Flag`
        """
        self.flag_type = flag_type
        self._codelist_oid = None
        if codelist_oid is not None:
            self.codelist_oid = codelist_oid

    @property
    def codelist_oid(self):
        """Reference to the :class:`CodeList` for the FlagType"""
        return self._codelist_oid

    @codelist_oid.setter
    def codelist_oid(self, value):
        if value in (None, '') or value.strip() == "":
            raise AttributeError("Empty CodeListOID value is invalid.")
        self._codelist_oid = value

    def build(self, builder):
        """
        Build XML by appending to builder
        """
        if self.codelist_oid is None:
            raise ValueError("CodeListOID not set.")
        builder.start("FlagType", dict(CodeListOID=self.codelist_oid))
        builder.data(self.flag_type)
        builder.end("FlagType")


class FlagValue(ODMElement):
    """
    The value of the flag. The meaning of this value is typically dependent on the associated FlagType.
    The actual value must be a member of the referenced CodeList.

    .. note::  FlagValue is not supported by Rave
    """

    def __init__(self, flag_value, codelist_oid=None):
        """
        :param flag_value: Value for :class:`Flag`
        """
        self.flag_value = flag_value
        self._codelist_oid = None
        if codelist_oid is not None:
            self.codelist_oid = codelist_oid

    @property
    def codelist_oid(self):
        """Reference to the :class:`CodeList` for the FlagType"""
        return self._codelist_oid

    @codelist_oid.setter
    def codelist_oid(self, value):
        if value in (None, '') or value.strip() == "":
            raise AttributeError("Empty CodeListOID value is invalid.")
        self._codelist_oid = value

    def build(self, builder):
        """
        Build XML by appending to builder
        """
        if self.codelist_oid is None:
            raise ValueError("CodeListOID not set.")
        builder.start("FlagValue", dict(CodeListOID=self.codelist_oid))
        builder.data(self.flag_value)
        builder.end("FlagValue")


class MdsolQuery(ODMElement):
    """
    MdsolQuery extension element for Queries at item level only

    .. note:: This is a Medidata Rave specific extension
    """

    def __init__(self, value=None, query_repeat_key=None, recipient=None, status=None, requires_response=None,
                 response=None):
        """
        :param str value: Query Value
        :param int query_repeat_key: Repeat key for Query
        :param str recipient: Recipient for Query
        :param QueryStatusType status: Query status
        :param bool requires_response: Does this Query need a response?
        :param response: Query response (if any)
        :type response: str or None
        """
        self.value = value
        self.query_repeat_key = query_repeat_key
        self.recipient = recipient
        self._status = None
        self.status = status
        self.requires_response = requires_response
        self.response = response

    @property
    def status(self):
        """Query Status"""
        return self._status

    @status.setter
    def status(self, value):
        """Set Query Status"""
        if value is not None:
            if not isinstance(value, QueryStatusType):
                raise AttributeError("%s action type is invalid in mdsol:Query." % (value,))
        self._status = value

    def build(self, builder):
        """
        Build XML by appending to builder
        """
        params = {}

        if self.value is not None:
            params['Value'] = str(self.value)

        if self.query_repeat_key is not None:
            params['QueryRepeatKey'] = str(self.query_repeat_key)

        if self.recipient is not None:
            params['Recipient'] = str(self.recipient)

        if self.status is not None:
            params['Status'] = self.status.value

        if self.requires_response is not None:
            params['RequiresResponse'] = bool_to_yes_no(self.requires_response)

        # When closing a query
        if self.response is not None:
            params['Response'] = str(self.response)

        builder.start("mdsol:Query", params)
        builder.end("mdsol:Query")


class ItemData(TransactionalElement):
    """Models the ODM ItemData object"""
    ALLOWED_TRANSACTION_TYPES = ['Insert', 'Update', 'Upsert', 'Context', 'Remove']

    def __init__(self, itemoid, value, specify_value=None, transaction_type=None, lock=None, freeze=None, verify=None):
        """
        :param str itemoid: OID for the matching :class:`ItemDef`
        :param str value: Value for the the ItemData
        :param str specify_value: 'If other, specify' value - *Rave specific attribute*
        :param str transaction_type: Transaction type for the data
        :param bool lock: Lock the DataPoint? - *Rave specific attribute*
        :param bool freeze: Freeze the DataPoint? - *Rave specific attribute*
        :param bool verify: Verify the DataPoint? - *Rave specific attribute*
        """
        super(self.__class__, self).__init__(transaction_type)
        self.itemoid = itemoid
        self.value = value

        self.specify_value = specify_value
        self.lock = lock
        self.freeze = freeze
        self.verify = verify
        #: the corresponding :class:`AuditRecord` for the DataPoint
        self.audit_record = None
        #: the list of :class:`MdsolQuery` on the DataPoint  - *Rave Specific Attribute*
        self.queries = []
        #: the list of :class:`Annotation` on the DataPoint - *Not supported by Rave*
        self.annotations = []
        #: the corresponding :class:`MeasurementUnitRef` for the DataPoint
        self.measurement_unit_ref = None
        #: the list of :class:`MdsolProtocolDeviation` references on the DataPoint - *Rave Specific Attribute*
        self.deviations = []

    def build(self, builder):
        """
        Build XML by appending to builder
        """
        params = dict(ItemOID=self.itemoid)

        if self.transaction_type is not None:
            params["TransactionType"] = self.transaction_type

        if self.value in [None, '']:
            params['IsNull'] = 'Yes'
        else:
            params['Value'] = str(self.value)

        if self.specify_value is not None:
            params['mdsol:SpecifyValue'] = self.specify_value

        if self.lock is not None:
            params['mdsol:Lock'] = bool_to_yes_no(self.lock)

        if self.freeze is not None:
            params['mdsol:Freeze'] = bool_to_yes_no(self.freeze)

        if self.verify is not None:
            params['mdsol:Verify'] = bool_to_yes_no(self.verify)

        builder.start("ItemData", params)

        if self.audit_record is not None:
            self.audit_record.build(builder)

        # Measurement unit ref must be after audit record or RWS complains
        if self.measurement_unit_ref is not None:
            self.measurement_unit_ref.build(builder)

        for query in self.queries:  # type: MdsolQuery
            query.build(builder)

        for deviation in self.deviations:  # type: MdsolProtocolDeviation
            deviation.build(builder)

        for annotation in self.annotations:  # type: Annotation
            annotation.build(builder)

        builder.end("ItemData")

    def __lshift__(self, other):
        if not isinstance(other, (MeasurementUnitRef, AuditRecord, MdsolQuery, Annotation,
                                  MdsolProtocolDeviation)):
            raise ValueError("ItemData object can only receive MeasurementUnitRef, AuditRecord, Annotation,"
                             "MdsolProtocolDeviation or MdsolQuery objects")
        self.set_single_attribute(other, MeasurementUnitRef, 'measurement_unit_ref')
        self.set_single_attribute(other, AuditRecord, 'audit_record')
        self.set_list_attribute(other, MdsolQuery, 'queries')
        self.set_list_attribute(other, MdsolProtocolDeviation, 'deviations')
        self.set_list_attribute(other, Annotation, 'annotations')
        return other


class ItemGroupData(TransactionalElement):
    """
    Models the ODM ItemGroupData object.

    .. note:: No name for the ItemGroupData element is required. This is built automatically by the form.
    """
    ALLOWED_TRANSACTION_TYPES = ['Insert', 'Update', 'Upsert', 'Context']

    def __init__(self, transaction_type=None, item_group_repeat_key=None,
                 whole_item_group=False, annotations=None):
        """
        :param str transaction_type: TransactionType for the ItemGroupData
        :param int item_group_repeat_key: RepeatKey for the ItemGroupData
        :param bool whole_item_group: Is this the entire ItemGroupData, or just parts? - *Rave specific attribute*
        :param annotations: Annotation for the ItemGroup - *Not supported by Rave*
        :type annotations: list(Annotation) or Annotation
        """
        super(self.__class__, self).__init__(transaction_type)
        self.item_group_repeat_key = item_group_repeat_key
        self.whole_item_group = whole_item_group
        self.items = OrderedDict()
        self.annotations = []
        if annotations:
            # Add the annotations
            if isinstance(annotations, Annotation):
                self << annotations
            elif isinstance(annotations, list):
                for annotation in annotations:
                    self << annotation
        #: :class:`Signature` for ItemGroupData
        self.signature = None

    def __lshift__(self, other):
        """Override << operator"""
        if not isinstance(other, (ItemData, Annotation, Signature)):
            raise ValueError("ItemGroupData object can only receive ItemData, Signature or Annotation objects")

        self.set_list_attribute(other, Annotation, 'annotations')
        self.set_single_attribute(other, Signature, 'signature')
        if isinstance(other, ItemData):
            if other.itemoid in self.items:
                raise ValueError("ItemGroupData object with that itemoid is already in the ItemGroupData object")
            self.items[other.itemoid] = other
        return other

    def build(self, builder, formname):
        """Build XML by appending to builder"""
        params = dict(ItemGroupOID=formname)

        if self.transaction_type is not None:
            params["TransactionType"] = self.transaction_type

        if self.item_group_repeat_key is not None:
            params["ItemGroupRepeatKey"] = str(
                self.item_group_repeat_key)  # may be @context for transaction type upsert or context

        params["mdsol:Submission"] = "WholeItemGroup" if self.whole_item_group else "SpecifiedItemsOnly"

        builder.start("ItemGroupData", params)

        # Ask children
        for item in self.items.values():
            item.build(builder)

        # Add annotations
        for annotation in self.annotations:
            annotation.build(builder)

        # Add the signature if it exists
        if self.signature is not None:
            self.signature.build(builder)
        builder.end("ItemGroupData")


class FormData(TransactionalElement):
    """Models the ODM FormData object"""
    ALLOWED_TRANSACTION_TYPES = ['Insert', 'Update']

    def __init__(self, formoid, transaction_type=None, form_repeat_key=None):
        """
        :param str formoid: :class:`FormDef` OID
        :param str transaction_type: Transaction Type for Data (one of **Insert**, **Update**)
        :param str form_repeat_key: Repeat Key for FormData
        """
        super(self.__class__, self).__init__(transaction_type)
        self.formoid = formoid
        self.form_repeat_key = form_repeat_key
        self.itemgroups = []
        #: :class:`Signature` for FormData
        self.signature = None  # type: Signature
        #: Collection of :class:`Annotation` for FormData - *Not supported by Rave*
        self.annotations = []  # type: list(Annotation)

    def __lshift__(self, other):
        """Override << operator"""
        if not isinstance(other, (Signature, ItemGroupData, Annotation)):
            raise ValueError(
                "FormData object can only receive ItemGroupData, Signature or Annotation objects (not '{}')".format(
                    other))
        self.set_list_attribute(other, ItemGroupData, 'itemgroups')
        self.set_list_attribute(other, Annotation, 'annotations')
        self.set_single_attribute(other, Signature, 'signature')
        return other

    def build(self, builder):
        """Build XML by appending to builder
        :Example:
        <FormData FormOID="MH" TransactionType="Update">

        """
        params = dict(FormOID=self.formoid)

        if self.transaction_type is not None:
            params["TransactionType"] = self.transaction_type

        if self.form_repeat_key is not None:
            params["FormRepeatKey"] = str(self.form_repeat_key)

        builder.start("FormData", params)

        # Ask children
        for itemgroup in self.itemgroups:
            itemgroup.build(builder, self.formoid)

        if self.signature is not None:
            self.signature.build(builder)

        for annotation in self.annotations:
            annotation.build(builder)

        builder.end("FormData")


class StudyEventData(TransactionalElement):
    """Models the ODM StudyEventData object"""
    ALLOWED_TRANSACTION_TYPES = ['Insert', 'Update', 'Remove', 'Context']

    def __init__(self, study_event_oid, transaction_type="Update", study_event_repeat_key=None):
        """
        :param str study_event_oid: :class:`StudyEvent` OID
        :param str transaction_type: Transaction Type for Data (one of **Insert**, **Update**, *Remove*, **Context**)
        :param int study_event_repeat_key: :attr:`StudyEventRepeatKey` for StudyEventData
        """
        super(self.__class__, self).__init__(transaction_type)
        self.study_event_oid = study_event_oid
        self.study_event_repeat_key = study_event_repeat_key
        #: :class:`FormData` part of Study Event Data
        self.forms = []
        #: :class:`Annotation` for Study Event Data  - *Not Supported by Rave*
        self.annotations = []
        #: :class:`Signature` for Study Event Data
        self.signature = None

    def __lshift__(self, other):
        """Override << operator"""
        if not isinstance(other, (FormData, Annotation, Signature)):
            raise ValueError("StudyEventData object can only receive FormData, Signature or Annotation objects")
        self.set_list_attribute(other, FormData, 'forms')
        self.set_single_attribute(other, Signature, 'signature')
        self.set_list_attribute(other, Annotation, 'annotations')
        return other

    def build(self, builder):
        """Build XML by appending to builder
        :Example:
        <StudyEventData StudyEventOID="SCREENING" StudyEventRepeatKey="1" TransactionType="Update">

        """
        params = dict(StudyEventOID=self.study_event_oid)

        if self.transaction_type is not None:
            params["TransactionType"] = self.transaction_type

        if self.study_event_repeat_key is not None:
            params["StudyEventRepeatKey"] = self.study_event_repeat_key

        builder.start("StudyEventData", params)

        # Ask children
        for form in self.forms:
            form.build(builder)

        if self.signature is not None:
            self.signature.build(builder)

        for annotation in self.annotations:
            annotation.build(builder)

        builder.end("StudyEventData")


class SubjectData(TransactionalElement):
    """Models the ODM SubjectData and ODM SiteRef objects"""
    ALLOWED_TRANSACTION_TYPES = ['Insert', 'Update', 'Upsert']

    def __init__(self, site_location_oid, subject_key, subject_key_type="SubjectName", transaction_type="Update"):
        """
        :param str site_location_oid: :class:`SiteLocation` OID
        :param str subject_key: Value for SubjectKey
        :param str subject_key_type: Specifier as to the type of SubjectKey (either **SubjectName** or **SubjectUUID**)
        :param str transaction_type: Transaction Type for Data (one of **Insert**, **Update**, **Upsert**)
        """
        super(self.__class__, self).__init__(transaction_type)
        self.sitelocationoid = site_location_oid
        self.subject_key = subject_key
        self.subject_key_type = subject_key_type
        #: collection of :class:`StudyEventData`
        self.study_events = []
        #: collection of :class:`Annotation`
        self.annotations = []
        #: :class:`AuditRecord` for SubjectData - *Not Supported By Rave*
        self.audit_record = None
        #: :class:`Signature` for SubjectData
        self.signature = None

    def __lshift__(self, other):
        """Override << operator"""
        if not isinstance(other, (StudyEventData, AuditRecord, Annotation, Signature)):
            raise ValueError("SubjectData object can only receive StudyEventData, AuditRecord, "
                             "Annotation or Signature object")

        self.set_list_attribute(other, Annotation, 'annotations')
        self.set_list_attribute(other, StudyEventData, 'study_events')
        self.set_single_attribute(other, AuditRecord, 'audit_record')
        self.set_single_attribute(other, Signature, 'signature')

        return other

    def build(self, builder):
        """Build XML by appending to builder"""
        params = dict(SubjectKey=self.subject_key)
        params['mdsol:SubjectKeyType'] = self.subject_key_type

        if self.transaction_type is not None:
            params["TransactionType"] = self.transaction_type

        builder.start("SubjectData", params)

        # Ask children
        if self.audit_record is not None:
            self.audit_record.build(builder)

        builder.start("SiteRef", {'LocationOID': self.sitelocationoid})
        builder.end("SiteRef")

        for event in self.study_events:
            event.build(builder)

        if self.signature is not None:
            self.signature.build(builder)

        for annotation in self.annotations:
            annotation.build(builder)

        builder.end("SubjectData")


class ClinicalData(ODMElement):
    """Models the ODM ClinicalData object"""

    def __init__(self, projectname, environment, metadata_version_oid="1"):
        """
        :param projectname: Name of Project in Medidata Rave
        :param environment: Rave Study Enviroment
        :param metadata_version_oid: MetadataVersion OID
        """
        self.projectname = projectname
        self.environment = environment
        self.metadata_version_oid = metadata_version_oid
        #: :class:`SubjectData` for the ClinicalData Element
        self.subject_data = None

    def __lshift__(self, other):
        """Override << operator"""
        if not isinstance(other, SubjectData):
            raise ValueError("ClinicalData object can only receive SubjectData object")
        self.set_single_attribute(other, SubjectData, 'subject_data')
        return other

    def build(self, builder):
        """Build XML by appending to builder"""
        params = dict(MetaDataVersionOID=self.metadata_version_oid,
                      StudyOID="%s (%s)" % (self.projectname, self.environment,),
                      )

        builder.start("ClinicalData", params)
        # Ask children
        if self.subject_data is not None:
            self.subject_data.build(builder)
        builder.end("ClinicalData")


class ODM(ODMElement):
    """Models the ODM object"""
    FILETYPE_TRANSACTIONAL = 'Transactional'
    FILETYPE_SNAPSHOT = 'Snapshot'

    def __init__(self, originator, description="", creationdatetime=now_to_iso8601(), fileoid=None, filetype=None):
        """
        :param str originator: The organization that generated the ODM file.
        :param str description: The sender should use the Description attribute to record any information that will 
            help the receiver interpret the document correctly.
        :param str creationdatetime: Time of creation of the file containing the document.
        :param str fileoid: A unique identifier for this file.
        :param str filetype: Snapshot means that the document contains only the current state of the data and metadata 
            it describes, and no transactional history. A Snapshot document may include only one instruction per 
            data point. For clinical data, TransactionType in a Snapshot file must either not be present or be Insert. 
            Transactional means that the document may contain more than one instruction per data point. 
            Use a Transactional document to send both what the current state of the data is, and how it came to be there.
        """
        self.originator = originator  # Required
        self.description = description
        self.creationdatetime = creationdatetime
        # filetype will always be "Transactional"
        # ODM version will always be 1.3
        # Granularity="SingleSubject"
        # AsOfDateTime always OMITTED (it's optional)
        self.clinical_data = None
        self.study = None
        self.filetype = ODM.FILETYPE_TRANSACTIONAL if filetype is None else ODM.FILETYPE_SNAPSHOT

        # Create unique fileoid if none given
        self.fileoid = str(uuid.uuid4()) if fileoid is None else fileoid

    def __lshift__(self, other):
        """Override << operator"""
        if not isinstance(other, (ClinicalData, Study,)):
            raise ValueError("ODM object can only receive ClinicalData or Study object")
        self.set_single_attribute(other, ClinicalData, 'clinical_data')
        self.set_single_attribute(other, Study, 'study')

        return other

    def getroot(self):
        """Build XML object, return the root"""
        builder = ET.TreeBuilder()

        params = dict(ODMVersion="1.3",
                      FileType=self.filetype,
                      CreationDateTime=self.creationdatetime,
                      Originator=self.originator,
                      FileOID=self.fileoid,
                      xmlns="http://www.cdisc.org/ns/odm/v1.3",
                      )
        params['xmlns:mdsol'] = "http://www.mdsol.com/ns/odm/metadata"

        if self.description:
            params['Description'] = self.description

        builder.start("ODM", params)

        # Ask the children
        if self.study is not None:
            self.study.build(builder)

        if self.clinical_data is not None:
            self.clinical_data.build(builder)

        builder.end("ODM")
        return builder.close()

    def __str__(self):
        doc = self.getroot()
        indent(doc)
        header = '<?xml version="1.0" encoding="utf-8" ?>\n'
        return header + ET.tostring(doc, encoding='utf-8').decode('utf-8')


# -----------------------------------------------------------------------------------------------------------------------
# Metadata Objects


class GlobalVariables(ODMElement):
    """
    GlobalVariables includes general summary information about the :class:`Study`.

    .. note:: Name and description are not important. protocol_name maps to the Rave project name
    """

    def __init__(self, protocol_name, name=None, description=''):
        """
        :param str protocol_name: Protocol Name
        :param str name: Study Name
        :param str description: Study Description
        """
        self.protocol_name = protocol_name
        self.name = name if name is not None else protocol_name
        self.description = description

    def build(self, builder):
        """Build XML by appending to builder"""
        builder.start("GlobalVariables", {})
        make_element(builder, 'StudyName', self.name)
        make_element(builder, 'StudyDescription', self.description)
        make_element(builder, 'ProtocolName', self.protocol_name)
        builder.end("GlobalVariables")


class TranslatedText(ODMElement):
    """
    Represents a language and a translated text for that language
    """

    def __init__(self, text, lang=None):
        """
        :param str text: Content expressed in language designated by :attr:`lang`
        :param str lang: Language code
        """
        self.text = text
        self.lang = lang

    def build(self, builder):
        """Build XML by appending to builder"""
        params = {}
        if self.lang is not None:
            params['xml:lang'] = self.lang
        builder.start("TranslatedText", params)
        builder.data(self.text)
        builder.end("TranslatedText")


class Symbol(ODMElement):
    """
    A human-readable name for a :class:`MeasurementUnit`.
    """

    def __init__(self):
        #: Collection of :class:`TranslatedText`
        self.translations = []

    def __lshift__(self, other):
        """Override << operator"""
        if not isinstance(other, TranslatedText):
            raise ValueError("Symbol can only accept TranslatedText objects as children")
        self.set_list_attribute(other, TranslatedText, 'translations')

        return other

    def build(self, builder):
        """Build XML by appending to builder"""
        builder.start("Symbol", {})
        for child in self.translations:
            child.build(builder)
        builder.end("Symbol")


class MeasurementUnit(ODMElement):
    """
    The physical unit of measure for a data item or value.
    The meaning of a MeasurementUnit is determined by its Name attribute.
    """

    def __init__(self,
                 oid,
                 name,
                 unit_dictionary_name=None,
                 constant_a=1,
                 constant_b=1,
                 constant_c=0,
                 constant_k=0,
                 standard_unit=False):
        """
        :param str oid: MeasurementUnit OID
        :param str name: Maps to Coded Unit within unit dictionary entries in Rave.
        :param str unit_dictionary_name: Maps to unit dictionary Name in Rave. - *Rave specific attribute*
        :param int constant_a: Maps to the unit dictionary Constant A in Rave. - *Rave specific attribute*
        :param int constant_b: Maps to the unit dictionary Constant B in Rave. - *Rave specific attribute*
        :param int constant_c: Maps to the unit dictionary Constant C in Rave. - *Rave specific attribute*
        :param int constant_k: Maps to the unit dictionary Constant K in Rave. - *Rave specific attribute*
        :param bool standard_unit: Yes = Standard checked within the unit dictionary entry in Rave.
            No = Standard unchecked within the unit dictionary entry in Rave.  - *Rave specific attribute*
        """
        #: Collection of :class:`Symbol` for this MeasurementUnit
        self.symbols = []
        self.oid = oid
        self.name = name
        self.unit_dictionary_name = unit_dictionary_name
        self.constant_a = constant_a
        self.constant_b = constant_b
        self.constant_c = constant_c
        self.constant_k = constant_k
        self.standard_unit = standard_unit

    def build(self, builder):
        """Build XML by appending to builder"""

        params = dict(OID=self.oid,
                      Name=self.name)

        if self.unit_dictionary_name:
            params['mdsol:UnitDictionaryName'] = self.unit_dictionary_name

        for suffix in ['A', 'B', 'C', 'K']:
            val = getattr(self, 'constant_{0}'.format(suffix.lower()))
            params['mdsol:Constant{0}'.format(suffix)] = str(val)

        if self.standard_unit:
            params['mdsol:StandardUnit'] = 'Yes'

        builder.start("MeasurementUnit", params)
        for child in self.symbols:
            child.build(builder)
        builder.end("MeasurementUnit")

    def __lshift__(self, other):
        """Override << operator"""
        if not isinstance(other, Symbol):
            raise ValueError("MeasurementUnits object can only receive Symbol object")
        self.set_list_attribute(other, Symbol, 'symbols')

        return other


class BasicDefinitions(ODMElement):
    """
    Container for :class:`MeasurementUnit`
    """

    def __init__(self):
        #: Collection of :class:`MeasurementUnit`
        self.measurement_units = []

    def build(self, builder):
        """Build XML by appending to builder"""
        builder.start("BasicDefinitions", {})
        for child in self.measurement_units:
            child.build(builder)
        builder.end("BasicDefinitions")

    def __lshift__(self, other):
        """Override << operator"""
        if not isinstance(other, MeasurementUnit):
            raise ValueError("BasicDefinitions object can only receive MeasurementUnit object")
        self.measurement_units.append(other)
        return other


class StudyEventRef(ODMElement):
    """
    A reference to a StudyEventDef as it occurs within a specific version of a :class:`Study`.
    The list of :class:`StudyEventRef` identifies the types of study events that are allowed to occur within the study.
    The :class:`StudyEventRef` within a :class:`Protocol` must not have duplicate StudyEventOIDs nor
    duplicate OrderNumbers.
    """

    def __init__(self, oid, order_number, mandatory):
        """
        :param oid: :class:`StudyEventDef` OID
        :type oid: str
        :param order_number: OrderNumber for the :class:`StudyEventRef` within the :class:`Study`
        :type order_number: int
        :param mandatory: Is this StudyEventDef Mandatory? (True|False)
        :type mandatory: bool
        """
        self.oid = oid
        self.order_number = order_number
        self.mandatory = mandatory

    def build(self, builder):
        """Build XML by appending to builder"""
        params = dict(StudyEventOID=self.oid,
                      OrderNumber=str(self.order_number),
                      Mandatory=bool_to_yes_no(self.mandatory))
        builder.start("StudyEventRef", params)
        builder.end("StudyEventRef")


class Protocol(ODMElement):
    """
    The Protocol lists the kinds of study events that can occur within a specific version of a :class:`Study`.
    All clinical data must occur within one of these study events.
    """

    def __init__(self):
        #: Collection of :class:`StudyEventRef`
        self.study_event_refs = []

    def build(self, builder):
        """Build XML by appending to builder"""
        builder.start("Protocol", {})
        for child in self.study_event_refs:
            child.build(builder)
        builder.end("Protocol")

    def __lshift__(self, other):
        """Override << operator"""
        if not isinstance(other, (StudyEventRef,)):
            raise ValueError('Protocol cannot accept a {0} as a child element'.format(other.__class__.__name__))
        self.set_list_attribute(other, StudyEventRef, 'study_event_refs')
        return other


class FormRef(ODMElement):
    """
    A reference to a :class:`FormDef` as it occurs within a specific :class:`StudyEventDef` .
    The list of :class:`FormRef` identifies the types of forms that are allowed to occur within this type of study
    event. The :class:`FormRef` within a single :class:`StudyEventDef` must not have duplicate FormOIDs nor OrderNumbers.
    """

    def __init__(self, oid, order_number, mandatory):
        """
        :param str oid: Set the :class:`FormDef` OID for the :class:`FormRef`
        :param int order_number: Define the OrderNumber for the :class:`FormRef` within the containing :class:`StudyEventDef`
        :param bool mandatory: Is this Form Mandatory?
        """
        self.oid = oid
        self.order_number = order_number
        self.mandatory = mandatory

    def build(self, builder):
        """Build XML by appending to builder"""
        params = dict(FormOID=self.oid,
                      OrderNumber=str(self.order_number),
                      Mandatory=bool_to_yes_no(self.mandatory)
                      )
        builder.start('FormRef', params)
        builder.end('FormRef')


class StudyEventDef(ODMElement):
    """
    A StudyEventDef packages a set of forms.
    Scheduled Study Events correspond to sets of forms that are expected to be collected for each subject as part of
    the planned visit sequence for the study.
    Unscheduled Study Events are designed to collect data that may or may not occur for any particular
    subject such as a set of forms that are completed for an early termination due to a serious adverse event.
    """
    # Event types
    SCHEDULED = 'Scheduled'
    UNSCHEDULED = 'Unscheduled'
    COMMON = 'Common'

    def __init__(self, oid, name, repeating, event_type,
                 category=None,
                 access_days=None,
                 start_win_days=None,
                 target_days=None,
                 end_win_days=None,
                 overdue_days=None,
                 close_days=None
                 ):
        """
        :param str oid: OID for StudyEventDef
        :param str name: Name for StudyEventDef
        :param bool repeating: Is this a repeating StudyEvent?
        :param str event_type: Type of StudyEvent (either *Scheduled*, *Unscheduled*, *Common*)
        :param str category: Category attribute is typically used to indicate the study phase appropriate to this type
            of study event. Examples might include Screening, PreTreatment, Treatment, and FollowUp.
        :param int access_days: The number of days before the Target date that the folder may be opened, viewed and
            edited from the Task List in Rave EDC. - *Rave Specific Attribute*
        :param int start_win_days: The number of days before the Target date that is considered to be the ideal
            start-date for use of this folder. - *Rave Specific Attribute*
        :param int target_days: The ideal number of days between Time Zero and the date of use for the
            folder. - *Rave Specific Attribute*
        :param int end_win_days: The number of days after the Target date that is considered to be the ideal end
            date for use of this folder. - *Rave Specific Attribute*
        :param int overdue_days: The number of days after the Target date at which point empty data points are
            marked overdue, and are displayed in the Task Summary in Rave EDC. - *Rave Specific Attribute*
        :param int close_days: The number of days after the Target date at which point no new data may be entered
            into the folder. - *Rave Specific Attribute*
        """
        self.oid = oid
        self.name = name
        self.repeating = repeating
        self.event_type = event_type
        self.category = category
        self.access_days = access_days
        self.start_win_days = start_win_days
        self.target_days = target_days
        self.end_win_days = end_win_days
        self.overdue_days = overdue_days
        self.close_days = close_days
        self.formrefs = []

    def build(self, builder):
        """Build XML by appending to builder"""

        params = dict(OID=self.oid, Name=self.name,
                      Repeating=bool_to_yes_no(self.repeating),
                      Type=self.event_type)

        if self.category is not None:
            params['Category'] = self.category

        if self.access_days is not None:
            params['mdsol:AccessDays'] = str(self.access_days)

        if self.start_win_days is not None:
            params['mdsol:StartWinDays'] = str(self.start_win_days)

        if self.target_days is not None:
            params['mdsol:TargetDays'] = str(self.target_days)

        if self.end_win_days is not None:
            params['mdsol:EndWinDays'] = str(self.end_win_days)

        if self.overdue_days is not None:
            params['mdsol:OverDueDays'] = str(self.overdue_days)

        if self.close_days is not None:
            params['mdsol:CloseDays'] = str(self.close_days)

        builder.start("StudyEventDef", params)
        for formref in self.formrefs:
            formref.build(builder)
        builder.end("StudyEventDef")

    def __lshift__(self, other):
        """Override << operator"""
        if not isinstance(other, (FormRef,)):
            raise ValueError('StudyEventDef cannot accept a {0} as a child element'.format(other.__class__.__name__))
        self.set_list_attribute(other, FormRef, 'formrefs')
        return other


class ItemGroupRef(ODMElement):
    """
    A reference to an ItemGroupDef as it occurs within a specific :class:`FormDef`.
    The list of ItemGroupRefs identifies the types of item groups that are allowed to occur within this type of form.
    The ItemGroupRefs within a single FormDef must not have duplicate ItemGroupOIDs nor OrderNumbers.
    """

    def __init__(self, oid, order_number, mandatory=True):
        #: OID for the referred :class:`ItemGroupDef`
        """
        :param str oid: OID for the referenced :class:`ItemGroupDef`
        :param int order_number: OrderNumber for the ItemGroupRef
        :param bool mandatory: Is this ItemGroupRef required?
        """
        self.oid = oid
        self.order_number = order_number
        self.mandatory = mandatory

    def build(self, builder):
        params = dict(ItemGroupOID=self.oid,
                      OrderNumber=str(self.order_number),
                      Mandatory=bool_to_yes_no(self.mandatory),
                      )
        builder.start("ItemGroupRef", params)
        builder.end("ItemGroupRef")


class MdsolHelpText(ODMElement):
    """
    Help element for :class:`FormDef` and :class:`ItemDef`

    .. note:: This is  Medidata Rave Specific Element
    """

    def __init__(self, lang, content):
        #: Language specification for HelpText
        self.lang = lang
        #: HelpText content
        self.content = content

    def build(self, builder):
        builder.start('mdsol:HelpText', {'xml:lang': self.lang})
        builder.data(self.content)
        builder.end('mdsol:HelpText')


class MdsolViewRestriction(ODMElement):
    """
    ViewRestriction for :class:`FormDef` and :class:`ItemDef`

    .. note:: This is  Medidata Rave Specific Element
    """

    def __init__(self, rolename):
        #: Name for the role for which the ViewRestriction applies
        self.rolename = rolename

    def build(self, builder):
        builder.start('mdsol:ViewRestriction', {})
        builder.data(self.rolename)
        builder.end('mdsol:ViewRestriction')


class MdsolEntryRestriction(ODMElement):
    """
    EntryRestriction for :class:`FormDef` and :class:`ItemDef`

    .. note:: This is  Medidata Rave Specific Element
    """

    def __init__(self, rolename):
        #: Name for the role for which the EntryRestriction applies
        self.rolename = rolename

    def build(self, builder):
        builder.start('mdsol:EntryRestriction', {})
        builder.data(self.rolename)
        builder.end('mdsol:EntryRestriction')


class FormDef(ODMElement):
    """
    A FormDef describes a type of form that can occur in a study.
    """
    LOG_PORTRAIT = 'Portrait'
    LOG_LANDSCAPE = 'Landscape'

    DDE_MUSTNOT = 'MustNotDDE'
    DDE_MAY = 'MayDDE'
    DDE_MUST = 'MustDDE'

    NOLINK = 'NoLink'
    LINK_NEXT = 'LinkNext'
    LINK_CUSTOM = 'LinkCustom'

    def __init__(self, oid, name,
                 repeating=False,
                 order_number=None,
                 active=True,
                 template=False,
                 signature_required=False,
                 log_direction=LOG_PORTRAIT,
                 double_data_entry=DDE_MUSTNOT,
                 confirmation_style=NOLINK,
                 link_study_event_oid=None,
                 link_form_oid=None
                 ):
        """
        :param str oid: OID for FormDef
        :param str name: Name for FormDef
        :param bool repeating: Is this a repeating Form?
        :param int order_number: OrderNumber for the FormDef
        :param bool active:  Indicates that the form is available to end users when you publish and
            push the draft to Rave EDC - *Rave Specific Attribute*
        :param bool template: Indicates that the form is a template form in Rave EDC - *Rave Specific Attribute*
        :param bool signature_required: Select to ensure that the form requires investigator signature
            for all submitted data points - *Rave Specific Attribute*
        :param str log_direction: Set the display mode of a form,
            (*Landscape* or *Portrait*) - *Rave Specific Attribute*
        :param str double_data_entry: Indicates if the form is used to collect data in Rave Double Data
            Entry (DDE), (*Always*, *Never* or *As Per Site*) - *Rave Specific Attribute*
        :param confirmation_style: Style of Confirmation,
            (*None*, *NotLink*, *LinkNext* or *LinkCustom*) - *Rave Specific Attribute*
        :param link_study_event_oid: OID for :class:`StudyEvent` target for Link - *Rave Specific Attribute*
        :param link_form_oid: OID for :class:`FormRef` target for Link - *Rave Specific Attribute*
        """
        self.oid = oid
        self.name = name
        self.order_number = order_number
        self.repeating = repeating  # Not actually used by Rave.
        self.active = active
        self.template = template
        self.signature_required = signature_required
        self.log_direction = log_direction
        self.double_data_entry = double_data_entry
        self.confirmation_style = confirmation_style
        self.link_study_event_oid = link_study_event_oid
        self.link_form_oid = link_form_oid
        #: Collection of :class:`ItemGroupRef` for Form
        self.itemgroup_refs = []
        #: Collection of :class:`HelpText` for Form (Cardinality not clear) - *Rave Specific Attribute*
        self.helptexts = []  #
        #: Collection of :class:`ViewRestriction` for Form - *Rave Specific Attribute*
        self.view_restrictions = []
        #: Collection of :class:`EntryRestriction` for Form - *Rave Specific Attribute*
        self.entry_restrictions = []

    def build(self, builder):
        """Build XML by appending to builder"""
        params = dict(OID=self.oid,
                      Name=self.name,
                      Repeating=bool_to_yes_no(self.repeating)
                      )

        if self.order_number is not None:
            params['mdsol:OrderNumber'] = str(self.order_number)

        if self.active is not None:
            params['mdsol:Active'] = bool_to_yes_no(self.active)

        params['mdsol:Template'] = bool_to_yes_no(self.template)
        params['mdsol:SignatureRequired'] = bool_to_yes_no(self.signature_required)
        params['mdsol:LogDirection'] = self.log_direction
        params['mdsol:DoubleDataEntry'] = self.double_data_entry
        params['mdsol:ConfirmationStyle'] = self.confirmation_style

        if self.link_study_event_oid:
            params['mdsol:LinkStudyEventOID'] = self.link_study_event_oid

        if self.link_form_oid:
            params['mdsol:LinkFormOID'] = self.link_form_oid

        builder.start("FormDef", params)
        for itemgroup_ref in self.itemgroup_refs:
            itemgroup_ref.build(builder)

        for helptext in self.helptexts:
            helptext.build(builder)

        for view_restriction in self.view_restrictions:
            view_restriction.build(builder)

        for entry_restriction in self.entry_restrictions:
            entry_restriction.build(builder)
        builder.end("FormDef")

    def __lshift__(self, other):
        """Override << operator"""
        if not isinstance(other, (ItemGroupRef, MdsolHelpText, MdsolViewRestriction, MdsolEntryRestriction,)):
            raise ValueError('StudyEventDef cannot accept a {0} as a child element'.format(other.__class__.__name__))

        self.set_list_attribute(other, ItemGroupRef, 'itemgroup_refs')
        self.set_list_attribute(other, MdsolHelpText, 'helptexts')
        self.set_list_attribute(other, MdsolViewRestriction, 'view_restrictions')
        self.set_list_attribute(other, MdsolEntryRestriction, 'entry_restrictions')
        return other


class MdsolLabelRef(ODMElement):
    """
    A reference to a label on a form

    .. note:: This is  Medidata Rave Specific Element
    """

    def __init__(self, oid, order_number):
        #: OID for the corresponding :class:`MdsoLabel`
        self.oid = oid
        #: :attr:`OrderNumber` for the Label
        self.order_number = order_number

    def build(self, builder):
        """Build XML by appending to builder"""
        params = dict(LabelOID=self.oid,
                      OrderNumber=str(self.order_number),
                      )

        builder.start('mdsol:LabelRef', params)
        builder.end('mdsol:LabelRef')


class MdsolAttribute(ODMElement):
    """
    Rave Web Services element for holding Vendor Attributes

    .. note:: This is  Medidata Rave Specific Element
    """

    def __init__(self, namespace, name, value, transaction_type='Insert'):
        #: Namespace for the Attribute
        self.namespace = namespace
        #: Name for the Attribute
        self.name = name
        #: Value for the Attribute
        self.value = value
        #: TransactionType for the Attribute
        self.transaction_type = transaction_type

    def build(self, builder):
        """Build XML by appending to builder"""
        params = dict(Namespace=self.namespace,
                      Name=self.name,
                      Value=self.value,
                      TransactionType=self.transaction_type,
                      )

        builder.start('mdsol:Attribute', params)
        builder.end('mdsol:Attribute')


class ItemRef(ODMElement):
    """
    A reference to an :class:`ItemDef` as it occurs within a specific :class:`ItemGroupDef`.
    The list of ItemRefs identifies the types of items that are allowed to occur within this type of item group.
    """

    def __init__(self, oid, order_number=None, mandatory=False, key_sequence=None,
                 imputation_method_oid=None, role=None, role_codelist_oid=None):
        """

        :param str oid: OID for :class:`ItemDef`
        :param int order_number: :attr:`OrderNumber` for the ItemRef
        :param bool mandatory: Is this ItemRef required?
        :param int key_sequence: The KeySequence (if present) indicates that this item is a key for the enclosing item
            group. It also provides an ordering for the keys.
        :param str imputation_method_oid: *DEPRECATED*
        :param str role: Role name describing the use of this data item.
        :param str role_codelist_oid: RoleCodeListOID may be used to reference a :class:`CodeList` that defines the
            full set roles from which the :attr:`Role` attribute value is to be taken.
        """
        self.oid = oid
        self.order_number = order_number
        self.mandatory = mandatory
        self.key_sequence = key_sequence
        self.imputation_method_oid = imputation_method_oid
        self.role = role
        self.role_codelist_oid = role_codelist_oid
        #: Collection of :class:`MdsolAttribute`
        self.attributes = []

    def build(self, builder):
        """Build XML by appending to builder"""

        params = dict(ItemOID=self.oid,
                      Mandatory=bool_to_yes_no(self.mandatory)
                      )

        if self.order_number is not None:
            params['OrderNumber'] = str(self.order_number)

        if self.key_sequence is not None:
            params['KeySequence'] = str(self.key_sequence)

        if self.imputation_method_oid is not None:
            params['ImputationMethodOID'] = self.imputation_method_oid

        if self.role is not None:
            params['Role'] = self.role

        if self.role_codelist_oid is not None:
            params['RoleCodeListOID'] = self.role_codelist_oid

        builder.start('ItemRef', params)

        for attribute in self.attributes:
            attribute.build(builder)
        builder.end('ItemRef')

    def __lshift__(self, other):
        """ItemRef can accept MdsolAttribute(s)"""
        if not isinstance(other, (MdsolAttribute)):
            raise ValueError('ItemRef cannot accept a {0} as a child element'.format(other.__class__.__name__))
        self.set_list_attribute(other, MdsolAttribute, 'attributes')
        return other


class ItemGroupDef(ODMElement):
    """
    An ItemGroupDef describes a type of item group that can occur within a Study.
    """

    def __init__(self, oid, name, repeating=False, is_reference_data=False, sas_dataset_name=None,
                 domain=None, origin=None, role=None, purpose=None, comment=None):
        """

        :param str oid: OID for ItemGroupDef
        :param str name: Name for ItemGroupDef
        :param bool repeating: Is this a repeating ItemDef?
        :param bool is_reference_data: If IsReferenceData is Yes, this type of item group can occur only within a
            :class:`ReferenceData` element. If IsReferenceData is No, this type of item group can occur only within a
            :class:`ClinicalData` element. The default for this attribute is No.
        :param str sas_dataset_name: SAS Dataset Name
        :param str domain: Domain for Items within this ItemGroup
        :param origin: Origin of data (eg CRF, eDT, Derived)
        :param role: Role for the ItemGroup (eg Identifier, Topic, Timing, Qualifiers)
        :param purpose: Purpose (eg Tabulation)
        :param comment: Comment on the ItemGroup Contents
        """
        self.oid = oid
        self.name = name
        self.repeating = repeating
        self.is_reference_data = is_reference_data
        self.sas_dataset_name = sas_dataset_name
        self.domain = domain
        self.origin = origin
        self.role = role
        self.purpose = purpose
        self.comment = comment
        #: Collection of :class:`ItemRef`
        self.item_refs = []
        #: Collection of :class:`MdsolLabelRef`
        self.label_refs = []

    def build(self, builder):
        """Build XML by appending to builder"""

        params = dict(OID=self.oid,
                      Name=self.name,
                      Repeating=bool_to_yes_no(self.repeating),
                      IsReferenceData=bool_to_yes_no(self.is_reference_data)
                      )

        if self.sas_dataset_name is not None:
            params['SASDatasetName'] = self.sas_dataset_name

        if self.domain is not None:
            params['Domain'] = self.domain

        if self.origin is not None:
            params['Origin'] = self.origin

        if self.role is not None:
            params['Role'] = self.role

        if self.purpose is not None:
            params['Purpose'] = self.purpose

        if self.comment is not None:
            params['Comment'] = self.comment

        builder.start('ItemGroupDef', params)

        for itemref in self.item_refs:
            itemref.build(builder)

        # Extensions always listed AFTER core elements
        for labelref in self.label_refs:
            labelref.build(builder)
        builder.end('ItemGroupDef')

    def __lshift__(self, other):
        """ItemGroupDef can accept ItemRef and LabelRef"""

        if not isinstance(other, (ItemRef, MdsolLabelRef)):
            raise ValueError('ItemGroupDef cannot accept a {0} as a child element'.format(other.__class__.__name__))

        self.set_list_attribute(other, ItemRef, 'item_refs')
        self.set_list_attribute(other, MdsolLabelRef, 'label_refs')
        return other


class Question(ODMElement):
    """
    A label shown to a human user when prompted to provide data for an item on paper or on a screen.
    """

    def __init__(self):
        #: Collection of :class:`Translation` for the Question
        self.translations = []

    def __lshift__(self, other):
        """Override << operator"""

        if not isinstance(other, (TranslatedText)):
            raise ValueError('Question cannot accept a {0} as a child element'.format(other.__class__.__name__))
        self.set_list_attribute(other, TranslatedText, 'translations')
        return other

    def build(self, builder):
        """
        Build XML by appending to builder

        .. note:: Questions can contain translations
        """
        builder.start('Question', {})
        for translation in self.translations:
            translation.build(builder)
        builder.end('Question')


class MeasurementUnitRef(ODMElement):
    """
    A reference to a measurement unit definition (:class:`MeasurementUnit`).
    """

    def __init__(self, oid, order_number=None):
        """
        :param str oid: :class:`MeasurementUnit` OID
        :param order_number: :attr:`OrderNumber` for MeasurementUnitRef
        """
        self.oid = oid
        self.order_number = order_number

    def build(self, builder):
        params = dict(MeasurementUnitOID=self.oid)
        if self.order_number is not None:
            params['mdsol:OrderNumber'] = str(self.order_number)

        builder.start('MeasurementUnitRef', params)
        builder.end('MeasurementUnitRef')


class AuditRecord(ODMElement):
    """
    An AuditRecord carries information pertaining to the creation, deletion, or modification of clinical data.
    This information includes who performed that action, and where, when, and why that action was performed.

    .. note:: AuditRecord is supported only by :class:`ItemData` in Rave
    """
    EDIT_MONITORING = 'Monitoring'
    EDIT_DATA_MANAGEMENT = 'DataManagement'
    EDIT_DB_AUDIT = 'DBAudit'
    EDIT_POINTS = [EDIT_MONITORING, EDIT_DATA_MANAGEMENT, EDIT_DB_AUDIT]

    def __init__(self, edit_point=None, used_imputation_method=None, identifier=None, include_file_oid=None):
        """
        :param str identifier: Audit identifier
        :param str edit_point: EditPoint attribute identifies the phase of data processing in which action occurred
            (*Monitoring*, *DataManagement*, *DBAudit*)
        :param bool used_imputation_method: Indicates whether the action involved the use of a Method
        :param bool include_file_oid: Include the FileOID in the AuditRecord
        """
        self._edit_point = None
        self.edit_point = edit_point
        self.used_imputation_method = used_imputation_method
        self._id = None
        if identifier:
            self.audit_id = identifier
        self.include_file_oid = include_file_oid
        #: :class:`UserRef` for the AuditRecord
        self.user_ref = None
        #: :class:`LocationRef` for the AuditRecord
        self.location_ref = None
        #: :class:`ReasonForChange` for the AuditRecord
        self.reason_for_change = None
        #: :class:`DateTimeStamp` for the AuditRecord
        self.date_time_stamp = None

    @property
    def audit_id(self):
        """
        AuditRecord ID

        .. note:: If an AuditRecord is contained within an AuditRecords element, the ID attribute must be provided.
        """
        return self._id

    @audit_id.setter
    def audit_id(self, value):
        if value not in [None, ''] and str(value).strip() != '':
            val = str(value).strip()[0]
            if val not in VALID_ID_CHARS:
                raise AttributeError('%s id cannot start with "%s" character' % (self.__class__.__name__, val,))
        self._id = value

    @property
    def edit_point(self):
        """
        EditPoint attribute identifies the phase of data processing in which action occurred
            (*Monitoring*, *DataManagement*, *DBAudit*)
        """
        return self._edit_point

    @edit_point.setter
    def edit_point(self, value):
        if value is not None:
            if value not in self.EDIT_POINTS:
                raise AttributeError('%s edit_point must be one of %s not %s' % (
                    self.__class__.__name__, ','.join(self.EDIT_POINTS), value,))
        self._edit_point = value

    def build(self, builder):
        """Build XML by appending to builder"""
        params = {}

        if self.edit_point is not None:
            params["EditPoint"] = self.edit_point

        if self.used_imputation_method is not None:
            params['UsedImputationMethod'] = bool_to_yes_no(self.used_imputation_method)

        if self.audit_id is not None:
            params['ID'] = str(self.audit_id)

        if self.include_file_oid is not None:
            params['mdsol:IncludeFileOID'] = bool_to_yes_no(self.include_file_oid)

        builder.start("AuditRecord", params)
        if self.user_ref is None:
            raise ValueError("User Reference not set.")
        self.user_ref.build(builder)

        if self.location_ref is None:
            raise ValueError("Location Reference not set.")
        self.location_ref.build(builder)

        if self.date_time_stamp is None:
            raise ValueError("DateTime not set.")

        self.date_time_stamp.build(builder)

        # Optional
        if self.reason_for_change is not None:
            self.reason_for_change.build(builder)

        builder.end("AuditRecord")

    def __lshift__(self, other):
        if not isinstance(other, (UserRef, LocationRef, DateTimeStamp, ReasonForChange,)):
            raise ValueError("AuditRecord cannot accept a child element of type %s" % other.__class__.__name__)

        # Order is important, apparently
        self.set_single_attribute(other, UserRef, 'user_ref')
        self.set_single_attribute(other, LocationRef, 'location_ref')
        self.set_single_attribute(other, DateTimeStamp, 'date_time_stamp')
        self.set_single_attribute(other, ReasonForChange, 'reason_for_change')
        return other


class MdsolHeaderText(ODMElement):
    """
    Header text for :class:`ItemDef` when shown in grid

    .. note:: this is a Medidata Rave Specific Element
    """

    def __init__(self, content, lang=None):
        """
        :param str content: Content for the Header Text
        :param str lang: Language specification for Header
        """
        self.content = content
        self.lang = lang

    def build(self, builder):
        """Build XML by appending to builder"""

        params = {}
        if self.lang is not None:
            params['xml:lang'] = self.lang

        builder.start('mdsol:HeaderText', params)
        builder.data(self.content)
        builder.end('mdsol:HeaderText')


class CodeListRef(ODMElement):
    """
    A reference to a :class:`CodeList` definition.
    """

    def __init__(self, oid):
        """
        :param oid: OID for :class:`CodeList`
        """
        self.oid = oid

    def build(self, builder):
        """Build XML by appending to builder"""
        builder.start('CodeListRef', {'CodeListOID': self.oid})
        builder.end('CodeListRef')


class MdsolLabelDef(ODMElement):
    """
    Label definition

    .. note:: This is a Medidata Rave Specific Element
    """

    def __init__(self, oid, name, field_number=None):
        """
        :param oid: OID for the MdsolLabelDef
        :param name: Name for the MdsolLabelDef
        :param int field_number: :attr:`FieldNumber` for the MdsolLabelDef
        """
        self.oid = oid
        self.name = name
        self.field_number = field_number
        #: Collection of :class:`HelpText`
        self.help_texts = []
        #: Collection of :class:`Translation`
        self.translations = []
        #: Collection of :class:`ViewRestriction`
        self.view_restrictions = []

    def build(self, builder):
        """Build XML by appending to builder"""

        params = dict(OID=self.oid, Name=self.name)
        if self.field_number is not None:
            params['FieldNumber'] = str(self.field_number)

        builder.start("mdsol:LabelDef", params)

        for translation in self.translations:
            translation.build(builder)

        for view_restriction in self.view_restrictions:
            view_restriction.build(builder)

        builder.end("mdsol:LabelDef")

    def __lshift__(self, other):
        """Override << operator"""
        if not isinstance(other, (MdsolViewRestriction, TranslatedText)):
            raise ValueError('MdsolLabelDef cannot accept a {0} as a child element'.format(other.__class__.__name__))
        self.set_list_attribute(other, TranslatedText, 'translations')
        self.set_list_attribute(other, MdsolViewRestriction, 'view_restrictions')

        return other


class MdsolReviewGroup(ODMElement):
    """
    Maps to Rave review groups for an :class:`ItemDef`

    .. note:: this is a Medidata Rave Specific Element
    """

    def __init__(self, name):
        """
        :param str name: Name for the MdsolReviewGroup
        """
        self.name = name

    def build(self, builder):
        """Build XML by appending to builder"""
        builder.start('mdsol:ReviewGroup', {})
        builder.data(self.name)
        builder.end('mdsol:ReviewGroup')


class CheckValue(ODMElement):
    """
    A value in a :class:`RangeCheck`
    """

    def __init__(self, value):
        """

        :param str value: Value for a :class:`RangeCheck`
        """
        self.value = value

    def build(self, builder):
        """Build XML by appending to builder"""
        builder.start('CheckValue', {})
        builder.data(str(self.value))
        builder.end('CheckValue')


class RangeCheck(ODMElement):
    """
    Rangecheck in Rave relates to QueryHigh QueryLow and NonConformantHigh and NonComformantLow
    for other types of RangeCheck, need to use an EditCheck (part of Rave's extensions to ODM)
    """

    def __init__(self, comparator, soft_hard):
        """
        :param str comparator: Comparator for RangeCheck (*LT*, *LE*, *GT*, *GE*, *EQ*, *NE*, *IN*, *NOTIN*)
        :param str soft_hard: Soft or Hard range check (*Soft*, *Hard*)
        """
        self._comparator = None
        self.comparator = comparator
        self._soft_hard = None
        self.soft_hard = soft_hard
        # ! :class:`CheckValue` for RangeCheck
        self.check_value = None
        # ! :class:`MeasurementUnitRef` for RangeCheck
        self.measurement_unit_ref = None

    @property
    def comparator(self):
        """returns the comparator"""
        return self._comparator

    @comparator.setter
    def comparator(self, value):
        """sets the comparator (with validation of input)"""
        if not isinstance(value, RangeCheckComparatorType):
            raise AttributeError("%s comparator is invalid in RangeCheck." % (value,))
        self._comparator = value

    @property
    def soft_hard(self):
        """returns the Soft or Hard range setting"""
        return self._soft_hard

    @soft_hard.setter
    def soft_hard(self, value):
        """sets the Soft or Hard range setting (with validation of input)"""
        if not isinstance(value, RangeCheckType):
            raise AttributeError("%s soft_hard invalid in RangeCheck." % (value,))
        self._soft_hard = value

    def build(self, builder):
        """Build XML by appending to builder"""
        params = dict(SoftHard=self.soft_hard.value, Comparator=self.comparator.value)
        builder.start("RangeCheck", params)
        if self.check_value is not None:
            self.check_value.build(builder)
        if self.measurement_unit_ref is not None:
            self.measurement_unit_ref.build(builder)
        builder.end("RangeCheck")

    def __lshift__(self, other):
        """Override << operator"""
        if not isinstance(other, (CheckValue, MeasurementUnitRef,)):
            raise ValueError('RangeCheck cannot accept a {0} as a child element'.format(other.__class__.__name__))

        self.set_single_attribute(other, CheckValue, 'check_value')
        self.set_single_attribute(other, MeasurementUnitRef, 'measurement_unit_ref')


class ItemDef(ODMElement):
    """
    An ItemDef describes a type of item that can occur within a study.
    Item properties include name, datatype, measurement units, range or codelist restrictions,
    and several other properties.
    """
    VALID_DATATYPES = [DataType.Text, DataType.Integer, DataType.Float, DataType.Date,
                       DataType.DateTime, DataType.Time]

    def __init__(self, oid, name, datatype,
                 length=None,
                 significant_digits=None,
                 sas_field_name=None,
                 sds_var_name=None,
                 origin=None,  # Not mapped in Rave
                 comment=None,
                 active=True,
                 control_type=None,
                 acceptable_file_extensions=None,
                 indent_level=0,
                 source_document_verify=False,
                 default_value=None,
                 sas_format=None,
                 sas_label=None,
                 query_future_date=False,
                 visible=True,
                 translation_required=False,
                 query_non_conformance=False,
                 other_visits=False,
                 can_set_item_group_date=False,
                 can_set_form_date=False,
                 can_set_study_event_date=False,
                 can_set_subject_date=False,
                 visual_verify=False,
                 does_not_break_signature=False,
                 date_time_format=None,
                 field_number=None,
                 variable_oid=None
                 ):
        """
        :param str oid: OID for ItemDef
        :param str name: Name for ItemDef
        :param str datatype: Datatype for ItemDef
        :param int length: Max. Length of content expected in Item Value
        :param int significant_digits: Max. Number of significant digits in Item Value
        :param str sas_field_name: SAS Name for the ItemDef
        :param str sds_var_name: SDS Variable Name
        :param str origin: Origin for the Variable
        :param str comment: Comment for the Variable
        :param bool active: Is the Variable Active? - *Rave Specific Attribute*
        :param ControlType control_type: Control Type for the Variable - *Rave Specific Attribute*
        :param str acceptable_file_extensions: File extensions for File Upload Control (separated by a comma)
            - *Rave Specific Attribute*
        :param int indent_level: Level of indentation of a field from the left-hand page margin.
            - *Rave Specific Attribute*
        :param bool source_document_verify: Does this Variable need to be SDV'ed? - *Rave Specific Attribute*
        :param str default_value: Value entered in this field is displayed as the default value in Rave EDC.
            - *Rave Specific Attribute*
        :param str sas_format: SAS variable format of maximum 25 alphanumeric characters.
        :param str sas_label: SAS label of maximum 256 alphanumeric characters.
        :param bool query_future_date: Generates a query when the Rave EDC user enters a future date in the field.
            - *Rave Specific Attribute*
        :param bool visible:  Indicates that the field displays on the form when the version is pushed to Rave EDC.
            - *Rave Specific Attribute*
        :param bool translation_required: Enables translation functionality for the selected field.
            - *Rave Specific Attribute*
        :param bool query_non_conformance: Generates a query when the Rave EDC user enters data in a format other than what
            has been defined for the variable. - *Rave Specific Attribute*
        :param bool other_visits: Display previous visit data - *Rave Specific Attribute*
        :param bool can_set_item_group_date: If a form contains log fields, this parameter assigns the date entered
            into the field as the date for the record (log line) - *Rave Specific Attribute*
        :param bool can_set_form_date: Observation Date of Form assigns the date entered into the field as the date for
            the form - *Rave Specific Attribute*
        :param bool can_set_study_event_date: Observation Date of Folder assigns the date entered into the field as the date
            for the folder - *Rave Specific Attribute*
        :param bool can_set_subject_date: Observation Date of Subject assigns the date entered into the field
            as the date for the Subject. - *Rave Specific Attribute*
        :param bool visual_verify: This parameter sets the field as a Visual Verify field in Rave DDE
            - *Rave Specific Attribute*
        :param bool does_not_break_signature: Indicates that the field (both derived and non-derived) does not
            participate in signature. - *Rave Specific Attribute*
        :param str date_time_format: Displays text boxes for the user to enter the day, month, and year according to the
            specified variable format. - *Rave Specific Attribute*
        :param str field_number: Number that displays to the right of a field label in Rave EDC to create a numbered list
            on the form. - *Rave Specific Attribute*
        :param variable_oid: OID for Variable - *Rave Specific Attribute*
        """
        self.oid = oid
        self.name = name

        if datatype not in ItemDef.VALID_DATATYPES:
            raise AttributeError('{0} is not a valid datatype!'.format(datatype))

        if control_type is not None:
            if not isinstance(control_type, ControlType):
                raise AttributeError("{0} is not a valid Control Type".format(control_type))

        if length is None:
            if datatype in [DataType.DateTime, DataType.Time, DataType.Date]:
                # Default this
                length = len(date_time_format)
            else:
                raise AttributeError('length must be set for all datatypes except Date/Time types')

        self.datatype = datatype
        self.length = length
        self.significant_digits = significant_digits
        self.sas_field_name = sas_field_name
        self.sds_var_name = sds_var_name
        self.origin = origin
        self.comment = comment
        self.active = active
        self.control_type = control_type
        self.acceptable_file_extensions = acceptable_file_extensions
        self.indent_level = indent_level
        self.source_document_verify = source_document_verify
        self.default_value = default_value
        self.sas_format = sas_format
        self.sas_label = sas_label
        self.query_future_date = query_future_date
        self.visible = visible
        self.translation_required = translation_required
        self.query_non_conformance = query_non_conformance
        self.other_visits = other_visits
        self.can_set_item_group_date = can_set_item_group_date
        self.can_set_form_date = can_set_form_date
        self.can_set_study_event_date = can_set_study_event_date
        self.can_set_subject_date = can_set_subject_date
        self.visual_verify = visual_verify
        self.does_not_break_signature = does_not_break_signature
        self.date_time_format = date_time_format
        self.field_number = field_number
        self.variable_oid = variable_oid

        #: Matching :class:`Question`
        self.question = None
        #: Matching :class:`CodeListRef`
        self.codelistref = None
        #: Collection of :class:`MeasurementUnitRef`
        self.measurement_unit_refs = []
        #: Collection of :class:`MdsolHelpText`
        self.help_texts = []
        #: Collection of :class:`MdsolViewRestriction`
        self.view_restrictions = []
        #: Collection of :class:`MdsolEntryRestriction`
        self.entry_restrictions = []
        #: Matching :class:`MdsolHeaderText`
        self.header_text = None
        #: Collection of :class:`MdsolReviewGroup`
        self.review_groups = []
        #: Collection of :class:`RangeCheck`
        self.range_checks = []

    def build(self, builder):
        """Build XML by appending to builder"""

        params = dict(OID=self.oid,
                      Name=self.name,
                      DataType=self.datatype.value,
                      Length=str(self.length),
                      )

        if self.date_time_format is not None:
            params['mdsol:DateTimeFormat'] = self.date_time_format

        params['mdsol:Active'] = bool_to_yes_no(self.active)

        if self.significant_digits is not None:
            params['SignificantDigits'] = str(self.significant_digits)

        if self.sas_field_name is not None:
            params['SASFieldName'] = self.sas_field_name

        if self.sds_var_name is not None:
            params['SDSVarName'] = self.sds_var_name

        if self.origin is not None:
            params['Origin'] = self.origin

        if self.comment is not None:
            params['Comment'] = self.comment

        if self.control_type is not None:
            params['mdsol:ControlType'] = self.control_type.value

        if self.acceptable_file_extensions is not None:
            params['mdsol:AcceptableFileExtensions'] = self.acceptable_file_extensions

        if self.default_value is not None:
            params['mdsol:DefaultValue'] = str(self.default_value)

        params['mdsol:SourceDocument'] = bool_to_yes_no(self.source_document_verify)
        params['mdsol:IndentLevel'] = str(self.indent_level)

        if self.sas_format is not None:
            params['mdsol:SASFormat'] = self.sas_format

        if self.sas_label is not None:
            params['mdsol:SASLabel'] = self.sas_label

        params['mdsol:QueryFutureDate'] = bool_to_yes_no(self.query_future_date)
        params['mdsol:Visible'] = bool_to_yes_no(self.visible)
        params['mdsol:TranslationRequired'] = bool_to_yes_no(self.translation_required)
        params['mdsol:QueryNonConformance'] = bool_to_yes_no(self.query_non_conformance)
        params['mdsol:OtherVisits'] = bool_to_yes_no(self.other_visits)
        params['mdsol:CanSetItemGroupDate'] = bool_to_yes_no(self.can_set_item_group_date)
        params['mdsol:CanSetFormDate'] = bool_to_yes_no(self.can_set_form_date)
        params['mdsol:CanSetStudyEventDate'] = bool_to_yes_no(self.can_set_study_event_date)
        params['mdsol:CanSetSubjectDate'] = bool_to_yes_no(self.can_set_subject_date)
        params['mdsol:VisualVerify'] = bool_to_yes_no(self.visual_verify)
        params['mdsol:DoesNotBreakSignature'] = bool_to_yes_no(self.does_not_break_signature)

        if self.field_number is not None:
            params['mdsol:FieldNumber'] = self.field_number

        if self.variable_oid is not None:
            params['mdsol:VariableOID'] = self.variable_oid

        builder.start("ItemDef", params)

        if self.question is not None:
            self.question.build(builder)

        if self.codelistref is not None:
            self.codelistref.build(builder)

        for mur in self.measurement_unit_refs:
            mur.build(builder)

        for range_check in self.range_checks:
            range_check.build(builder)

        if self.header_text is not None:
            self.header_text.build(builder)

        for view_restriction in self.view_restrictions:
            view_restriction.build(builder)

        for entry_restriction in self.entry_restrictions:
            entry_restriction.build(builder)

        for help_text in self.help_texts:
            help_text.build(builder)

        for review_group in self.review_groups:
            review_group.build(builder)

        builder.end("ItemDef")

    def __lshift__(self, other):
        """Override << operator"""

        # ExternalQuestion?,,
        # Role*, Alias*,
        # mdsol:HelpText?, mdsol:ViewRestriction* or mdsolEntryRestrictions*), (or mdsol:ReviewGroups*), mdsol:Label?)

        if not isinstance(other, (MdsolHelpText, MdsolEntryRestriction, MdsolViewRestriction, Question,
                                  MeasurementUnitRef, CodeListRef, MdsolHeaderText, MdsolReviewGroup, RangeCheck)):
            raise ValueError('ItemDef cannot accept a {0} as a child element'.format(other.__class__.__name__))

        self.set_single_attribute(other, Question, 'question')
        self.set_single_attribute(other, CodeListRef, 'codelistref')
        self.set_single_attribute(other, MdsolHeaderText, 'header_text')
        self.set_list_attribute(other, RangeCheck, 'range_checks')
        self.set_list_attribute(other, MeasurementUnitRef, 'measurement_unit_refs')
        self.set_list_attribute(other, MdsolHelpText, 'help_texts')
        self.set_list_attribute(other, MdsolViewRestriction, 'view_restrictions')
        self.set_list_attribute(other, MdsolEntryRestriction, 'entry_restrictions')
        self.set_list_attribute(other, MdsolReviewGroup, 'review_groups')
        return other


class Decode(ODMElement):
    """
    The displayed value relating to the CodedValue
    """

    def __init__(self):
        #: Collection of :class:`Translation` for the Decode
        self.translations = []

    def build(self, builder):
        """Build XML by appending to builder"""
        builder.start("Decode", {})
        for translation in self.translations:
            translation.build(builder)
        builder.end("Decode")

    def __lshift__(self, other):
        """Override << operator"""
        if not isinstance(other, TranslatedText):
            raise ValueError('Decode cannot accept child of type {0}'.format(other.__class__.__name__))
        self.translations.append(other)
        return other


class CodeListItem(ODMElement):
    """
    Defines an individual member value of a :class:`CodeList` including display format.
    The actual value is given, along with a set of print/display-forms.
    """

    def __init__(self, coded_value, order_number=None, specify=False):
        """
        :param str coded_value: Coded Value for CodeListItem
        :param int order_number: :attr:`OrderNumber` for the CodeListItem - Note: this is a
            Medidata Rave Extension, but upstream ODM has been updated to include the OrderNumber attribute
        :param bool specify: Does this have a Specify? option? - *Rave Specific Attribute*
        """
        self.coded_value = coded_value
        self.order_number = order_number
        self.specify = specify
        self.decode = None

    def build(self, builder):
        """Build XML by appending to builder"""
        params = dict(CodedValue=self.coded_value)
        if self.order_number is not None:
            params['mdsol:OrderNumber'] = str(self.order_number)

        if self.specify:
            params['mdsol:Specify'] = "Yes"

        builder.start("CodeListItem", params)
        if self.decode is not None:
            self.decode.build(builder)
        builder.end("CodeListItem")

    def __lshift__(self, other):
        """Override << operator"""
        if not isinstance(other, Decode):
            raise ValueError('CodelistItem cannot accept child of type {0}'.format(other.__class__.__name__))
        self.set_single_attribute(other, Decode, 'decode')
        return other


class CodeList(ODMElement):
    """
    Defines a discrete set of permitted values for an item.

    .. note:: Equates to a Rave Dictionary
    .. note:: Does not support ExternalCodeList
    """
    VALID_DATATYPES = [DataType.Integer, DataType.Text, DataType.Float, DataType.String]

    def __init__(self, oid, name, datatype, sas_format_name=None):
        """
        :param str oid: CodeList OID
        :param str name: Name of CodeList
        :param str datatype: DataType restricts the values that can appear in the CodeList whether internal or external
            (*integer* | *float* | *text* | *string* )
        :param str sas_format_name: SASFormatName must be a legal SAS format for CodeList
        """
        self.oid = oid
        self.name = name
        if datatype not in CodeList.VALID_DATATYPES:
            raise ValueError("{0} is not a valid CodeList datatype".format(datatype))
        self.datatype = datatype
        self.sas_format_name = sas_format_name
        #: Collection of :class:`CodeListItem`
        self.codelist_items = []

    def build(self, builder):
        """Build XML by appending to builder"""
        params = dict(OID=self.oid,
                      Name=self.name,
                      DataType=self.datatype.value)
        if self.sas_format_name is not None:
            params['SASFormatName'] = self.sas_format_name
        builder.start("CodeList", params)
        for item in self.codelist_items:
            item.build(builder)
        builder.end("CodeList")

    def __lshift__(self, other):
        """Override << operator"""
        if not isinstance(other, CodeListItem):
            raise ValueError('Codelist cannot accept child of type {0}'.format(other.__class__.__name__))
        self.set_list_attribute(other, CodeListItem, 'codelist_items')

        return other


class MdsolConfirmationMessage(ODMElement):
    """
    Form is saved confirmation message

    .. note:: this is a Medidata Rave Specific Element
    """

    def __init__(self, message, lang=None):
        """
        :param str message: Content of confirmation message
        :param str lang: Language declaration for Message
        """
        self.message = message
        self.lang = lang

    def build(self, builder):
        """Build XML by appending to builder"""
        params = {}
        if self.lang:
            params['xml:lang'] = self.lang
        builder.start('mdsol:ConfirmationMessage', params)
        builder.data(self.message)
        builder.end('mdsol:ConfirmationMessage')


class MdsolDerivationStep(ODMElement):
    """A derivation step modeled after the Architect Loader definition.

    .. note:: Do not use directly, use appropriate subclasses.
    .. note:: this is a Medidata Rave Specific Element
    """

    VALID_STEPS = VALID_DERIVATION_STEPS
    LRP_TYPES = LOGICAL_RECORD_POSITIONS

    def __init__(self,
                 variable_oid=None,
                 data_format=None,
                 form_oid=None,
                 folder_oid=None,
                 field_oid=None,
                 value=None,
                 function=None,
                 custom_function=None,
                 record_position=None,
                 form_repeat_number=None,
                 folder_repeat_number=None,
                 logical_record_position=None
                 ):
        """
        :param str variable_oid: OID for Variable targeted by Derivation
        :param str data_format: Format for Value
        :param str form_oid: OID for Form
        :param str folder_oid: OID for Folder
        :param str field_oid: OID for Field
        :param str value: Value for DerivationStep
        :param str custom_function: Name of Custom Function for DerivationStep
        :param int record_position: Record Position - If the field is a standard (non-log) field, enter 0
        :param int form_repeat_number: Repeat Number for Form for DerivationStep
        :param int folder_repeat_number: Repeat Number for Folder for DerivationStep
        :param LogicalRecordPositionType logical_record_position: LRP value for the DerivationStep
        """
        self.variable_oid = variable_oid
        self.data_format = data_format
        self.form_oid = form_oid
        self.folder_oid = folder_oid
        self.field_oid = field_oid
        self.value = value
        self._function = None
        self.function = function
        self.custom_function = custom_function
        self.record_position = record_position
        self.form_repeat_number = form_repeat_number
        self.folder_repeat_number = folder_repeat_number
        self._logical_record_position = None
        self.logical_record_position = logical_record_position

    @property
    def logical_record_position(self):
        """
        Get the Logical Record Position
        :return: the Logical Record Position
        """
        return self._logical_record_position

    @logical_record_position.setter
    def logical_record_position(self, value=None):
        if value is not None:
            if value not in MdsolDerivationStep.LRP_TYPES:
                raise AttributeError("Invalid Derivation Logical Record Position %s" % value)
        self._logical_record_position = value

    @property
    def function(self):
        """
        Return the Derivation Function
        :return:
        """
        return self._function

    @function.setter
    def function(self, value):
        if value is not None:
            if value not in MdsolDerivationStep.VALID_STEPS:
                raise AttributeError("Invalid derivation function %s" % value)
        self._function = value

    def build(self, builder):
        """Build XML by appending to builder"""
        params = dict()

        if self.variable_oid is not None:
            params['VariableOID'] = self.variable_oid

        if self.data_format is not None:
            params['DataFormat'] = self.data_format

        if self.folder_oid is not None:
            params['FolderOID'] = self.folder_oid

        if self.field_oid is not None:
            params['FieldOID'] = self.field_oid

        if self.form_oid is not None:
            params['FormOID'] = self.form_oid

        if self.value is not None:
            params['Value'] = self.value

        if self.function is not None:
            params['Function'] = self.function.value

        if self.custom_function is not None:
            params['CustomFunction'] = self.custom_function

        if self.record_position is not None:
            params['RecordPosition'] = str(self.record_position)

        if self.form_repeat_number is not None:
            params['FormRepeatNumber'] = str(self.form_repeat_number)

        if self.folder_repeat_number is not None:
            params['FolderRepeatNumber'] = str(self.folder_repeat_number)

        if self.logical_record_position is not None:
            params['LogicalRecordPosition'] = self.logical_record_position.value

        builder.start("mdsol:DerivationStep", params)
        builder.end("mdsol:DerivationStep")


class MdsolCheckStep(ODMElement):
    """A check step modeled after the Architect Loader definition.

    .. note:: Do not use directly, use appropriate subclasses.
    .. note:: this is a Medidata Rave Specific Element
    """

    VALID_STEPS = ALL_STEPS
    LRP_TYPES = LOGICAL_RECORD_POSITIONS

    def __init__(self,
                 variable_oid=None,
                 data_format=None,
                 form_oid=None,
                 folder_oid=None,
                 field_oid=None,
                 static_value=None,
                 function=None,
                 custom_function=None,
                 record_position=None,
                 form_repeat_number=None,
                 folder_repeat_number=None,
                 logical_record_position=None
                 ):

        """
        :param str variable_oid: OID for Variable targeted by CheckStep
        :param str data_format: Format for Value
        :param str form_oid: OID for Form
        :param str folder_oid: OID for Folder
        :param str field_oid: OID for Field
        :param str custom_function: Name of Custom Function for CheckStep
        :param int record_position: Record Position - If the field is a standard (non-log) field, enter 0
        :param int form_repeat_number: Repeat Number for Form for CheckStep
        :param int folder_repeat_number: Repeat Number for Folder for CheckStep
        :param LogicalRecordPositionType logical_record_position: LRP value for the CheckStep
        :param str static_value: Static Value for CheckStep
        :param StepType function: Check Function for CheckStep
        """
        self.variable_oid = variable_oid
        self.data_format = data_format
        self.form_oid = form_oid
        self.folder_oid = folder_oid
        self.field_oid = field_oid
        self.static_value = static_value
        self._function = None
        self.function = function
        self.custom_function = custom_function
        self.record_position = record_position
        self.form_repeat_number = form_repeat_number
        self.folder_repeat_number = folder_repeat_number
        self._logical_record_position = None
        self.logical_record_position = logical_record_position

    @property
    def logical_record_position(self):
        """
        Get the Logical Record Position
        :return: the Logical Record Position
        """
        return self._logical_record_position

    @logical_record_position.setter
    def logical_record_position(self, value=None):
        if value is not None:
            if value not in MdsolCheckStep.LRP_TYPES:
                raise AttributeError("Invalid Check Step Logical Record Position %s" % value)
        self._logical_record_position = value

    @property
    def function(self):
        return self._function

    @function.setter
    def function(self, value):
        if value is not None:
            if value not in MdsolCheckStep.VALID_STEPS:
                raise AttributeError("Invalid function %s" % value)
        self._function = value

    def build(self, builder):
        """Build XML by appending to builder"""
        params = dict()

        if self.variable_oid is not None:
            params['VariableOID'] = self.variable_oid

        if self.data_format is not None:
            params['DataFormat'] = self.data_format

        if self.folder_oid is not None:
            params['FolderOID'] = self.folder_oid

        if self.field_oid is not None:
            params['FieldOID'] = self.field_oid

        if self.form_oid is not None:
            params['FormOID'] = self.form_oid

        if self.static_value is not None:
            params['StaticValue'] = self.static_value

        if self.function is not None:
            params['Function'] = self.function.value

        if self.custom_function is not None:
            params['CustomFunction'] = self.custom_function

        if self.record_position is not None:
            params['RecordPosition'] = str(self.record_position)

        if self.form_repeat_number is not None:
            params['FormRepeatNumber'] = str(self.form_repeat_number)

        if self.folder_repeat_number is not None:
            params['FolderRepeatNumber'] = str(self.folder_repeat_number)

        if self.logical_record_position is not None:
            params['LogicalRecordPosition'] = self.logical_record_position.value

        builder.start("mdsol:CheckStep", params)
        builder.end("mdsol:CheckStep")


class MdsolCheckAction(ODMElement):
    """
    Check Action modeled after check action in Architect Loader spreadsheet.

    .. note:: Do not use directly, use appropriate sub-class.
    .. note:: This is a Medidata Rave Specific Element
    """

    def __init__(self,
                 variable_oid=None,
                 field_oid=None,
                 form_oid=None,
                 folder_oid=None,
                 record_position=None,
                 form_repeat_number=None,
                 folder_repeat_number=None,
                 check_action_type=None,
                 check_string=None,
                 check_options=None,
                 check_script=None
                 ):
        """
        :param str variable_oid: OID for the Variable that is the target of the CheckAction
        :param str field_oid: OID for the Field that is the target of the CheckAction
        :param str form_oid: OID for the Form that is the target of the CheckAction
        :param str folder_oid: OID for the Folder that is the target of the CheckAction
        :param int record_position: Record Position for the CheckAction
        :param int form_repeat_number: Form Repeat Number for the CheckAction
        :param int folder_repeat_number: Folder Repeat Number for the CheckAction
        :param str check_string: CheckAction String
        :param str check_options: CheckAction Options
        :param str check_script: CheckAction Script
        """
        self.variable_oid = variable_oid
        self.folder_oid = folder_oid
        self.field_oid = field_oid
        self.form_oid = form_oid
        self.record_position = record_position
        self.form_repeat_number = form_repeat_number
        self.folder_repeat_number = folder_repeat_number
        self._check_action_type = None
        self.check_action_type = check_action_type
        self.check_string = check_string
        self.check_options = check_options
        self.check_script = check_script

    @property
    def check_action_type(self):
        """return the CheckAction Type"""
        return self._check_action_type

    @check_action_type.setter
    def check_action_type(self, value):
        """Set the value for the CheckActionType, validating input"""
        if value is not None:
            if not isinstance(value, ActionType):
                raise AttributeError("Invalid check action %s" % value)
        self._check_action_type = value

    def build(self, builder):
        params = dict()

        if self.variable_oid is not None:
            params['VariableOID'] = self.variable_oid

        if self.field_oid is not None:
            params['FieldOID'] = self.field_oid

        if self.form_oid is not None:
            params['FormOID'] = self.form_oid

        if self.folder_oid is not None:
            params['FolderOID'] = self.folder_oid

        if self.record_position is not None:
            params['RecordPosition'] = str(self.record_position)

        if self.form_repeat_number is not None:
            params['FormRepeatNumber'] = str(self.form_repeat_number)

        if self.folder_repeat_number is not None:
            params['FolderRepeatNumber'] = str(self.folder_repeat_number)

        if self.check_action_type is not None:
            params['Type'] = self.check_action_type.value

        if self.check_string is not None:
            params['String'] = self.check_string

        if self.check_options is not None:
            params['Options'] = self.check_options

        if self.check_script is not None:
            params['Script'] = self.check_script

        builder.start("mdsol:CheckAction", params)
        builder.end("mdsol:CheckAction")


class MdsolEditCheckDef(ODMElement):
    """
    Extension for Rave edit checks

    .. note:: This is a Medidata Rave Specific Extension
    """

    def __init__(self, oid, active=True, bypass_during_migration=False, needs_retesting=False):
        """
        :param str oid: EditCheck OID
        :param bool active: Is this EditCheck active?
        :param bool bypass_during_migration: Bypass this EditCheck during a Study Migration
        :param bool needs_retesting: Does this EditCheck need Retesting?
        """
        self.oid = oid
        self.active = active
        self.bypass_during_migration = bypass_during_migration
        self.needs_retesting = needs_retesting
        #: Set of :class:`MdsolCheckStep` for this EditCheck
        self.check_steps = []
        #: Set of :class:`MdsolCheckAction` for this EditCheck
        self.check_actions = []

    def build(self, builder):
        """Build XML by appending to builder"""
        params = dict(OID=self.oid,
                      Active=bool_to_true_false(self.active),
                      BypassDuringMigration=bool_to_true_false(self.bypass_during_migration),
                      NeedsRetesting=bool_to_true_false(self.needs_retesting)
                      )

        builder.start('mdsol:EditCheckDef', params)
        for step in self.check_steps:
            step.build(builder)

        for action in self.check_actions:
            action.build(builder)
        builder.end('mdsol:EditCheckDef')

    def __lshift__(self, other):
        """Override << operator"""
        if not isinstance(other, (MdsolCheckStep, MdsolCheckAction,)):
            raise ValueError('EditCheck cannot accept a {0} as a child element'.format(other.__class__.__name__))
        self.set_list_attribute(other, MdsolCheckStep, 'check_steps')
        self.set_list_attribute(other, MdsolCheckAction, 'check_actions')


class MdsolProtocolDeviation(TransactionalElement):
    """
    Extension for Protocol Deviations in Rave
    
    .. note:: This is a Medidata Rave Specific Extension
    .. note:: This primarily exists as a mechanism for use by the Clinical Audit Record Service, but it is useful 
        to define for the builders
    """
    ALLOWED_TRANSACTION_TYPES = ["Insert"]

    def __init__(self, value, status, repeat_key=1, code=None, klass=None, transaction_type=None):
        """
        :param str value: Value for the Protocol Deviation 
        :param rwslib.builder_constants.ProtocolDeviationStatus status: 
        :param int repeat_key: RepeatKey for the Protocol Deviation
        :param basestring code: Protocol Deviation Code
        :param basestring klass: Protocol Deviation Class 
        :param transaction_type: Transaction Type for the Protocol Deviation
        """
        super(MdsolProtocolDeviation, self).__init__(transaction_type=transaction_type)
        self._status = None
        self._repeat_key = None
        self.status = status
        self.value = value
        self.repeat_key = repeat_key
        self.code = code
        self.pdclass = klass

    @property
    def repeat_key(self):
        return self._repeat_key

    @repeat_key.setter
    def repeat_key(self, value):
        if isinstance(value, int):
            self._repeat_key = value
        else:
            raise ValueError("RepeatKey should be an integer, not {}".format(value))

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        if isinstance(value, ProtocolDeviationStatus):
            self._status = value
        else:
            raise ValueError("Status {} is not a valid ProtocolDeviationStatus".format(value))

    def build(self, builder):
        """Build XML by appending to builder"""
        params = dict(Value=self.value,
                      Status=self.status.value,
                      ProtocolDeviationRepeatKey=self.repeat_key
                      )

        if self.code:
            params['Code'] = self.code
        if self.pdclass:
            params['Class'] = self.pdclass
        if self.transaction_type:
            params['TransactionType'] = self.transaction_type
        builder.start('mdsol:ProtocolDeviation', params)
        builder.end('mdsol:ProtocolDeviation')


class MdsolDerivationDef(ODMElement):
    """
    Extension for Rave derivations

    .. note:: This is a Medidata Rave Specific Extension
    """
    LRP_TYPES = LOGICAL_RECORD_POSITIONS

    def __init__(self, oid, active=True,
                 bypass_during_migration=False,
                 needs_retesting=False,
                 variable_oid=None,
                 field_oid=None,
                 form_oid=None,
                 folder_oid=None,
                 record_position=None,
                 form_repeat_number=None,
                 folder_repeat_number=None,
                 logical_record_position=None,
                 all_variables_in_folders=None,
                 all_variables_in_fields=None
                 ):
        """
        :param str oid: OID for Derivation
        :param bool active: Is this Derivation Active?
        :param bool bypass_during_migration: Bypass this Derivation on Study Migration?
        :param bool needs_retesting: Does this Derivation need retesting?
        :param str variable_oid: OID for target variable (eg OID for :class:`ItemDef`)
        :param str field_oid: OID for target field (eg OID for :class:`ItemDef`)
        :param str form_oid: OID for Form for target of Derivation (eg OID for :class:`FormDef`)
        :param str folder_oid: OID for Folder for target of Derivation (eg OID for :class:`StudyEventDef`)
        :param int record_position: Record Position for the Derivation
        :param int form_repeat_number: Form Repeat Number for the CheckAction
        :param int folder_repeat_number: Folder Repeat Number for the CheckAction
        :param LogicalRecordPositionType logical_record_position:
        :param bool all_variables_in_folders: Evaluates the derivation according to any field using the specified
            variable within a specific folder.
        :param bool all_variables_in_fields: Evaluates the derivation according to any field using the specified
            variable across the whole subject.
        """
        self.oid = oid
        self.active = active
        self.bypass_during_migration = bypass_during_migration
        self.needs_retesting = needs_retesting
        self.variable_oid = variable_oid
        self.field_oid = field_oid
        self.form_oid = form_oid
        self.folder_oid = folder_oid
        self.record_position = record_position
        self.form_repeat_number = form_repeat_number
        self.folder_repeat_number = folder_repeat_number
        self._logical_record_position = None
        self.logical_record_position = logical_record_position
        self.all_variables_in_folders = all_variables_in_folders
        self.all_variables_in_fields = all_variables_in_fields
        #: Set of :class:`MdsolDerivationStep` for this derivation
        self.derivation_steps = []

    @property
    def logical_record_position(self):
        """
        Get the Logical Record Position
        :return: the Logical Record Position
        """
        return self._logical_record_position

    @logical_record_position.setter
    def logical_record_position(self, value=None):
        if value is not None:
            if value not in MdsolCheckStep.LRP_TYPES:
                raise AttributeError("Invalid Derivation Def Logical Record Position %s" % value)
        self._logical_record_position = value

    def build(self, builder):
        """Build XML by appending to builder"""
        params = dict(
            OID=self.oid,
            Active=bool_to_true_false(self.active),
            BypassDuringMigration=bool_to_true_false(self.bypass_during_migration),
            NeedsRetesting=bool_to_true_false(self.needs_retesting)
        )

        if self.variable_oid is not None:
            params['VariableOID'] = self.variable_oid

        if self.field_oid is not None:
            params['FieldOID'] = self.field_oid

        if self.form_oid is not None:
            params['FormOID'] = self.form_oid

        if self.folder_oid is not None:
            params['FolderOID'] = self.folder_oid

        if self.record_position is not None:
            params['RecordPosition'] = str(self.record_position)

        if self.form_repeat_number is not None:
            params['FormRepeatNumber'] = str(self.form_repeat_number)

        if self.folder_repeat_number is not None:
            params['FolderRepeatNumber'] = str(self.folder_repeat_number)

        if self.all_variables_in_folders is not None:
            params['AllVariablesInFolders'] = bool_to_true_false(self.all_variables_in_folders)

        if self.all_variables_in_fields is not None:
            params['AllVariablesInFields'] = bool_to_true_false(self.all_variables_in_fields)

        if self.logical_record_position is not None:
            params['LogicalRecordPosition'] = self.logical_record_position.value

        builder.start('mdsol:DerivationDef', params)
        for step in self.derivation_steps:
            step.build(builder)
        builder.end('mdsol:DerivationDef')

    def __lshift__(self, other):
        """Override << operator"""
        if not isinstance(other, MdsolDerivationStep):
            raise ValueError('Derivation cannot accept a {0} as a child element'.format(other.__class__.__name__))
        self.set_list_attribute(other, MdsolDerivationStep, 'derivation_steps')


class MdsolCustomFunctionDef(ODMElement):
    """
    Extension for Rave Custom functions

    .. note:: This is a Medidata Rave Specific Extension
    .. note:: VB was deprecated in later Rave versions.
    """
    VB = "VB"  # VB was deprecated in later Rave versions.
    C_SHARP = "C#"
    SQL = "SQ"
    VALID_LANGUAGES = [C_SHARP, SQL, VB]

    def __init__(self, oid, code, language="C#"):
        """
        :param str oid: OID for CustomFunction
        :param str code: Content for the CustomFunction
        :param str language: Language for the CustomFunction
        """
        self.oid = oid
        self.code = code
        self.language = language

    def build(self, builder):
        """Build XML by appending to builder"""
        params = dict(OID=self.oid, Language=self.language)
        builder.start('mdsol:CustomFunctionDef', params)
        builder.data(self.code)
        builder.end('mdsol:CustomFunctionDef')


class MetaDataVersion(ODMElement):
    """
    A metadata version (MDV) defines the types of study events, forms, item groups, and items that form the study data.
    """

    def __init__(self, oid, name,
                 description=None,
                 primary_formoid=None,
                 default_matrix_oid=None,
                 delete_existing=False,
                 signature_prompt=None):
        """
        :param str oid: MDV OID
        :param str name: Name for MDV
        :param str description: Description for MDV
        :param str primary_formoid: OID of Primary Form - *Rave Specific Attribute*
        :param str default_matrix_oid: OID of Default Matrix - *Rave Specific Attribute*
        :param bool delete_existing: Overwrite the previous version - *Rave Specific Attribute*
        :param str signature_prompt: Prompt for Signature - *Rave Specific Attribute*
        """
        self.oid = oid
        self.name = name
        self.description = description
        self.primary_formoid = primary_formoid
        self.default_matrix_oid = default_matrix_oid
        self.delete_existing = delete_existing
        self.signature_prompt = signature_prompt
        self.confirmation_message = None
        self.protocol = None
        self.codelists = []
        self.item_defs = []
        self.label_defs = []
        self.item_group_defs = []
        self.form_defs = []
        self.study_event_defs = []
        self.edit_checks = []
        self.derivations = []
        self.custom_functions = []

    def build(self, builder):
        """Build XML by appending to builder"""

        params = dict(OID=self.oid, Name=self.name)

        if self.description is not None:
            params['Description'] = self.description

        if self.signature_prompt is not None:
            params['mdsol:SignaturePrompt'] = self.signature_prompt

        if self.primary_formoid is not None:
            params['mdsol:PrimaryFormOID'] = self.primary_formoid

        if self.default_matrix_oid is not None:
            params['mdsol:DefaultMatrixOID'] = self.default_matrix_oid

        params['mdsol:DeleteExisting'] = bool_to_yes_no(self.delete_existing)

        builder.start("MetaDataVersion", params)
        if self.protocol:
            self.protocol.build(builder)

        for event in self.study_event_defs:
            event.build(builder)

        for formdef in self.form_defs:
            formdef.build(builder)

        for itemgroupdef in self.item_group_defs:
            itemgroupdef.build(builder)

        for itemdef in self.item_defs:
            itemdef.build(builder)

        for codelist in self.codelists:
            codelist.build(builder)

        # Extensions must always come after core elements
        if self.confirmation_message:
            self.confirmation_message.build(builder)

        for labeldef in self.label_defs:
            labeldef.build(builder)

        for edit_check in self.edit_checks:
            edit_check.build(builder)

        for derivation in self.derivations:
            derivation.build(builder)

        for custom_function in self.custom_functions:
            custom_function.build(builder)

        builder.end("MetaDataVersion")

    def __lshift__(self, other):
        """Override << operator"""

        if not isinstance(other, (Protocol, StudyEventDef, FormDef, ItemGroupDef, ItemDef, MdsolLabelDef, CodeList,
                                  MdsolConfirmationMessage, MdsolEditCheckDef, MdsolDerivationDef,
                                  MdsolCustomFunctionDef)):
            raise ValueError('MetaDataVersion cannot accept a {0} as a child element'.format(other.__class__.__name__))

        self.set_single_attribute(other, Protocol, 'protocol')
        self.set_single_attribute(other, MdsolConfirmationMessage, 'confirmation_message')
        self.set_list_attribute(other, StudyEventDef, 'study_event_defs')
        self.set_list_attribute(other, FormDef, 'form_defs')
        self.set_list_attribute(other, ItemGroupDef, 'item_group_defs')
        self.set_list_attribute(other, MdsolLabelDef, 'label_defs')
        self.set_list_attribute(other, ItemDef, 'item_defs')
        self.set_list_attribute(other, CodeList, 'codelists')
        self.set_list_attribute(other, MdsolEditCheckDef, 'edit_checks')
        self.set_list_attribute(other, MdsolDerivationDef, 'derivations')
        self.set_list_attribute(other, MdsolCustomFunctionDef, 'custom_functions')  # NB. Current schema limits to 1
        return other


class Study(ODMElement):
    """
    This element collects static structural information about an individual study.
    """

    PROJECT = 'Project'
    GLOBAL_LIBRARY = 'GlobalLibrary Volume'
    PROJECT_TYPES = [PROJECT, GLOBAL_LIBRARY]

    def __init__(self, oid, project_type=None):
        """
        :param str oid: Study OID
        :param str project_type: Type of Project (Project or Global Library) - *Rave Specific Attribute*
        """
        self.oid = oid
        self.global_variables = None
        self.basic_definitions = None
        self.metadata_version = None
        #: set of :class:`StudyEventDef` for this Study element
        self.studyevent_defs = []
        if project_type is None:
            self.project_type = "Project"
        else:
            if project_type in Study.PROJECT_TYPES:
                self.project_type = project_type
            else:
                raise ValueError('Project type "{0}" not valid. Expected one of {1}'.format(project_type,
                                                                                            ','.join(
                                                                                                Study.PROJECT_TYPES)))

    def __lshift__(self, other):
        """Override << operator"""

        if not isinstance(other, (GlobalVariables, BasicDefinitions, MetaDataVersion)):
            raise ValueError('Study cannot accept a {0} as a child element'.format(other.__class__.__name__))

        self.set_single_attribute(other, GlobalVariables, 'global_variables')
        self.set_single_attribute(other, BasicDefinitions, 'basic_definitions')
        self.set_single_attribute(other, MetaDataVersion, 'metadata_version')

        return other

    def build(self, builder):
        """Build XML by appending to builder"""
        params = dict(OID=self.oid)
        params['mdsol:ProjectType'] = self.project_type

        builder.start("Study", params)

        # Ask children
        if self.global_variables is not None:
            self.global_variables.build(builder)

        if self.basic_definitions is not None:
            self.basic_definitions.build(builder)

        if self.metadata_version is not None:
            self.metadata_version.build(builder)

        builder.end("Study")
