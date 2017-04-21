# -*- coding: utf-8 -*-

__author__ = 'glow'

import datetime
import enum

class MODMExtensionRegistry(enum.Enum):
    """
    A registry of MODM extension Elements
    """
    StudyEventDef = ["ArmAssociation"]
    StudyEventRef = ["ArmAssociation"]
    ClinicalData = ["ExternalStudyID", "StudyUUID"]
    SubjectData = ["VisitOpenDate", "VisitCloseDate", "StudyEventUUID"]
    FormData = ["FormUUID"]
    ItemGroupData = ["ItemGroupUUID"]
    ItemData = ["ItemUUID"]
    SiteRef = ["SiteStartDate", "SiteCloseDate"]
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
        return self.raw_value


class MODMMixin(object):

    @property
    def attributes(self):
        if not hasattr(self, "_attributes"):
            self._attributes = []
        return self._attributes

    def add_attribute(self, attribute, value):
        if attribute not in MODMExtensionRegistry[self.__class__.__name__].value:
            raise ValueError("Can't add {} to {}".format(attribute, self.__class__.__name__))
        self.attributes.append(MODMAttribute(attribute, value))

    def mixin(self):
        pass

    def mixin_params(self, params):
        for attribute in self.attributes:
            params.update({attribute.tag: attribute.value})


class LastUpdateMixin(MODMMixin):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "last_update_time"):
            if "last_update_time" in kwargs:
                cls.last_update_time = kwargs.get("last_update_time")
            else:
                cls.last_update_time = None
        return super(LastUpdateMixin, cls).__new__(cls)

    def set_update_time(self):
        """
        Set the Update Time from the local clock (in UTC)
        """
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

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "milestones"):
            cls.milestones = {}
        return super(MilestoneMixin, cls).__new__(cls)

    def add_milestone(self, milestone, codelistoid="MILESTONES"):
        """
        Add a milestone
        :param str milestone: Milestone to add 
        """
        if milestone not in self.milestones.get(codelistoid, []):
            self.milestones.setdefault(codelistoid, []).append(milestone)

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
