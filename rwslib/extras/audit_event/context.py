# -*- coding: utf-8 -*-
__author__ = 'isparks'

"""Holds all context classes used by the parser"""


class ContextBase(object):
    """Base class"""

    def __repr__(self):
        vals = dict((k, v) for k, v in self.__dict__.items() if v is not None)
        return "{0}({1})".format(self.__class__.__name__, str(vals))


class Context(ContextBase):
    """A context class that holds the data for every reportable element in the ODM response"""

    def __init__(self, study_oid, subcategory, metadata_version):
        self.study_oid = study_oid
        self.subcategory = subcategory
        self.metadata_version = metadata_version
        self.subject = None
        self.event = None
        self.form = None
        self.itemgroup = None
        self.item = None
        self.audit_record = AuditRecord()
        self.query = None
        self.protocol_deviation = None
        self.comment = None
        self.review = None
        self.signature = Signature()


class AuditRecord(ContextBase):
    def __init__(self):
        self.user_oid = None
        self.location_oid = None
        self.datetimestamp = None
        self.reason_for_change = None
        self.source_id = -1


class Signature(ContextBase):
    def __init__(self):
        self.oid = None
        self.user_oid = None
        self.location_oid = None
        self.datetimestamp = None


class Subject(ContextBase):
    def __init__(self, key, name, status, transaction_type):
        self.key = key
        self.name = name
        self.status = status
        self.transaction_type = transaction_type


class ContextContainer(ContextBase):
    """Base classes for ODM containers that have an oid and repeat key"""

    def __init__(self, oid, repeat_key, transaction_type):
        self.oid = oid
        self.repeat_key = repeat_key
        self.transaction_type = transaction_type


class Event(ContextContainer):
    def __init__(self, oid, repeat_key, transaction_type, instance_name, instance_overdue, instance_id):
        ContextContainer.__init__(self, oid, repeat_key, transaction_type)
        self.instance_name = instance_name
        self.instance_overdue = instance_overdue
        self.instance_id = instance_id


class Form(ContextContainer):
    def __init__(self, oid, repeat_key, transaction_type, datapage_name, datapage_id):
        ContextContainer.__init__(self, oid, repeat_key, transaction_type)
        self.datapage_name = datapage_name
        self.datapage_id = datapage_id


class ItemGroup(ContextContainer):
    def __init__(self, oid, repeat_key, transaction_type, record_id):
        ContextContainer.__init__(self, oid, repeat_key, transaction_type)
        self.record_id = record_id


class Item(ContextBase):
    def __init__(self, oid, value, freeze, verify, lock, transaction_type):
        self.oid = oid
        self.value = value
        self.freeze = freeze
        self.verify = verify
        self.lock = lock
        self.transaction_type = transaction_type


class Query(ContextBase):
    """Query related attributes"""

    def __init__(self, repeat_key, status, response, recipient, value):
        self.repeat_key = repeat_key
        self.status = status
        self.response = response
        self.recipient = recipient
        self.value = value


class Review(ContextBase):
    """Review related attributes"""

    def __init__(self, group_name, reviewed):
        self.group_name = group_name
        self.reviewed = reviewed


class Comment(ContextBase):
    """Review related attributes"""

    def __init__(self, repeat_key, value, transaction_type):
        self.repeat_key = int(repeat_key) if repeat_key else repeat_key
        self.value = value
        self.transaction_type = transaction_type


class ProtocolDeviation(ContextBase):
    """Protocol Deviation related attributes"""

    def __init__(self, repeat_key, code, klass, status, value, transaction_type):
        self.repeat_key = repeat_key
        self.code = code
        self.klass = klass
        self.status = status
        self.value = value
        self.transaction_type = transaction_type
