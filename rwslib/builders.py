# -*- coding: utf-8 -*-
__author__ = 'isparks'

import uuid
from xml.etree import cElementTree as ET
from datetime import datetime
from string import ascii_letters
from rwslib.builder_constants import *

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
        return ET.tostring(builder.close(),encoding='utf-8').decode('utf-8')

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


class UserRef(ODMElement):
    def __init__(self, oid):
        self.oid = oid

    def build(self, builder):
        builder.start("UserRef", dict(UserOID=self.oid))
        builder.end("UserRef")


class LocationRef(ODMElement):
    def __init__(self, oid):
        self.oid = oid

    def build(self, builder):
        builder.start("LocationRef", dict(LocationOID=self.oid))
        builder.end("LocationRef")


class ReasonForChange(ODMElement):
    def __init__(self, reason):
        self.reason = reason

    def build(self, builder):
        builder.start("ReasonForChange", {})
        builder.data(self.reason)
        builder.end("ReasonForChange")


class DateTimeStamp(ODMElement):
    def __init__(self, date_time):
        self.date_time = date_time

    def build(self, builder):
        builder.start("DateTimeStamp", {})
        if isinstance(self.date_time, datetime):
            builder.data(dt_to_iso8601(self.date_time))
        else:
            builder.data(self.date_time)
        builder.end("DateTimeStamp")


class AuditRecord(ODMElement):
    """AuditRecord is supported only by ItemData in Rave"""
    EDIT_MONITORING = 'Monitoring'
    EDIT_DATA_MANAGEMENT = 'DataManagement'
    EDIT_DB_AUDIT = 'DBAudit'
    EDIT_POINTS = [EDIT_MONITORING, EDIT_DATA_MANAGEMENT, EDIT_DB_AUDIT]

    def __init__(self, edit_point=None, used_imputation_method=None, identifier=None, include_file_oid=None):
        self._edit_point = None
        self.edit_point = edit_point
        self.used_imputation_method = used_imputation_method
        self._id = None
        self.id = identifier
        self.include_file_oid = include_file_oid
        self.user_ref = None
        self.location_ref = None
        self.reason_for_change = None
        self.date_time_stamp = None

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if value not in [None, ''] and str(value).strip() != '':
            val = str(value).strip()[0]
            if val not in VALID_ID_CHARS:
                raise AttributeError('%s id cannot start with "%s" character' % (self.__class__.__name__, val,))
        self._id = value

    @property
    def edit_point(self):
        return self._edit_point

    @edit_point.setter
    def edit_point(self, value):
        if value is not None:
            if value not in self.EDIT_POINTS:
                raise AttributeError('%s edit_point must be one of %s not %s' % (
                    self.__class__.__name__, ','.join(self.EDIT_POINTS), value,))
        self._edit_point = value

    def build(self, builder):
        params = {}

        if self.edit_point is not None:
            params["EditPoint"] = self.edit_point

        if self.used_imputation_method is not None:
            params['UsedImputationMethod'] = bool_to_yes_no(self.used_imputation_method)

        if self.id is not None:
            params['ID'] = str(self.id)

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


class TransactionalElement(ODMElement):
    """Models an ODM Element that is allowed a transaction type. Different elements have different
       allowed transaction types"""
    ALLOWED_TRANSACTION_TYPES = []

    def __init__(self, transaction_type):
        self._transaction_type = None
        self.transaction_type = transaction_type

    @property
    def transaction_type(self):
        return self._transaction_type

    @transaction_type.setter
    def transaction_type(self, value):
        if value is not None:
            if value not in self.ALLOWED_TRANSACTION_TYPES:
                raise AttributeError('%s transaction_type element must be one of %s not %s' % (
                    self.__class__.__name__, ','.join(self.ALLOWED_TRANSACTION_TYPES), value,))
        self._transaction_type = value


class MdsolQuery(ODMElement):
    """MdsolQuery extension element for Queries at item level only"""

    def __init__(self, value=None, query_repeat_key=None, recipient=None, status=None, requires_response=None,
                 response=None):
        self.value = value
        self.query_repeat_key = query_repeat_key
        self.recipient = recipient
        self._status = None
        self.status = status
        self.requires_response = requires_response
        self.response = response

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        if value is not None:
            if not isinstance(value, QueryStatusType):
                raise AttributeError("%s action type is invalid in mdsol:Query." % (value,))
        self._status = value

    def build(self, builder):
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
        super(self.__class__, self).__init__(transaction_type)
        self.itemoid = itemoid
        self.value = value

        self.specify_value = specify_value
        self.lock = lock
        self.freeze = freeze
        self.verify = verify
        self.audit_record = None
        self.queries = []
        self.measurement_unit_ref = None

    def build(self, builder):
        """Build XML by appending to builder
           <ItemData ItemOID="MH_DT" Value="06 Jan 2009" TransactionType="Insert">
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

        for query in self.queries:
            query.build(builder)
        builder.end("ItemData")

    def __lshift__(self, other):
        if not isinstance(other, (MeasurementUnitRef, AuditRecord, MdsolQuery,)):
            raise ValueError("ItemData object can only receive MeasurementUnitRef, AuditRecord or MdsolQuery objects")
        self.set_single_attribute(other, MeasurementUnitRef, 'measurement_unit_ref')
        self.set_single_attribute(other, AuditRecord, 'audit_record')
        self.set_list_attribute(other, MdsolQuery, 'queries')
        return other


class ItemGroupData(TransactionalElement):
    """Models the ODM ItemGroupData object.
       Note no name for the ItemGroupData element is required. This is built automatically by the form.
    """
    ALLOWED_TRANSACTION_TYPES = ['Insert', 'Update', 'Upsert', 'Context']

    def __init__(self, transaction_type=None, item_group_repeat_key=None, whole_item_group=False):
        super(self.__class__, self).__init__(transaction_type)
        self.item_group_repeat_key = item_group_repeat_key
        self.whole_item_group = whole_item_group
        self.items = {}

    def __lshift__(self, other):
        """Override << operator"""
        if not isinstance(other, ItemData):
            raise ValueError("ItemGroupData object can only receive ItemData object")

        if other.itemoid in self.items:
            raise ValueError("ItemGroupData object with that itemoid is already in the ItemGroupData object")

        self.items[other.itemoid] = other
        return other

    def build(self, builder, formname):
        """Build XML by appending to builder
        """
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
        builder.end("ItemGroupData")


class FormData(TransactionalElement):
    """Models the ODM FormData object"""
    ALLOWED_TRANSACTION_TYPES = ['Insert', 'Update']

    def __init__(self, formoid, transaction_type=None, form_repeat_key=None):
        super(self.__class__, self).__init__(transaction_type)
        self.formoid = formoid
        self.form_repeat_key = form_repeat_key
        self.itemgroups = []

    def __lshift__(self, other):
        """Override << operator"""
        if not isinstance(other, ItemGroupData):
            raise ValueError("FormData object can only receive ItemGroupData object")
        self.set_list_attribute(other, ItemGroupData, 'itemgroups')
        return other

    def build(self, builder):
        """Build XML by appending to builder

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
        builder.end("FormData")


class StudyEventData(TransactionalElement):
    """Models the ODM StudyEventData object"""
    ALLOWED_TRANSACTION_TYPES = ['Insert', 'Update', 'Remove', 'Context']

    def __init__(self, study_event_oid, transaction_type="Update", study_event_repeat_key=None):
        super(self.__class__, self).__init__(transaction_type)
        self.study_event_oid = study_event_oid
        self.study_event_repeat_key = study_event_repeat_key
        self.forms = []

    def __lshift__(self, other):
        """Override << operator"""
        if not isinstance(other, FormData):
            raise ValueError("StudyEventData object can only receive FormData object")
        self.set_list_attribute(other, FormData, 'forms')
        return other

    def build(self, builder):
        """Build XML by appending to builder

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
        builder.end("StudyEventData")


class SubjectData(TransactionalElement):
    """Models the ODM SubjectData and ODM SiteRef objects"""
    ALLOWED_TRANSACTION_TYPES = ['Insert', 'Update', 'Upsert']

    def __init__(self, sitelocationoid, subject_key, subject_key_type="SubjectName", transaction_type="Update"):
        super(self.__class__, self).__init__(transaction_type)
        self.sitelocationoid = sitelocationoid
        self.subject_key = subject_key
        self.subject_key_type = subject_key_type
        self.study_events = []  # Can have collection
        self.audit_record = None

    def __lshift__(self, other):
        """Override << operator"""
        if not isinstance(other, (StudyEventData, AuditRecord,)):
            raise ValueError("SubjectData object can only receive StudyEventData or AuditRecord object")

        self.set_list_attribute(other, StudyEventData, 'study_events')
        self.set_single_attribute(other, AuditRecord, 'audit_record')

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

        builder.end("SubjectData")


class ClinicalData(ODMElement):
    """Models the ODM ClinicalData object"""

    def __init__(self, projectname, environment, metadata_version_oid="1"):
        self.projectname = projectname
        self.environment = environment
        self.metadata_version_oid = metadata_version_oid
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
    """GlobalVariables Metadata element"""

    def __init__(self, protocol_name, name=None, description=''):
        """Name and description are not important. protocol_name maps to the Rave project name"""
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
    """Represents a language and a translated text for that language"""

    def __init__(self, text, lang=None):
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
    def __init__(self):
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
    """A measurement unit"""

    def __init__(self,
                 oid,
                 name,
                 unit_dictionary_name=None,
                 constant_a=1,
                 constant_b=1,
                 constant_c=0,
                 constant_k=0,
                 standard_unit=False):
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
    """Container for Measurement units"""

    def __init__(self):
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
    def __init__(self, oid, order_number, mandatory):
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
    """Protocol child of MetaDataVersion, holder of StudyEventRefs"""

    def __init__(self):
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
    def __init__(self, oid, order_number, mandatory):
        self.oid = oid
        self.order_number = order_number
        self.mandatory = mandatory

    def build(self, builder):
        params = dict(FormOID=self.oid,
                      OrderNumber=str(self.order_number),
                      Mandatory=bool_to_yes_no(self.mandatory)
                      )
        builder.start('FormRef', params)
        builder.end('FormRef')


class StudyEventDef(ODMElement):
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
    def __init__(self, oid, order_number, mandatory=True):
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
    """Help element for FormDefs and ItemDefs"""

    def __init__(self, lang, content):
        self.lang = lang
        self.content = content

    def build(self, builder):
        builder.start('mdsol:HelpText', {'xml:lang': self.lang})
        builder.data(self.content)
        builder.end('mdsol:HelpText')


class MdsolViewRestriction(ODMElement):
    """ViewRestriction for FormDefs and ItemDefs"""

    def __init__(self, rolename):
        self.rolename = rolename

    def build(self, builder):
        builder.start('mdsol:ViewRestriction', {})
        builder.data(self.rolename)
        builder.end('mdsol:ViewRestriction')


class MdsolEntryRestriction(ODMElement):
    """EntryRestriction for FormDefs and ItemDefs"""

    def __init__(self, rolename):
        self.rolename = rolename

    def build(self, builder):
        builder.start('mdsol:EntryRestriction', {})
        builder.data(self.rolename)
        builder.end('mdsol:EntryRestriction')


class FormDef(ODMElement):
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
        self.itemgroup_refs = []
        self.helptexts = []  # Not clear that Rave can accept multiple from docs
        self.view_restrictions = []
        self.entry_restrictions = []

    def build(self, builder):
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
    """A reference to a label on a form"""

    def __init__(self, oid, order_number):
        self.oid = oid
        self.order_number = order_number

    def build(self, builder):
        params = dict(LabelOID=self.oid,
                      OrderNumber=str(self.order_number),
                      )

        builder.start('mdsol:LabelRef', params)
        builder.end('mdsol:LabelRef')


class MdsolAttribute(ODMElement):
    def __init__(self, namespace, name, value, transaction_type='Insert'):
        self.namespace = namespace
        self.name = name
        self.value = value
        self.transaction_type = transaction_type

    def build(self, builder):
        params = dict(Namespace=self.namespace,
                      Name=self.name,
                      Value=self.value,
                      TransactionType=self.transaction_type,
                      )

        builder.start('mdsol:Attribute', params)
        builder.end('mdsol:Attribute')


class ItemRef(ODMElement):
    def __init__(self, oid, order_number, mandatory=False, key_sequence=None,
                 imputation_method_oid=None, role=None, role_codelist_oid=None):
        self.oid = oid
        self.order_number = order_number
        self.mandatory = mandatory
        self.key_sequence = key_sequence
        self.imputation_method_oid = imputation_method_oid
        self.role = role
        self.role_codelist_oid = role_codelist_oid
        self.attributes = []

    def build(self, builder):

        params = dict(ItemOID=self.oid,
                      OrderNumber=str(self.order_number),
                      Mandatory=bool_to_yes_no(self.mandatory)
                      )

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
    def __init__(self, oid, name, repeating=False, is_reference_data=False, sas_dataset_name=None,
                 domain=None, origin=None, role=None, purpose=None, comment=None):
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
        self.item_refs = []
        self.label_refs = []

    def build(self, builder):

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
    def __init__(self):
        self.translations = []

    def __lshift__(self, other):
        """Override << operator"""

        if not isinstance(other, (TranslatedText)):
            raise ValueError('Question cannot accept a {0} as a child element'.format(other.__class__.__name__))
        self.set_list_attribute(other, TranslatedText, 'translations')
        return other

    def build(self, builder):
        """Questions can contain translations"""
        builder.start('Question', {})
        for translation in self.translations:
            translation.build(builder)
        builder.end('Question')


class MeasurementUnitRef(ODMElement):
    def __init__(self, oid, order_number=None):
        self.oid = oid
        self.order_number = order_number

    def build(self, builder):
        params = dict(MeasurementUnitOID=self.oid)
        if self.order_number is not None:
            params['mdsol:OrderNumber'] = str(self.order_number)

        builder.start('MeasurementUnitRef', params)
        builder.end('MeasurementUnitRef')


class MdsolHeaderText(ODMElement):
    """Header text for ItemDef when showed in grid"""

    def __init__(self, content, lang=None):
        self.content = content
        self.lang = lang

    def build(self, builder):
        params = {}
        if self.lang is not None:
            params['xml:lang'] = self.lang

        builder.start('mdsol:HeaderText', params)
        builder.data(self.content)
        builder.end('mdsol:HeaderText')


class CodeListRef(ODMElement):
    """CodeListRef: a reference a codelist within an ItemDef"""

    def __init__(self, oid):
        self.oid = oid

    def build(self, builder):
        builder.start('CodeListRef', {'CodeListOID': self.oid})
        builder.end('CodeListRef')


class MdsolLabelDef(ODMElement):
    """Label definition"""

    def __init__(self, oid, name, field_number=None):
        self.oid = oid
        self.name = name
        self.field_number = field_number
        self.help_texts = []
        self.translations = []
        self.view_restrictions = []

    def build(self, builder):
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
    """Maps to Rave review groups for an Item"""

    def __init__(self, name):
        self.name = name

    def build(self, builder):
        builder.start('mdsol:ReviewGroup', {})
        builder.data(self.name)
        builder.end('mdsol:ReviewGroup')


class CheckValue(ODMElement):
    """A value in a RangeCheck"""

    def __init__(self, value):
        self.value = value

    def build(self, builder):
        builder.start('CheckValue', {})
        builder.data(str(self.value))
        builder.end('CheckValue')


class RangeCheck(ODMElement):
    """
        Rangecheck in Rave relates to QueryHigh QueryLow and NonConformandHigh and NonComformanLow
       for other types of RangeCheck, need to use an EditCheck (part of Rave's extensions to ODM)
    """

    def __init__(self, comparator, soft_hard):
        self._comparator = None
        self.comparator = comparator
        self._soft_hard = None
        self.soft_hard = soft_hard
        self.check_value = None
        self.measurement_unit_ref = None

    @property
    def comparator(self):
        return self._comparator

    @comparator.setter
    def comparator(self, value):
        if not isinstance(value, RangeCheckComparatorType):
            raise AttributeError("%s comparator is invalid in RangeCheck." % (value,))
        self._comparator = value

    @property
    def soft_hard(self):
        return self._soft_hard

    @soft_hard.setter
    def soft_hard(self, value):
        if not isinstance(value, RangeCheckType):
            raise AttributeError("%s soft_hard invalid in RangeCheck." % (value,))
        self._soft_hard = value

    def build(self, builder):
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

        self.question = None
        self.codelistref = None
        self.measurement_unit_refs = []
        self.help_texts = []
        self.view_restrictions = []
        self.entry_restrictions = []
        self.header_text = None
        self.review_groups = []
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
    def __init__(self):
        self.translations = []

    def build(self, builder):
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
    def __init__(self, coded_value, order_number=None, specify=False):
        self.coded_value = coded_value
        self.order_number = order_number
        self.specify = specify
        self.decode = None

    def build(self, builder):
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
    """A container for CodeListItems equivalent of Rave Dictionary"""
    VALID_DATATYPES = [DataType.Integer, DataType.Text, DataType.Float, DataType.String]

    def __init__(self, oid, name, datatype, sas_format_name=None):
        self.oid = oid
        self.name = name
        if datatype not in CodeList.VALID_DATATYPES:
            raise ValueError("{0} is not a valid CodeList datatype".format(datatype))
        self.datatype = datatype
        self.sas_format_name = sas_format_name
        self.codelist_items = []

    def build(self, builder):
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
    """Form is saved confirmation message"""

    def __init__(self, message, lang=None):
        self.message = message
        self.lang = lang

    def build(self, builder):
        params = {}
        if self.lang:
            params['xml:lang'] = self.lang
        builder.start('mdsol:ConfirmationMessage', params)
        builder.data(self.message)
        builder.end('mdsol:ConfirmationMessage')


class MdsolDerivationStep(ODMElement):
    """A derivation step modeled after the Architect Loader definition.
       Do not use directly, use appropriate subclasses.
    """
    VALID_STEPS = VALID_DERIVATION_STEPS

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
        self.logical_record_position = logical_record_position

    @property
    def function(self):
        return self._function

    @function.setter
    def function(self, value):
        if value is not None:
            if value not in MdsolDerivationStep.VALID_STEPS:
                raise AttributeError("Invalid derivation function %s" % value)
        self._function = value

    def build(self, builder):
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
            params['LogicalRecordPosition'] = self.logical_record_position

        builder.start("mdsol:DerivationStep", params)
        builder.end("mdsol:DerivationStep")


class MdsolCheckStep(ODMElement):
    """A check step modeled after the Architect Loader definition.
       Do not use directly, use appropriate subclasses.
    """
    VALID_STEPS = ALL_STEPS

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
        self.logical_record_position = logical_record_position

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
            params['LogicalRecordPosition'] = self.logical_record_position

        builder.start("mdsol:CheckStep", params)
        builder.end("mdsol:CheckStep")


class MdsolCheckAction(ODMElement):
    """
    Check Action modeled after check action in Architect Loader spreadsheet.
    Do not use directly, use appropriate sub-class.
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
        return self._check_action_type

    @check_action_type.setter
    def check_action_type(self, value):
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
    """Extension for Rave edit checks"""

    def __init__(self, oid, active=True, bypass_during_migration=False, needs_retesting=False):
        self.oid = oid
        self.active = active
        self.bypass_during_migration = bypass_during_migration
        self.needs_retesting = needs_retesting
        self.check_steps = []
        self.check_actions = []

    def build(self, builder):
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


class MdsolDerivationDef(ODMElement):
    """Extension for Rave derivations"""

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
        self.logical_record_position = logical_record_position
        self.all_variables_in_folders = all_variables_in_folders
        self.all_variables_in_fields = all_variables_in_fields
        self.derivation_steps = []

    def build(self, builder):
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
            params['LogicalRecordPosition'] = self.logical_record_position

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
    """Extension for Rave Custom functions"""
    VB = "VB"  # VB was deprecated in later Rave versions.
    C_SHARP = "C#"
    SQL = "SQ"
    VALID_LANGUAGES = [C_SHARP, SQL, VB]

    def __init__(self, oid, code, language="C#"):
        self.oid = oid
        self.code = code
        self.language = language

    def build(self, builder):
        params = dict(OID=self.oid, Language=self.language)
        builder.start('mdsol:CustomFunctionDef', params)
        builder.data(self.code)
        builder.end('mdsol:CustomFunctionDef')


class MetaDataVersion(ODMElement):
    """MetaDataVersion, child of study"""

    def __init__(self, oid, name,
                 description=None,
                 primary_formoid=None,
                 default_matrix_oid=None,
                 delete_existing=False,
                 signature_prompt=None):
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
    """ODM Study Metadata element"""

    PROJECT = 'Project'
    GLOBAL_LIBRARY = 'GlobalLibrary Volume'
    PROJECT_TYPES = [PROJECT, GLOBAL_LIBRARY]

    def __init__(self, oid, project_type=None):
        self.oid = oid
        self.global_variables = None
        self.basic_definitions = None
        self.metadata_version = None
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
