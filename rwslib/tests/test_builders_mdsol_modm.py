# -*- coding: utf-8 -*-
from unittest import TestCase

from rwslib.builders.admindata import Location

from rwslib.builders.constants import QueryStatusType
from rwslib.builders.clinicaldata import ClinicalData, FormData, ItemData, ItemGroupData, MdsolQuery, StudyEventData, \
    SubjectData
from rwslib.tests.common import obj_to_doc

import datetime
import unittest


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

    def test_last_update_time_naiive(self):
        """We don't see a LastUpdateTime for naiive elements"""
        clindata = ClinicalData("Mediflex", "Prod", metadata_version_oid="1012")
        tested = obj_to_doc(clindata)
        self.assertIsNone(tested.get('mdsol:LastUpdateTime'))


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
