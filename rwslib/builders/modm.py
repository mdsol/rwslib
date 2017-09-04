# -*- coding: utf-8 -*-

__author__ = 'glow'

import datetime
import enum


class MODMExtensionRegistry(enum.Enum):
    """
    A registry of MODM extension Elements
    TODO: Get this from the Schema
    """
    StudyEventDef = ["ArmAssociation"]
    StudyEventRef = ["ArmAssociation"]
    ClinicalData = ["ExternalStudyID", "StudyUUID", "AuditSubCategoryName",
                    "StudyName", "ClientDivisionUUID", "ClientDivisionSchemeUUID",
                    "SDRCompleteDate", "SDVCompleteDate", "LockCompleteDate",
                    "IsSDVRequired", "IsSDVComplete"]
    StudyEventData = ["StartWindowDate", "EndWindowDate", "StudyEventUUID",
                      "InstanceName", "VisitTargetDate", "InstanceId",
                      "InstanceOverDue", "InstanceStartWindow", "InstanceEndWindow",
                      "InstanceClose", "InstanceAccess", "StudyEventDate",
                      "SDRCompleteDate", "SDVCompleteDate", "LockCompleteDate",
                      "VisitFirstDataEntryDate",
                      "IsSDVRequired", "IsSDVComplete"]
    SubjectData = ["SubjectName", "Status",
                   "SDRCompleteDate", "SDVCompleteDate", "LockCompleteDate",
                   "IsSDVRequired", "IsSDVComplete"]
    FormData = ["FormUUID", "DataPageName", "DataPageID",
                "SDRCompleteDate", "SDVCompleteDate", "LockCompleteDate",
                "IsSDVRequired", "IsSDVComplete"]
    ItemGroupData = ["ItemGroupUUID", "RecordID",
                     "SDRCompleteDate", "SDVCompleteDate", "LockCompleteDate",
                     "IsSDVRequired", "IsSDVComplete"]
    ItemData = ["ItemUUID",
                "SDRCompleteDate", "SDVCompleteDate", "LockCompleteDate",
                "IsSDVRequired", "IsSDVComplete"]
    SiteRef = ["SiteStartDate", "SiteCloseDate", "LocationOIDType"]
    Location = ["SiteStartDate", "SiteCloseDate"]


class MODMAttribute(object):
    def __init__(self, attribute, value):
        self.attribute = attribute
        self.raw_value = value

    @property
    def tag(self):
        return "mdsol:{}".format(self.attribute)

    @property
    def value(self):
        if isinstance(self.raw_value, (datetime.datetime, datetime.date)):
            return self.raw_value.isoformat()
        elif isinstance(self.raw_value, (bool,)):
            return 'Yes' if self.raw_value else 'No'
        return self.raw_value


class MODMMixin(object):
    @property
    def attributes(self):
        if not hasattr(self, "_attributes"):
            self._attributes = []
        return self._attributes

    def add_attribute(self, attribute, value):
        class_name = self.__class__.__name__
        if class_name.startswith('ItemData'):
            # ItemData* Elements
            class_name = 'ItemData'
        if attribute not in MODMExtensionRegistry[class_name].value:
            raise ValueError("Can't add {} to {}".format(attribute, self.__class__.__name__))
        self.attributes.append(MODMAttribute(attribute, value))

    def mixin(self):
        pass

    def mixin_params(self, params):
        for attribute in self.attributes:
            params.update({attribute.tag: attribute.value})


class LastUpdateMixin(MODMMixin):
    @property
    def last_update_time(self):
        """
        Last Update Time 
        :return: 
        """
        if not hasattr(self, "_last_update_time"):
            self._last_update_time = None
        return self._last_update_time

    @last_update_time.setter
    def last_update_time(self, value):
        if isinstance(value, (datetime.datetime,)):
            self._last_update_time = value
        else:
            raise ValueError("Expect last_update_time to be a datetime")

    def set_update_time(self, update_time=None):
        """
        Set the Update Time from the local clock (in UTC)
        """
        if update_time and isinstance(update_time, (datetime.datetime,)):
            self.last_update_time = update_time
        else:
            self.last_update_time = datetime.datetime.utcnow()

    def mixin_params(self, params):
        """
        Add the mdsol:LastUpdateTime attribute
        :return: 
        """
        super(LastUpdateMixin, self).mixin_params(params)
        if self.last_update_time is not None:
            params.update({"mdsol:LastUpdateTime": self.last_update_time.isoformat()})
        return {}


class MilestoneMixin(MODMMixin):
    @property
    def milestones(self):
        if not hasattr(self, "_milestones"):
            self._milestones = {}
        return self._milestones

    def add_milestone(self,
                      milestone,
                      codelistoid="MILESTONES"):
        """
        Add a milestone
        :param str milestone: Milestone to add 
        """
        if milestone not in self.milestones.get(codelistoid, []):
            self._milestones.setdefault(codelistoid, []).append(milestone)

    def mixin(self):
        """
        Add the annotations
        :return: 
        """
        if self.milestones:
            from rwslib.builders.clinicaldata import Annotation, Flag, FlagValue
            annotation = Annotation()
            for codelist, milestones in self.milestones.items():
                for milestone in milestones:
                    annotation << Flag() << FlagValue(milestone, codelist_oid=codelist)
            self.annotations.append(annotation)
