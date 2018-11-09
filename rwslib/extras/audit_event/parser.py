# -*- coding: utf-8 -*-
import six

__author__ = 'isparks'

from lxml import etree
import datetime
from rwslib.extras.audit_event.context import (Context, Subject, Event,
                                                Form, ItemGroup, Item,
                                                Query, Review, Comment,
                                                ProtocolDeviation)

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


def yes_no_none(value):
    """Convert Yes/No/None to True/False/None"""
    if not value:
        return None

    # Yes = True, anything else false
    return value.lower() == 'yes'


def make_int(value, missing=-1):
    """Convert string value to long, '' to missing"""
    if isinstance(value, six.string_types):
        if not value.strip():
            return missing
    elif value is None:
        return missing
    return int(value)

# Defaults
DEFAULT_TRANSACTION_TYPE = u'Upsert'

# Attributes
A_AUDIT_SUBCATEGORY_NAME = mdsol('AuditSubCategoryName')
A_METADATA_VERSION_OID = 'MetaDataVersionOID'
A_STUDY_OID = 'StudyOID'
A_TRANSACTION_TYPE = 'TransactionType'
A_SUBJECT_NAME = mdsol('SubjectName')
A_SUBJECT_KEY = 'SubjectKey'
A_USER_OID = 'UserOID'
A_LOCATION_OID = 'LocationOID'
A_ITEM_OID = 'ItemOID'
A_VALUE = 'Value'
A_STUDYEVENT_OID = 'StudyEventOID'
A_STUDYEVENT_REPEAT_KEY = 'StudyEventRepeatKey'
A_RECORD_ID = mdsol('RecordId')
A_FORM_OID = 'FormOID'
A_FORM_REPEAT_KEY = 'FormRepeatKey'
A_ITEMGROUP_OID = 'ItemGroupOID'
A_ITEMGROUP_REPEAT_KEY = 'ItemGroupRepeatKey'
A_QUERY_REPEAT_KEY = 'QueryRepeatKey'
A_STATUS = 'Status'
A_RECIPIENT = 'Recipient'
A_RESPONSE = 'Response'
A_FREEZE = mdsol('Freeze')
A_VERIFY = mdsol('Verify')
A_LOCK = mdsol('Lock')
A_SUBJECT_STATUS = mdsol('Status')
A_PROTCOL_DEVIATION_REPEAT_KEY = 'ProtocolDeviationRepeatKey'
A_CLASS = 'Class'  # PV
A_CODE = 'Code'  # PV
A_REVIEWED = 'Reviewed'  # Reviews
A_GROUP_NAME = 'GroupName'
A_COMMENT_REPEAT_KEY = 'CommentRepeatKey'
A_INSTANCE_ID = mdsol('InstanceId')
A_INSTANCE_NAME = mdsol('InstanceName')
A_INSTANCE_OVERDUE = mdsol('InstanceOverdue')
A_DATAPAGE_NAME = mdsol('DataPageName')
A_DATAPAGE_ID = mdsol('DataPageId')
A_SIGNATURE_OID = 'SignatureOID'


# Elements
E_CLINICAL_DATA = odm('ClinicalData')
E_SUBJECT_DATA = odm('SubjectData')
E_USER_REF = odm('UserRef')
E_SOURCE_ID = odm('SourceID')
E_DATE_TIME_STAMP_ = odm('DateTimeStamp')
E_REASON_FOR_CHANGE = odm('ReasonForChange')
E_LOCATION_REF = odm('LocationRef')
E_STUDY_EVENT_DATA = odm('StudyEventData')
E_FORM_DATA = odm('FormData')
E_ITEM_GROUP_DATA = odm('ItemGroupData')
E_ITEM_DATA = odm('ItemData')
E_QUERY = mdsol('Query')
E_PROTOCOL_DEVIATION = mdsol('ProtocolDeviation')
E_REVIEW = mdsol('Review')
E_COMMENT = mdsol('Comment')
E_SIGNATURE = odm('Signature')
E_SIGNATURE_REF = odm('SignatureRef')

# Parser States
STATE_NONE = 0
STATE_SOURCE_ID = 1
STATE_DATETIME = 2
STATE_REASON_FOR_CHANGE = 3

# Signature elements have some of the same elements as Audits. Tells us which we are collecting
AUDIT_REF_STATE = 0
SIGNATURE_REF_STATE = 1


class ODMTargetParser(object):
    """A SAX-style lxml Target parser class"""

    def __init__(self, handler):

        # Handler, object that deals with emitting entries etc
        self.handler = handler

        # Context holds the current set of values we are building up, ready to emit
        self.context = None

        # State controls when we are looking for element text content what attribute to put it in
        self.state = STATE_NONE

        # Count of elements processed
        self.count = 0

        self.ref_state = AUDIT_REF_STATE

    def emit(self):
        """We are finished processing one element. Emit it"""

        self.count += 1

        # event_name = 'on_{0}'.format(self.context.subcategory.lower())
        event_name = self.context.subcategory
        if hasattr(self.handler, event_name):
            getattr(self.handler, event_name)(self.context)
        elif hasattr(self.handler, 'default'):
            self.handler.default(self.context)

    def start(self, tag, attrib):
        """On start of element tag"""
        if tag == E_CLINICAL_DATA:
            self.ref_state = AUDIT_REF_STATE
            self.context = Context(attrib[A_STUDY_OID],
                                   attrib[A_AUDIT_SUBCATEGORY_NAME],
                                   int(attrib[A_METADATA_VERSION_OID]))

        elif tag == E_SUBJECT_DATA:
            self.context.subject = Subject(
                attrib.get(A_SUBJECT_KEY),
                attrib.get(A_SUBJECT_NAME),
                attrib.get(A_SUBJECT_STATUS),
                attrib.get(A_TRANSACTION_TYPE, DEFAULT_TRANSACTION_TYPE),
            )
        elif tag == E_USER_REF:
            # Set the Signature or audit-record value depending on state
            self.get_parent_element().user_oid = attrib.get(A_USER_OID)

        elif tag == E_SOURCE_ID:
            self.state = STATE_SOURCE_ID

        elif tag == E_DATE_TIME_STAMP_:
            self.state = STATE_DATETIME

        elif tag == E_REASON_FOR_CHANGE:
            self.state = STATE_REASON_FOR_CHANGE

        elif tag == E_LOCATION_REF:
            # Set the Signature or audit-record value depending on state
            self.get_parent_element().location_oid = attrib.get(A_LOCATION_OID)

        elif tag == E_STUDY_EVENT_DATA:
            self.context.event = Event(
                attrib.get(A_STUDYEVENT_OID),
                attrib.get(A_STUDYEVENT_REPEAT_KEY),
                attrib.get(A_TRANSACTION_TYPE),
                attrib.get(A_INSTANCE_NAME),
                attrib.get(A_INSTANCE_OVERDUE),
                make_int(attrib.get(A_INSTANCE_ID), -1)
            )

        elif tag == E_FORM_DATA:
            self.context.form = Form(
                attrib.get(A_FORM_OID),
                int(attrib.get(A_FORM_REPEAT_KEY, 0)),
                attrib.get(A_TRANSACTION_TYPE),
                attrib.get(A_DATAPAGE_NAME),
                make_int(attrib.get(A_DATAPAGE_ID, -1)),
            )

        elif tag == E_ITEM_GROUP_DATA:
            self.context.itemgroup = ItemGroup(
                attrib.get(A_ITEMGROUP_OID),
                int(attrib.get(A_ITEMGROUP_REPEAT_KEY, 0)),
                attrib.get(A_TRANSACTION_TYPE),
                make_int(attrib.get(A_RECORD_ID, -1)),
            )

        elif tag == E_ITEM_DATA:
            self.context.item = Item(
                attrib.get(A_ITEM_OID),
                attrib.get(A_VALUE),
                yes_no_none(attrib.get(A_FREEZE)),
                yes_no_none(attrib.get(A_VERIFY)),
                yes_no_none(attrib.get(A_LOCK)),
                attrib.get(A_TRANSACTION_TYPE)
            )

        elif tag == E_QUERY:
            self.context.query = Query(
                make_int(attrib.get(A_QUERY_REPEAT_KEY, -1)),
                attrib.get(A_STATUS),
                attrib.get(A_RESPONSE),
                attrib.get(A_RECIPIENT),
                attrib.get(A_VALUE)  # Optional, depends on status
            )

        elif tag == E_PROTOCOL_DEVIATION:
            self.context.protocol_deviation = ProtocolDeviation(
                make_int(attrib.get(A_PROTCOL_DEVIATION_REPEAT_KEY, -1)),
                attrib.get(A_CODE),
                attrib.get(A_CLASS),
                attrib.get(A_STATUS),
                attrib.get(A_VALUE),
                attrib.get(A_TRANSACTION_TYPE)
            )

        elif tag == E_REVIEW:
            self.context.review = Review(
                attrib.get(A_GROUP_NAME),
                yes_no_none(attrib.get(A_REVIEWED)),
            )
        elif tag == E_COMMENT:
            self.context.comment = Comment(
                attrib.get(A_COMMENT_REPEAT_KEY),
                attrib.get(A_VALUE),
                attrib.get(A_TRANSACTION_TYPE)

            )
        elif tag == E_SIGNATURE:
            self.ref_state = SIGNATURE_REF_STATE

        elif tag == E_SIGNATURE_REF:
            self.context.signature.oid = attrib.get(A_SIGNATURE_OID)

    def end(self, tag):
        """Detect end of element"""
        # Emit the context if we reach the end of the audit section
        if tag == E_CLINICAL_DATA:
            self.emit()

    def get_parent_element(self):
        """Signatures and Audit elements share sub-elements, we need to know which to set attributes on"""
        return {AUDIT_REF_STATE: self.context.audit_record,
                SIGNATURE_REF_STATE: self.context.signature}[self.ref_state]

    def data(self, data):
        """Called for text between tags"""
        if self.state == STATE_SOURCE_ID:
            self.context.audit_record.source_id = int(data)  # Audit ids can be 64 bits
        elif self.state == STATE_DATETIME:
            dt = datetime.datetime.strptime(data, "%Y-%m-%dT%H:%M:%S")
            self.get_parent_element().datetimestamp = dt
        elif self.state == STATE_REASON_FOR_CHANGE:
            self.context.audit_record.reason_for_change = data.strip() or None  # Convert a result of '' to None.
        self.state = STATE_NONE

    def close(self):
        self.context = None
        return self.count


def parse(data, eventer):
    """Parse the XML data, firing events from the eventer"""
    parser = etree.XMLParser(target=ODMTargetParser(eventer))
    return etree.XML(data, parser)  # Returns value of close
