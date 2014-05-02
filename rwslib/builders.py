__author__ = 'isparks'
"""
builders.py provides convenience classes for building ODM documents for clinical data post messages.
"""


import uuid
from xml.etree import cElementTree as ET
from datetime import datetime

#-----------------------------------------------------------------------------------------------------------------------
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
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

#-----------------------------------------------------------------------------------------------------------------------
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
                raise AttributeError('%s transaction_type element must be one of %s not %s' % (self.__class__.__name__,','.join(self.ALLOWED_TRANSACTION_TYPES), value,))
        self._transaction_type = value


class ItemData(TransactionalElement):
    """Models the ODM ItemData object"""
    ALLOWED_TRANSACTION_TYPES = ['Insert','Update','Upsert','Context','Remove']

    def __init__(self, itemoid, value, specify_value = None, transaction_type = None, lock = None, freeze = None, verify = None):
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

        if self.value in [None,'']:
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

        #Ask children (queries etc not added yet)
        #for item  in self.items.values():
        #   item.build(builder)
        builder.end("ItemData")

class ItemGroupData(TransactionalElement):
    """Models the ODM ItemGroupData object.
       Note no name for the ItemGroupData element is required. This is built automatically by the form.
    """
    ALLOWED_TRANSACTION_TYPES = ['Insert','Update','Upsert','Context']

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
            params["ItemGroupRepeatKey"] = str(self.item_group_repeat_key) #may be @context for transaction type upsert or context

        params["mdsol:Submission"] = "WholeItemGroup" if self.whole_item_group else "SpecifiedItemsOnly"

        builder.start("ItemGroupData", params)

        #Ask children
        for item  in self.items.values():
           item.build(builder)
        builder.end("ItemGroupData")


class FormData(TransactionalElement):
    """Models the ODM FormData object"""
    ALLOWED_TRANSACTION_TYPES = ['Insert','Update']

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

        #Ask children
        for itemgroup in self.itemgroups:
            itemgroup.build(builder, self.formoid)
        builder.end("FormData")


class StudyEventData(TransactionalElement):
    """Models the ODM StudyEventData object"""
    ALLOWED_TRANSACTION_TYPES = ['Insert','Update','Remove','Context']
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

        #Ask children
        for form in self.forms:
            form.build(builder)
        builder.end("StudyEventData")

class SubjectData(TransactionalElement):
    """Models the ODM SubjectData and ODM SiteRef objects"""
    ALLOWED_TRANSACTION_TYPES = ['Insert','Update','Upsert']
    def __init__(self, sitelocationoid, subject_key, subject_key_type="SubjectName", transaction_type="Update"):
        super(self.__class__, self).__init__(transaction_type)
        self.sitelocationoid = sitelocationoid
        self.subject_key = subject_key
        self.subject_key_type = subject_key_type
        self.study_events = [] #Can have collection


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
        params = dict(SubjectKey = self.subject_key)
        params['mdsol:SubjectKeyType'] = self.subject_key_type

        if self.transaction_type is not None:
            params["TransactionType"] = self.transaction_type

        builder.start("SubjectData", params)

        builder.start("SiteRef", {'LocationOID': self.sitelocationoid})
        builder.end("SiteRef")

        #Ask children
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
        params = dict(MetaDataVersionOID = '1',
                      StudyOID = "%s (%s)" % (self.projectname, self.environment,),
                     )

        builder.start("ClinicalData", params)
        #Ask children
        if self.subject_data is not None:
            self.subject_data.build(builder)
        builder.end("ClinicalData")

class ODM(ODMElement):
    """Models the ODM object"""
    def __init__(self, originator, description="", creationdatetime=now_to_iso8601(), fileoid=None ):
        self.originator = originator #Required
        self.description = description
        self.creationdatetime = creationdatetime
        #filetype will always be "Transactional"
        #ODM version will always be 1.3
        #Granularity="SingleSubject"
        #AsOfDateTime always OMITTED (it's optional)
        self.clinical_data = None

        #Create unique fileoid if none given
        if fileoid is None:
            self.fileoid = str(uuid.uuid4())
        else:
            self.fileoid = fileoid

    def __lshift__(self, other):
        """Override << operator"""
        if not isinstance(other, ClinicalData):
            raise ValueError("ODM object can only receive ClinicalData object")
        self.clinical_data = other
        return other

    def getroot(self):
        """Build XML object, return the root"""
        self.builder = ET.TreeBuilder()

        params = dict(ODMVersion = "1.3",
                      FileType= "Transactional",
                      CreationDateTime = self.creationdatetime,
                      Originator = self.originator,
                      FileOID = self.fileoid,
                      xmlns = "http://www.cdisc.org/ns/odm/v1.3",
                      )

        params['xmlns:mdsol'] = "http://www.mdsol.com/ns/odm/metadata"

        if self.description:
            params['Description'] = self.description
        self.builder.start("ODM", params)
        #Ask the children
        if self.clinical_data is not None:
            self.clinical_data.build(self.builder)

        self.builder.end("ODM")
        return self.builder.close()

    def __str__(self):
        doc = self.getroot()
        indent(doc)
        header = '<?xml version="1.0" encoding="utf-8" ?>\n'
        return header + ET.tostring(doc, 'utf-8')
