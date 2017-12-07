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
                   "IsSDVRequired", "IsSDVComplete", "SubjectUUID"]
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
    """
    A Medidata-ODM specific attribute Mixin for ODM Elements

    .. note:: This is Rave Specific (MODM)
    """
    def __init__(self, attribute, value):
        """
        Define a new MODMAttribute

        :param str attribute: Name of the Attribute
        :type value: Union[datetime, bool, str]
        :param value: Value for the attribute
        """
        self.attribute = attribute
        self.raw_value = value

    @property
    def tag(self):
        """
        The namespaced Attribute Tag

        :rtype: str
        :return: The namespaced attribute
        """
        return "mdsol:{}".format(self.attribute)

    @property
    def value(self):
        """
        Normalise the Attribute value and return
        .. note: `datetime` objects are normalised to ISO datestring, `bool` objects are normalised to Yes or No

        :rtype: str
        :return: The normalised value
        """
        if isinstance(self.raw_value, (datetime.datetime, datetime.date)):
            return self.raw_value.isoformat()
        elif isinstance(self.raw_value, (bool,)):
            return 'Yes' if self.raw_value else 'No'
        return self.raw_value


class MODMMixin(object):
    """
    Mixin to add MODM capabilities to Instance types

    .. note:: This is Rave Specific (MODM)
    """
    @property
    def attributes(self):
        """
        Get the attributes for the object

        :rtype: list(MdsolAttribute)
        :return: list of attributes
        """
        if not hasattr(self, "_attributes"):
            self._attributes = []
        return self._attributes

    def add_attribute(self, attribute, value):
        """
        Add an attribute to the current instance

        :param str attribute: Attribute name
        :type value: Union[datetime,bool,str]
        :param value: Attribute value
        """
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
        """
        Merge in the MdsolAttribute for the passed parameter

        :param dict params: dictionary of object parameters
        """
        if not isinstance(params, (dict,)):
            raise AttributeError("Cannot mixin to object of type {}".format(type(params)))
        for attribute in self.attributes:
            params.update({attribute.tag: attribute.value})


class LastUpdateMixin(MODMMixin):
    """
    Mixin to add MODM capabilities to Instance types

    .. note:: This is Rave Specific (MODM)
    """

    @property
    def last_update_time(self):
        """
        Last Update Time for the object
        """
        if not hasattr(self, "_last_update_time"):
            self._last_update_time = None
        return self._last_update_time

    @last_update_time.setter
    def last_update_time(self, value):
        """
        Setter for the last_update_time attribute

        :param datetime.datetime value: value to set for the element
        """
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


class MilestoneMixin(MODMMixin):
    """
    Add a Subject Milestone to the element, rendered as Annotation/Flag in the output

    .. note:: This is MODM Rave peculiar
    """

    @property
    def milestones(self):
        """
        Get the assigned milestones
        :rtype: dict
        :return: Milestones (can be an empty dict)
        """
        if not hasattr(self, "_milestones"):
            self._milestones = {}
        return self._milestones

    def add_milestone(self,
                      milestone,
                      codelistoid="MILESTONES"):
        """
        Add a milestone
        :param codelistoid: specify the CodeListOID (defaults to MILESTONES)
        :param str milestone: Milestone to add
        """
        if milestone not in self.milestones.get(codelistoid, []):
            self._milestones.setdefault(codelistoid, []).append(milestone)

    def mixin(self):
        """
        Add the annotations to the ODM Element (if defined)
        :return: 
        """
        if self.milestones:
            from rwslib.builders.clinicaldata import Annotation, Flag, FlagValue
            annotation = Annotation()
            for codelist, milestones in self.milestones.items():
                for milestone in milestones:
                    annotation << Flag() << FlagValue(milestone, codelist_oid=codelist)
            self.annotations.append(annotation)
