# -*- coding: utf-8 -*-
__author__ = 'isparks'
"""
builders.py provides convenience classes for building ODM documents for clinical data and metadata post messages.
"""

import uuid
from xml.etree import cElementTree as ET
from datetime import datetime


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


def indent(elem, level=0):
    """Indent a elementree structure"""
    i = "\n" + level * "  "
    if len(elem):
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
    builder.start(tag)
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
        raise NotImplementedError('__lshift__ must be overriden in descendant classes.')

    def add(self, *args):
        """Like call but adds a set of args"""
        for child in args:
            self << child
        return self


class TransactionalElement(ODMElement):
    """Models an ODM Element that is allowed a transaction type. Different elements have different
       allowed transaction types"""
    ALLOWED_TRANSACTION_TYPES = []

    def __init__(self, transaction_type):
        self._transaction_type = None
        self.transaction_type = transaction_type
        return self

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

        # Ask children (queries etc not added yet)
        # for item  in self.items.values():
        #   item.build(builder)
        builder.end("ItemData")


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

        if other in self.itemgroups:
            raise ValueError("ItemGroupData object is already in the FormData object")

        self.itemgroups.append(other)
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
        self.study_event_repeat_key = str(study_event_repeat_key)
        self.forms = []

    def __lshift__(self, other):
        """Override << operator"""
        if not isinstance(other, FormData):
            raise ValueError("StudyEventData object can only receive FormData object")

        if other in self.forms:
            raise ValueError("FormData object is already in the StudyEventData object")

        self.forms.append(other)
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

    def __lshift__(self, other):
        """Override << operator"""
        if not isinstance(other, StudyEventData):
            raise ValueError("SubjectData object can only receive StudyEventData object")

        if other in self.study_events:
            raise ValueError("StudyEventData object is already in the SubjectData object")

        self.study_events.append(other)
        return other

    def build(self, builder):
        """Build XML by appending to builder"""
        params = dict(SubjectKey=self.subject_key)
        params['mdsol:SubjectKeyType'] = self.subject_key_type

        if self.transaction_type is not None:
            params["TransactionType"] = self.transaction_type

        builder.start("SubjectData", params)

        builder.start("SiteRef", {'LocationOID': self.sitelocationoid})
        builder.end("SiteRef")

        # Ask children
        for event in self.study_events:
            event.build(builder)
        builder.end("SubjectData")


class ClinicalData(ODMElement):
    """Models the ODM ClinicalData object"""

    def __init__(self, projectname, environment):
        self.projectname = projectname
        self.environment = environment
        self.subject_data = None

    def __lshift__(self, other):
        """Override << operator"""
        if self.subject_data is not None:
            raise ValueError("Message already contains a SubjectData object")

        if not isinstance(other, SubjectData):
            raise ValueError("ClinicalData object can only receive SubjectData object")
        self.subject_data = other
        return other

    def build(self, builder):
        """Build XML by appending to builder"""
        params = dict(MetaDataVersionOID='1',
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
        self.filetype = ODM.FILETYPE_TRANSACTIONAL if filetype is None else ODM.FILETYPE_SNAPSHOT

        # Create unique fileoid if none given
        self.fileoid = str(uuid.uuid4()) if fileoid is None else fileoid

    def __lshift__(self, other):
        """Override << operator"""
        if not isinstance(other, (ClinicalData, Study,)):
            raise ValueError("ODM object can only receive ClinicalData or Study object")
        self.clinical_data = other
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


DATATYPE_TEXT = 'text'
DATATYPE_INTEGER = 'integer'
DATATYPE_FLOAT = 'float'
DATATYPE_DATE = 'date'
DATATYPE_DATETIME = 'datetime'
DATATYPE_TIME = 'time'
DATATYPE_STRING = 'string'  # Used only by codelists


class GlobalVariables(ODMElement):
    """GlobalVariables Metadata element"""

    def __init__(self, protocol_name, name=None, description=''):
        """Name and description are not important. protocol_name maps to the Rave project name"""
        self.protocol_name = protocol_name
        self.name = name if name is not None else protocol_name
        self.description = description

    def build(self, builder):
        """Build XML by appending to builder"""
        builder.start("GlobalVariables")
        make_element(builder, 'StudyName', self.name)
        make_element(builder, 'StudyDescription', self.description)
        make_element(builder, 'ProtocolName', self.protocol_name)
        builder.end("GlobalVariables")

    def __lshift__(self, other):
        """Override << operator"""
        raise ValueError("GlobalVariables does not accept any children")


class TranslatedText(ODMElement):
    """Represents a language and a translated text for that language"""

    def __init__(self, text, lang=None):
        self.text = text
        self.lang = lang

    def __lshift__(self, other):
        """Override << operator"""
        raise ValueError("TranslatedText does not accept any children")

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
        self.translations.append(other)

    def build(self, builder):
        """Build XML by appending to builder"""
        builder.start("Symbol")
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
        self.symbols.append(other)
        return other


class BasicDefinitions(ODMElement):
    """Container for Measurement units"""

    def __init__(self):
        self.measurement_units = []

    def build(self, builder):
        """Build XML by appending to builder"""
        builder.start("BasicDefinitions")
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

    def __lshift__(self, other):
        """No children"""
        raise ValueError("StudyEventRef does not accept any child elements")

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
        builder.start("Protocol")
        for child in self.study_event_refs:
            child.build(builder)
        builder.end("Protocol")

    def __lshift__(self, other):
        """Override << operator"""
        if not isinstance(other, (StudyEventRef,)):
            raise ValueError('Protocol cannot accept a {0} as a child element'.format(other.__class__.__name__))
        self.study_event_refs.append(other)


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

    def __lshift__(self, other):
        """Override << operator"""
        raise ValueError("FormRef does not accept any children")


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
        self.formrefs.append(other)


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

    def __lshift__(self, other):
        """Override << operator"""
        raise ValueError("ItemGroupRef does not accept any child elements.")


class MdsolHelpText(ODMElement):
    """Help element for FormDefs and ItemDefs"""

    def __init__(self, lang, content):
        self.lang = lang
        self.content = content

    def build(self, builder):
        builder.start('mdsol:HelpText', {'xml:lang': self.lang})
        builder.data(self.content)
        builder.end('mdsol:HelpText')

    def __lshift__(self, other):
        """Override << operator"""
        raise ValueError("mdsol:HelpText does not accept any child elements.")


class MdsolViewRestriction(ODMElement):
    """ViewRestriction for FormDefs and ItemDefs"""

    def __init__(self, rolename):
        self.rolename = rolename

    def build(self, builder):
        builder.start('mdsol:ViewRestriction')
        builder.data(self.rolename)
        builder.end('mdsol:ViewRestriction')

    def __lshift__(self, other):
        raise ValueError("mdsol:ViewRestriction does not accept any child elements.")


class MdsolEntryRestriction(ODMElement):
    """EntryRestriction for FormDefs and ItemDefs"""

    def __init__(self, rolename):
        self.rolename = rolename

    def build(self, builder):
        builder.start('mdsol:EntryRestriction')
        builder.data(self.rolename)
        builder.end('mdsol:EntryRestriction')

    def __lshift__(self, other):
        raise ValueError("mdsol:EntryRestriction does not accept any child elements.")


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

        if isinstance(other, ItemGroupRef):
            self.itemgroup_refs.append(other)

        if isinstance(other, MdsolHelpText):
            self.helptexts.append(other)

        if isinstance(other, MdsolViewRestriction):
            self.view_restrictions.append(other)

        if isinstance(other, MdsolEntryRestriction):
            self.entry_restrictions.append(other)


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

    def __lshift__(self, other):
        raise ValueError('MdsolLabelRef does not accept any child elements')


class MdsolAttribute(ODMElement):
    def __init__(self, namespace, name, value, transaction_type='Insert'):
        self.namespace = namespace
        self.name = name
        self.value = value
        self.transaction_type = transaction_type

    def __lshift__(self, other):
        raise ValueError('MdsolAttribute does not accept any child elements')

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

        self.attributes.append(other)


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

        if isinstance(other, ItemRef):
            self.item_refs.append(other)

        if isinstance(other, MdsolLabelRef):
            self.label_refs.append(other)


class Question(ODMElement):
    def __init__(self):
        self.translations = []

    def __lshift__(self, other):
        """Override << operator"""

        if not isinstance(other, (TranslatedText)):
            raise ValueError('Question cannot accept a {0} as a child element'.format(other.__class__.__name__))

        self.translations.append(other)

    def build(self, builder):
        """Questions can contain translations"""
        builder.start('Question')
        for translation in self.translations:
            translation.build(builder)
        builder.end('Question')


class MeasurementUnitRef(ODMElement):
    def __init__(self, oid, order_number=None):
        self.oid = oid
        self.order_number = order_number

    def __lshift__(self, other):
        """Has no children"""
        raise ValueError("MeasurementUnitRef takes no child elements.")

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

    def __lshift__(self, other):
        """Has no children"""
        raise ValueError("MdsolHeaderText takes no child elements.")


class CodeListRef(ODMElement):
    """CodeListRef: a reference a codelist within an ItemDef"""

    def __init__(self, oid):
        self.oid = oid

    def __lshift__(self, other):
        """Has no children"""
        raise ValueError("CodeListRef takes no child elements.")

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

        if isinstance(other, TranslatedText):
            self.translations.append(other)

        if isinstance(other, MdsolViewRestriction):
            self.view_restrictions.append(other)


class MdsolReviewGroup(ODMElement):
    """Maps to Rave review groups for an Item"""

    def __init__(self, name):
        self.name = name

    def __lshift__(self, other):
        """Has no children"""
        raise ValueError("MdsolReviewGroup takes no child elements.")

    def build(self, builder):
        builder.start('mdsol:ReviewGroup')
        builder.data(self.name)
        builder.end('mdsol:ReviewGroup')


class ItemDef(ODMElement):
    VALID_DATATYPES = [DATATYPE_TEXT, DATATYPE_INTEGER, DATATYPE_FLOAT, DATATYPE_DATE,
                       DATATYPE_DATETIME, DATATYPE_TIME]

    CONTROLTYPE_CHECKBOX = 'CheckBox'
    CONTROLTYPE_TEXT = 'Text'
    CONTROLTYPE_DATETIME = 'DateTime'
    CONTROLTYPE_DROPDOWNLIST = 'DropDownList'
    CONTROLTYPE_SEARCHLIST = 'SearchList'
    CONTROLTYPE_RADIOBUTTON = 'RadioButton'
    CONTROLTYPE_RADIOBUTTON_VERTICAL = 'RadioButton (Vertical)'
    CONTROLTYPE_FILE_UPLOAD = 'File Upload'
    CONTROLTYPE_LONGTEXT = 'LongText'
    CONTROLTYPE_SIGNATURE_PAGE = 'Signature page'
    CONTROLTYPE_SIGNATURE_FOLDER = 'Signature folder'
    CONTROLTYPE_SIGNATURE_SUBJECT = 'Signature subject'

    def __init__(self, oid, name, datatype, length,
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
            raise KeyError('{0} is not a valid datatype!'.format(datatype))

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

    def build(self, builder):
        """Build XML by appending to builder"""

        params = dict(OID=self.oid,
                      Name=self.name,
                      DataType=self.datatype,
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
            params['mdsol:ControlType'] = self.control_type

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

        # ExternalQuestion?,
        # RangeCheck*,
        # Role*, Alias*,
        # mdsol:HelpText?, mdsol:ViewRestriction* or mdsolEntryRestrictions*), (or mdsol:ReviewGroups*), mdsol:Label?)

        if not isinstance(other, (MdsolHelpText, MdsolEntryRestriction, MdsolViewRestriction, Question,
                                  MeasurementUnitRef, CodeListRef, MdsolHeaderText, MdsolReviewGroup)):
            raise ValueError('MetaDataVersion cannot accept a {0} as a child element'.format(other.__class__.__name__))

        if isinstance(other, Question):
            if self.question is not None:
                raise ValueError('ItemDef already contains a Question')
            self.question = other

        if isinstance(other, CodeListRef):
            if self.codelistref is not None:
                raise ValueError('ItemDef already contains a CodeListRef')
            self.codelistref = other

        if isinstance(other, MeasurementUnitRef):
            self.measurement_unit_refs.append(other)

        if isinstance(other, MdsolHeaderText):
            if self.header_text is not None:
                raise ValueError('ItemDef already contains an mdsol:HeaderText element')
            self.header_text = other

        if isinstance(other, MdsolHelpText):
            self.help_texts.append(other)

        if isinstance(other, MdsolViewRestriction):
            self.view_restrictions.append(other)

        if isinstance(other, MdsolEntryRestriction):
            self.entry_restrictions.append(other)

        if isinstance(other, MdsolReviewGroup):
            self.review_groups.append(other)


class Decode(ODMElement):
    def __init__(self):
        self.translations = []

    def build(self, builder):
        builder.start("Decode")
        for translation in self.translations:
            translation.build(builder)
        builder.end("Decode")

    def __lshift__(self, other):
        """Override << operator"""
        if not isinstance(other, TranslatedText):
            raise ValueError('Decode cannot accept child of type {0}'.format(other.__class__.__name__))
        self.translations.append(other)


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
        self.decode = other


class CodeList(ODMElement):
    """A container for CodeListItems equivalent of Rave Dictionary"""
    VALID_DATATYPES = [DATATYPE_INTEGER, DATATYPE_TEXT, DATATYPE_FLOAT, DATATYPE_STRING]

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
                      DataType=self.datatype)
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
        self.codelist_items.append(other)


class MetaDataVersion(ODMElement):
    """MetaDataVersion, child of study"""

    def __init__(self, oid, name, description=None,
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
        self.protocol = None
        self.codelists = []
        self.item_defs = []
        self.label_defs = []
        self.item_group_defs = []
        self.form_defs = []
        self.study_event_defs = []

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
        for labeldef in self.label_defs:
            labeldef.build(builder)

        builder.end("MetaDataVersion")

    def __lshift__(self, other):
        """Override << operator"""

        if not isinstance(other, (Protocol, StudyEventDef, FormDef, ItemGroupDef, ItemDef, MdsolLabelDef, CodeList)):
            raise ValueError('MetaDataVersion cannot accept a {0} as a child element'.format(other.__class__.__name__))

        if isinstance(other, Protocol):
            self.protocol = other

        if isinstance(other, StudyEventDef):
            self.study_event_defs.append(other)

        if isinstance(other, FormDef):
            self.form_defs.append(other)

        if isinstance(other, ItemGroupDef):
            self.item_group_defs.append(other)

        if isinstance(other, MdsolLabelDef):
            self.label_defs.append(other)

        if isinstance(other, ItemDef):
            self.item_defs.append(other)

        if isinstance(other, CodeList):
            self.codelists.append(other)


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

        if isinstance(other, GlobalVariables):
            if self.global_variables is not None:
                raise ValueError('GlobalVariables is already set.')
            self.global_variables = other

        if isinstance(other, BasicDefinitions):
            if self.basic_definitions is not None:
                raise ValueError('BasicDefinitions is already set.')
            self.basic_definitions = other

        if isinstance(other, MetaDataVersion):
            if self.metadata_version is not None:
                raise ValueError('A MetaDataVersion is already set and Rave only allows one.')
            self.metadata_version = other

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
