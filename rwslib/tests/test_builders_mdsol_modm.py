# -*- coding: utf-8 -*-
import random
import uuid
from unittest import TestCase

from faker import Faker

from rwslib.builders.admindata import Location

from rwslib.builders.constants import QueryStatusType
from rwslib.builders.clinicaldata import ClinicalData, FormData, ItemData, ItemGroupData, MdsolQuery, StudyEventData, \
    SubjectData
from rwslib.tests.common import obj_to_doc

import datetime
import unittest

# create a Faker
fake = Faker()

YesNoRave = ('Yes', 'No')


class TestMdsolQuery(unittest.TestCase):
    """Test extension MdsolQuery"""

    def get_tested(self):
        return MdsolQuery(status=QueryStatusType.Open, value="Data missing", query_repeat_key=123,
                          recipient="Site from System", requires_response=True)

    def test_basic(self):
        tested = self.get_tested()
        self.assertEqual("Data missing", tested.value)
        self.assertEqual(123, tested.query_repeat_key)
        self.assertEqual(QueryStatusType.Open, tested.status)
        self.assertEqual("Site from System", tested.recipient)
        self.assertEqual(True, tested.requires_response)

    def test_builder(self):
        tested = self.get_tested()
        tested.response = "Done"
        doc = obj_to_doc(tested)
        self.assertEqual("mdsol:Query", doc.tag)
        self.assertEqual("Yes", doc.attrib['RequiresResponse'])
        self.assertEqual("Site from System", doc.attrib['Recipient'])
        self.assertEqual("123", doc.attrib['QueryRepeatKey'])
        self.assertEqual("Data missing", doc.attrib['Value'])
        self.assertEqual("Done", doc.attrib['Response'])

    def test_invalid_status_value(self):
        """Status must come from QueryStatusType"""
        with self.assertRaises(AttributeError):
            MdsolQuery(status='A test')


class TestMODMClinicalData(TestCase):
    def test_add_last_update_time(self):
        """We add a LastUpdateTime"""
        clindata = ClinicalData("Mediflex", "Prod", metadata_version_oid="1012")
        now = datetime.datetime.utcnow()
        clindata.last_update_time = now
        tested = obj_to_doc(clindata)
        self.assertEqual(now.isoformat(), tested.get('mdsol:LastUpdateTime'))

    def test_add_audit_subcategory(self):
        """We add a LastUpdateTime"""
        clindata = ClinicalData("Mediflex", "Prod", metadata_version_oid="1012")
        clindata.add_attribute('AuditSubCategoryName', "EnteredWithChangeCode")
        tested = obj_to_doc(clindata)
        self.assertEqual("EnteredWithChangeCode", tested.get('mdsol:AuditSubCategoryName'))

    def test_last_update_time_naiive(self):
        """We don't see a LastUpdateTime for naive elements"""
        clindata = ClinicalData("Mediflex", "Prod", metadata_version_oid="1012")
        tested = obj_to_doc(clindata)
        self.assertIsNone(tested.get('mdsol:LastUpdateTime'))

    def test_modm_attributes(self):
        """Each modm attribute is settable"""
        for attribute in ["ExternalStudyID", "StudyUUID", "AuditSubCategoryName",
                          "StudyName", "ClientDivisionUUID", "ClientDivisionSchemeUUID",
                          "SDRCompleteDate", "SDVCompleteDate", "LockCompleteDate",
                          "IsSDVRequired", "IsSDVComplete"]:
            data = ClinicalData("Mediflex", "Prod", metadata_version_oid="1012")
            if "UUID" in attribute:
                data.add_attribute(attribute, uuid.uuid4())
            elif "Date" in attribute:
                data.add_attribute(attribute, fake.date_time_this_year(before_now=True,
                                                                       after_now=False,
                                                                       tzinfo=None))
            elif attribute.startswith('Is'):
                data.add_attribute(attribute, random.choice(YesNoRave))
            else:
                data.add_attribute(attribute, "Blargle")
            tested = obj_to_doc(data)
            self.assertIsNotNone(tested.get("mdsol:{}".format(attribute)))


class TestMODMSubjectData(TestCase):
    def test_add_last_update_time(self):
        """We add a LastUpdateTime"""
        obj = SubjectData("Subject 1", "Site 1")
        now = datetime.datetime.utcnow()
        obj.last_update_time = now
        tested = obj_to_doc(obj)
        self.assertEqual(now.isoformat(), tested.get('mdsol:LastUpdateTime'))

    def test_last_update_time_naiive(self):
        """We don't see a LastUpdateTime for naiive elements"""
        obj = SubjectData("Subject 1", "Site 1")
        tested = obj_to_doc(obj)
        self.assertIsNone(tested.get('mdsol:LastUpdateTime'))

    def test_add_milestone(self):
        """We add a Milestone"""
        obj = SubjectData("Subject 1", "Site 1")
        obj.add_milestone("Randomised")
        tested = obj_to_doc(obj)
        self.assertEqual('Annotation', list(tested)[1].tag)
        self.assertEqual('Randomised', list(list(list(tested)[1])[0])[0].text)

    def test_modm_attributes(self):
        """Each modm attribute is settable"""
        for attribute in ["SubjectName", "Status",
                          "SDRCompleteDate", "SDVCompleteDate", "LockCompleteDate",
                          "IsSDVRequired", "IsSDVComplete", "SubjectUUID"]:
            data = SubjectData("Subject 1", "Site 1")
            if "UUID" in attribute:
                data.add_attribute(attribute, uuid.uuid4())
            elif "Date" in attribute:
                data.add_attribute(attribute, fake.date_time_this_year(before_now=True,
                                                                       after_now=False,
                                                                       tzinfo=None))
            elif attribute.startswith('Is'):
                data.add_attribute(attribute, random.choice(YesNoRave))
            else:
                data.add_attribute(attribute, "Blargle")
            tested = obj_to_doc(data)
            self.assertIsNotNone(tested.get("mdsol:{}".format(attribute)))

    def test_invalid_modm_attributes(self):
        """Each invalid modm attribute raises an exception"""
        for attribute in ["StudyUUID"]:
            obj = SubjectData("Subject 1", "Site 1")
            with self.assertRaises(ValueError) as exc:
                if "UUID" in attribute:
                    obj.add_attribute(attribute, uuid.uuid4())
                elif "Date" in attribute:
                    obj.add_attribute(attribute, fake.date_time_this_year(before_now=True,
                                                                          after_now=False,
                                                                          tzinfo=None))
                else:
                    obj.add_attribute(attribute, "Blargle")
            self.assertEqual("Can't add {} to SubjectData".format(attribute), str(exc.exception))


class TestMODMStudyEventData(TestCase):
    def test_add_last_update_time(self):
        """We add a LastUpdateTime"""
        obj = StudyEventData("VISIT1")
        now = datetime.datetime.utcnow()
        obj.last_update_time = now
        tested = obj_to_doc(obj)
        self.assertEqual("StudyEventData", tested.tag)
        self.assertEqual(now.isoformat(), tested.get('mdsol:LastUpdateTime'))

    def test_last_update_time_naiive(self):
        """We don't see a LastUpdateTime for naiive elements"""
        obj = StudyEventData("VISIT1")
        tested = obj_to_doc(obj)
        self.assertEqual("StudyEventData", tested.tag)
        self.assertIsNone(tested.get('mdsol:LastUpdateTime'))

    def test_add_milestone(self):
        """We add a single milestone"""
        obj = StudyEventData("VISIT1")
        obj.add_milestone("Informed Consent")
        tested = obj_to_doc(obj)
        self.assertEqual('Annotation', list(tested)[0].tag)
        annotation = list(tested)[0]
        self.assertEqual('Informed Consent', list(list(annotation)[0])[0].text)

    def test_add_milestones(self):
        """We add multiple milestones"""
        obj = StudyEventData("VISIT1")
        obj.add_milestone("Informed Consent")
        obj.add_milestone("Study Start")
        tested = obj_to_doc(obj)
        self.assertEqual('Annotation', list(tested)[0].tag)
        annotation = list(tested)[0]
        self.assertEqual('Informed Consent', list(list(annotation)[0])[0].text)
        self.assertEqual('Study Start', list(list(annotation)[1])[0].text)

    def test_modm_attributes(self):
        """Each modm attribute is settable"""
        for attribute in ["StartWindowDate", "EndWindowDate", "StudyEventUUID",
                          "InstanceName", "VisitTargetDate", "InstanceId",
                          "InstanceOverDue", "InstanceStartWindow", "InstanceEndWindow",
                          "InstanceClose", "InstanceAccess", "StudyEventDate",
                          "SDRCompleteDate", "SDVCompleteDate", "LockCompleteDate",
                          "VisitFirstDataEntryDate", "IsSDVComplete", "IsSDVRequired"]:
            data = StudyEventData("VISIT1")
            if "UUID" in attribute:
                data.add_attribute(attribute, uuid.uuid4())
            elif "Date" in attribute:
                data.add_attribute(attribute, fake.date_time_this_year(before_now=True,
                                                                       after_now=False,
                                                                       tzinfo=None))
            elif attribute.startswith('Is'):
                data.add_attribute(attribute, random.choice(YesNoRave))
            else:
                data.add_attribute(attribute, "Blargle")
            tested = obj_to_doc(data)
            self.assertIsNotNone(tested.get("mdsol:{}".format(attribute)))

    def test_invalid_modm_attributes(self):
        """Each invalid modm attribute raises an exception"""
        for attribute in ["StudyUUID"]:
            obj = StudyEventData("VISIT1")
            with self.assertRaises(ValueError) as exc:
                if "UUID" in attribute:
                    obj.add_attribute(attribute, uuid.uuid4())
                elif "Date" in attribute:
                    obj.add_attribute(attribute, fake.date_time_this_year(before_now=True,
                                                                          after_now=False,
                                                                          tzinfo=None))
                else:
                    obj.add_attribute(attribute, "Blargle")
            self.assertEqual("Can't add {} to StudyEventData".format(attribute), str(exc.exception))


class TestMODMFormData(TestCase):
    def test_add_last_update_time(self):
        """We add a LastUpdateTime"""
        obj = FormData(formoid="DM")
        now = datetime.datetime.utcnow()
        obj.last_update_time = now
        tested = obj_to_doc(obj)
        self.assertEqual("FormData", tested.tag)
        self.assertEqual(now.isoformat(), tested.get('mdsol:LastUpdateTime'))

    def test_last_update_time_naiive(self):
        """We don't see a LastUpdateTime for naiive elements"""
        obj = FormData(formoid="DM")
        tested = obj_to_doc(obj)
        self.assertEqual("FormData", tested.tag)
        self.assertIsNone(tested.get('mdsol:LastUpdateTime'))

    def test_add_milestone(self):
        """We add a single milestone"""
        obj = FormData(formoid="DM")
        obj.add_milestone("Informed Consent")
        tested = obj_to_doc(obj)
        self.assertEqual('Annotation', list(tested)[0].tag)
        annotation = list(tested)[0]
        self.assertEqual('Informed Consent', list(list(annotation)[0])[0].text)

    def test_add_milestones(self):
        """We add multiple milestones"""
        obj = FormData(formoid="DM")
        obj.add_milestone("Informed Consent")
        obj.add_milestone("Study Start")
        tested = obj_to_doc(obj)
        self.assertEqual('Annotation', list(tested)[0].tag)
        annotation = list(tested)[0]
        self.assertEqual('Informed Consent', list(list(annotation)[0])[0].text)
        self.assertEqual('Study Start', list(list(annotation)[1])[0].text)

    def test_modm_attributes(self):
        """Each modm attribute is settable"""
        for attribute in ["FormUUID", "DataPageName", "DataPageID",
                          "SDRCompleteDate", "SDVCompleteDate", "LockCompleteDate", "IsSDVRequired",
                          "IsSDVComplete"]:
            data = FormData(formoid="DM")
            if "UUID" in attribute:
                data.add_attribute(attribute, uuid.uuid4())
            elif "Date" in attribute:
                data.add_attribute(attribute, fake.date_time_this_year(before_now=True,
                                                                       after_now=False,
                                                                       tzinfo=None))
            elif attribute.startswith('Is'):
                data.add_attribute(attribute, random.choice(YesNoRave))
            else:
                data.add_attribute(attribute, "Blargle")
            tested = obj_to_doc(data)
            self.assertIsNotNone(tested.get("mdsol:{}".format(attribute)))

    def test_invalid_modm_attributes(self):
        """Each invalid modm attribute raises an exception"""
        for attribute in ["StudyUUID"]:
            obj = FormData(formoid="DM")
            with self.assertRaises(ValueError) as exc:
                if "UUID" in attribute:
                    obj.add_attribute(attribute, uuid.uuid4())
                elif "Date" in attribute:
                    obj.add_attribute(attribute, fake.date_time_this_year(before_now=True,
                                                                          after_now=False,
                                                                          tzinfo=None))
                else:
                    obj.add_attribute(attribute, "Blargle")
            self.assertEqual("Can't add {} to FormData".format(attribute), str(exc.exception))


class TestMODMItemGroupData(TestCase):
    def test_add_last_update_time(self):
        """We add a LastUpdateTime"""
        obj = ItemGroupData(itemgroupoid="DM")
        now = datetime.datetime.utcnow()
        obj.last_update_time = now
        tested = obj_to_doc(obj)
        self.assertEqual("ItemGroupData", tested.tag)
        self.assertEqual(now.isoformat(), tested.get('mdsol:LastUpdateTime'))

    def test_last_update_time_naiive(self):
        """We don't see a LastUpdateTime for naiive elements"""
        obj = ItemGroupData(itemgroupoid="DM")
        tested = obj_to_doc(obj)
        self.assertEqual("ItemGroupData", tested.tag)
        self.assertIsNone(tested.get('mdsol:LastUpdateTime'))

    def test_add_milestone(self):
        """We add a single milestone"""
        obj = ItemGroupData(itemgroupoid="DM")
        obj.add_milestone("Informed Consent")
        tested = obj_to_doc(obj)
        self.assertEqual('Annotation', list(tested)[0].tag)
        annotation = list(tested)[0]
        self.assertEqual('Informed Consent', list(list(annotation)[0])[0].text)

    def test_add_milestones(self):
        """We add multiple milestones"""
        obj = ItemGroupData(itemgroupoid="DM")
        obj.add_milestone("Informed Consent")
        obj.add_milestone("Study Start")
        tested = obj_to_doc(obj)
        self.assertEqual('Annotation', list(tested)[0].tag)
        annotation = list(tested)[0]
        self.assertEqual('Informed Consent', list(list(annotation)[0])[0].text)
        self.assertEqual('Study Start', list(list(annotation)[1])[0].text)

    def test_modm_attributes(self):
        """Each modm attribute is settable"""
        for attribute in ["ItemGroupUUID", "RecordID",
                          "SDRCompleteDate", "SDVCompleteDate", "LockCompleteDate",
                          "IsSDVRequired", "IsSDVComplete"]:
            data = ItemGroupData(itemgroupoid="DM")
            if "UUID" in attribute:
                data.add_attribute(attribute, uuid.uuid4())
            elif "Date" in attribute:
                data.add_attribute(attribute, fake.date_time_this_year(before_now=True,
                                                                       after_now=False,
                                                                       tzinfo=None))
            elif attribute.startswith('Is'):
                data.add_attribute(attribute, random.choice(YesNoRave))
            else:
                data.add_attribute(attribute, "Blargle")
            tested = obj_to_doc(data)
            self.assertIsNotNone(tested.get("mdsol:{}".format(attribute)))

    def test_invalid_modm_attributes(self):
        """Each invalid modm attribute raises an exception"""
        for attribute in ["StudyUUID"]:
            obj = ItemGroupData(itemgroupoid="DM")
            with self.assertRaises(ValueError) as exc:
                if "UUID" in attribute:
                    obj.add_attribute(attribute, uuid.uuid4())
                elif "Date" in attribute:
                    obj.add_attribute(attribute, fake.date_time_this_year(before_now=True,
                                                                          after_now=False,
                                                                          tzinfo=None))
                else:
                    obj.add_attribute(attribute, "Blargle")
            self.assertEqual("Can't add {} to ItemGroupData".format(attribute), str(exc.exception))


class TestMODMItemData(TestCase):
    def test_add_last_update_time(self):
        """We add a LastUpdateTime"""
        obj = ItemData(itemoid="BRTHDAT", value="12 DEC 1975")
        now = datetime.datetime.utcnow()
        obj.last_update_time = now
        tested = obj_to_doc(obj)
        self.assertEqual("ItemData", tested.tag)
        self.assertEqual(now.isoformat(), tested.get('mdsol:LastUpdateTime'))

    def test_add_last_update_time_with_invalid_time(self):
        """We add a LastUpdateTime with a nonsense value"""
        obj = ItemData(itemoid="BRTHDAT", value="12 DEC 1975")
        now = "2017-04-21"
        with self.assertRaises(ValueError) as exc:
            obj.last_update_time = now

    def test_last_update_time_naiive(self):
        """We don't see a LastUpdateTime for naiive elements"""
        obj = ItemData(itemoid="BRTHDAT", value="12 DEC 1975")
        tested = obj_to_doc(obj)
        self.assertEqual("ItemData", tested.tag)
        self.assertIsNone(tested.get('mdsol:LastUpdateTime'))

    def test_last_update_time_set(self):
        """We don't see a LastUpdateTime for naiive elements"""
        obj = ItemData(itemoid="BRTHDAT", value="12 DEC 1975")
        obj.set_update_time()
        tested = obj_to_doc(obj)
        self.assertEqual("ItemData", tested.tag)
        self.assertIsNotNone(tested.get('mdsol:LastUpdateTime'))

    def test_add_milestone(self):
        """We add a single milestone"""
        obj = ItemData(itemoid="BRTHDAT", value="12 DEC 1975")
        obj.add_milestone("Informed Consent")
        tested = obj_to_doc(obj)
        self.assertEqual('Annotation', list(tested)[0].tag)
        annotation = list(tested)[0]
        self.assertEqual('Informed Consent', list(list(annotation)[0])[0].text)

    def test_add_milestones(self):
        """We add multiple milestones"""
        obj = ItemData(itemoid="BRTHDAT", value="12 DEC 1975")
        obj.add_milestone("Informed Consent")
        obj.add_milestone("Study Start")
        tested = obj_to_doc(obj)
        self.assertEqual('Annotation', list(tested)[0].tag)
        annotation = list(tested)[0]
        self.assertEqual('Informed Consent', list(list(annotation)[0])[0].text)
        self.assertEqual('Study Start', list(list(annotation)[1])[0].text)

    def test_add_item_uuid(self):
        """We add a mdsol:ItemUUID"""
        obj = ItemData(itemoid="BRTHDAT", value="12 DEC 1975")
        now = datetime.datetime.utcnow()
        obj.last_update_time = now
        obj.add_attribute("ItemUUID", "85D4F9F0-9F49-42F3-A8E7-413DE85CC55E")
        tested = obj_to_doc(obj)
        self.assertEqual("ItemData", tested.tag)
        self.assertEqual(now.isoformat(), tested.get('mdsol:LastUpdateTime'))
        self.assertEqual("85D4F9F0-9F49-42F3-A8E7-413DE85CC55E", tested.get('mdsol:ItemUUID'))

    def test_gate_modm_attributes(self):
        """We add a mdsol:Nonsense"""
        obj = ItemData(itemoid="BRTHDAT", value="12 DEC 1975")
        now = datetime.datetime.utcnow()
        obj.last_update_time = now
        with self.assertRaises(ValueError) as exc:
            obj.add_attribute("Nonsense", "85D4F9F0-9F49-42F3-A8E7-413DE85CC55E")
        self.assertEqual("Can't add Nonsense to ItemData", str(exc.exception))

    def test_gate_modm_milestones_global(self):
        """We add a mdsol:Nonsense"""
        igp = ItemGroupData("LOG_LINE")
        brth = ItemData(itemoid="BRTHDAT", value="12 DEC 1975")
        brth.add_milestone("Birth Date")
        igp << brth
        ifc = ItemData(itemoid="DSSTDAT_IFC", value="12 DEC 1975")
        ifc.add_milestone("Informed Consent")
        igp << ifc
        tested = obj_to_doc(igp)
        self.assertEqual('ItemGroupData', tested.tag)
        self.assertEqual('ItemData', list(tested)[0].tag)
        idata_zero = list(tested)[0]
        self.assertEqual('Annotation', list(idata_zero)[0].tag)
        anno = list(idata_zero)[0]
        self.assertEqual(1, len(list(anno)))

    def test_modm_attributes(self):
        """Each modm attribute is settable"""
        for attribute in ["ItemUUID",
                          "SDRCompleteDate", "SDVCompleteDate", "LockCompleteDate",
                          "IsSDVRequired", "IsSDVComplete"]:
            data = ItemData(itemoid="BRTHDAT", value="12 DEC 1975")
            if "UUID" in attribute:
                data.add_attribute(attribute, uuid.uuid4())
            elif "Date" in attribute:
                data.add_attribute(attribute, fake.date_time_this_year(before_now=True,
                                                                       after_now=False,
                                                                       tzinfo=None))
            elif attribute.startswith('Is'):
                data.add_attribute(attribute, random.choice(YesNoRave))
            else:
                data.add_attribute(attribute, "Blargle")
            tested = obj_to_doc(data)
            self.assertIsNotNone(tested.get("mdsol:{}".format(attribute)))

    def test_modm_bool_attribute(self):
        """A boolean gets mapped to Yes or No"""
        data = ItemData(itemoid="BRTHDAT", value="12 DEC 1975")
        data.add_attribute("IsSDVRequired", True)
        data.add_attribute("IsSDVComplete", False)
        tested = obj_to_doc(data)
        self.assertEqual(tested.get("mdsol:IsSDVRequired"), "Yes")
        self.assertEqual(tested.get("mdsol:IsSDVComplete"), "No")

    def test_invalid_modm_attributes(self):
        """Each invalid modm attribute raises an exception"""
        for attribute in ["StudyUUID"]:
            obj = ItemData(itemoid="BRTHDAT", value="12 DEC 1975")
            with self.assertRaises(ValueError) as exc:
                if "UUID" in attribute:
                    obj.add_attribute(attribute, uuid.uuid4())
                elif "Date" in attribute:
                    obj.add_attribute(attribute, fake.date_time_this_year(before_now=True,
                                                                          after_now=False,
                                                                          tzinfo=None))
                else:
                    obj.add_attribute(attribute, "Blargle")
            self.assertEqual("Can't add {} to ItemData".format(attribute), str(exc.exception))


class TestMODMLocation(unittest.TestCase):
    def test_add_a_date(self):
        """We add a date to the open and close"""
        obj = Location("site1", "Site 1")
        obj.add_attribute("SiteStartDate", datetime.date(2015, 12, 27))
        obj.add_attribute("SiteCloseDate", datetime.date(2016, 2, 27))
        tested = obj_to_doc(obj)
        self.assertEqual('Location', tested.tag)
        self.assertEqual("2015-12-27", tested.get('mdsol:SiteStartDate'))
        self.assertEqual("2016-02-27", tested.get('mdsol:SiteCloseDate'))
