# -*- coding: utf-8 -*-
__author__ = 'anewbigging'

from lxml import etree
from enum import Enum

# Constants
ODM_NS = '{http://www.cdisc.org/ns/odm/v1.3}'
MDSOL_NS = '{http://www.mdsol.com/ns/odm/metadata}'


# Some constant-making helpers
def odm(value):
    """Value prefix with ODM Namespace"""
    return "{0}{1}".format(ODM_NS, value)

def mdsol(value):
    """Value prefix with mdsol Namespace"""
    return "{0}{1}".format(MDSOL_NS, value)


class E_ODM(Enum):
    """
    Defines ODM Elements
    """
    CLINICAL_DATA = odm('ClinicalData')
    SUBJECT_DATA = odm('SubjectData')
    STUDY_EVENT_DATA = odm('StudyEventData')
    FORM_DATA = odm('FormData')
    ITEM_GROUP_DATA = odm('ItemGroupData')
    ITEM_DATA = odm('ItemData')
    METADATA_VERSION = odm('MetaDataVersion')

    USER_REF = odm('UserRef')
    SOURCE_ID = odm('SourceID')
    DATE_TIME_STAMP_ = odm('DateTimeStamp')
    REASON_FOR_CHANGE = odm('ReasonForChange')
    LOCATION_REF = odm('LocationRef')
    QUERY = mdsol('Query')
    PROTOCOL_DEVIATION = mdsol('ProtocolDeviation')
    REVIEW = mdsol('Review')
    COMMENT = mdsol('Comment')
    SIGNATURE = odm('Signature')
    SIGNATURE_REF = odm('SignatureRef')
    SOURCEID = odm('SourceID')

    ITEM_DEF = odm('ItemDef')
    RANGE_CHECK = odm('RangeCheck')
    CODELIST_REF = odm('CodeListRef')
    CODELIST = odm('CodeList')
    CODELIST_ITEM = odm('CodeListItem')
    ENUMERATED_ITEM = odm('EnumeratedItem')


class A_ODM(Enum):
    """
    Defines ODM Attributes
    """
    AUDIT_SUBCATEGORY_NAME = mdsol('AuditSubCategoryName')
    METADATA_VERSION_OID = 'MetaDataVersionOID'
    STUDY_OID = 'StudyOID'
    TRANSACTION_TYPE = 'TransactionType'
    SUBJECT_NAME = mdsol('SubjectName')
    SUBJECT_KEY = 'SubjectKey'
    USER_OID = 'UserOID'
    LOCATION_OID = 'LocationOID'
    ITEM_OID = 'ItemOID'
    VALUE = 'Value'
    STUDYEVENT_OID = 'StudyEventOID'
    STUDYEVENT_REPEAT_KEY = 'StudyEventRepeatKey'
    FORM_OID = 'FormOID'
    FORM_REPEAT_KEY = 'FormRepeatKey'
    ITEMGROUP_OID = 'ItemGroupOID'
    ITEMGROUP_REPEAT_KEY = 'ItemGroupRepeatKey'
    QUERY_REPEAT_KEY = 'QueryRepeatKey'
    STATUS = 'Status'
    RECIPIENT = 'Recipient'
    RESPONSE = 'Response'
    FREEZE = mdsol('Freeze')
    VERIFY = mdsol('Verify')
    LOCK = mdsol('Lock')
    SUBJECT_STATUS = mdsol('Status')
    PROTCOL_DEVIATION_REPEAT_KEY = 'ProtocolDeviationRepeatKey'
    CLASS = 'Class'  # PV
    CODE = 'Code'  # PV
    REVIEWED = 'Reviewed' #Reviews
    GROUP_NAME = 'GroupName'
    COMMENT_REPEAT_KEY = 'CommentRepeatKey'
    INSTANCE_NAME = mdsol('InstanceName')
    INSTANCE_OVERDUE = mdsol('InstanceOverdue')
    DATAPAGE_NAME = mdsol('DataPageName')
    SIGNATURE_OID = 'SignatureOID'

    OID = 'OID'
    DATATYPE = 'DataType'
    LENGTH = 'Length'
    SIGNIFICANT_DIGITS = 'SignficantDigits'
    CODELIST_OID = 'CodeListOID'
    CODED_VALUE = 'CodedValue'
    DATETIME_FORMAT = mdsol('DateTimeFormat')


def xml_pretty_print(str):
    parser = etree.XMLParser(remove_blank_text=True)
    xml = etree.fromstring(str, parser)
    return etree.tostring(xml, pretty_print=True)

