# -*- coding: utf-8 -*-
import datetime
import sys

from mock import patch

from rwslib.tests.common import obj_to_doc

__author__ = 'isparks'

import unittest

from rwslib.builders.common import bool_to_yes_no, bool_to_true_false, ODMElement
from rwslib.builders.clinicaldata import UserRef, LocationRef, ClinicalData, SubjectData
from rwslib.builders.metadata import Study
from rwslib.builders.admindata import AdminData
from rwslib.builders.core import ODM
from xml.etree import cElementTree as ET


class TestBoolToTrueFalse(unittest.TestCase):
    def test_true_to_TRUE(self):
        """TRUE returned from true"""
        self.assertEqual('TRUE', bool_to_true_false(True))

    def test_false_to_FALSE(self):
        """FALSE returned from false"""
        self.assertEqual('FALSE', bool_to_true_false(False))


class TestBoolToYesNo(unittest.TestCase):
    def test_true_to_TRUE(self):
        """TRUE returned from true"""
        self.assertEqual('Yes', bool_to_yes_no(True))

    def test_false_to_FALSE(self):
        """FALSE returned from false"""
        self.assertEqual('No', bool_to_yes_no(False))


class TestInheritance(unittest.TestCase):
    """The things we do for 100% coverage."""

    def test_inheritance_warning(self):
        class NewObj(ODMElement):
            """We do not override the __lshift__ method"""
            pass

        with self.assertRaises(ValueError):
            # Exercise __lshift__
            NewObj() << object()


class TestString(unittest.TestCase):
    def test_to_string(self):
        self.assertEqual('<UserRef UserOID="test" />', str(UserRef("test")))


class TestAttributeSetters(unittest.TestCase):
    class TestElem(ODMElement):
        """Test class with a bad __lshift__ implementation"""

        def __init__(self):
            self.user = None
            self.locations = []

        def __lshift__(self, other):
            self.set_single_attribute(other, UserRef, "xxxuser")  # Incorrect spelling of user attribute
            self.set_list_attribute(other, LocationRef, "xxxlocations")  # Incorrect spelling of location attribute

    def test_single_attribute_misspelling(self):
        tested = TestAttributeSetters.TestElem()
        with self.assertRaises(AttributeError):
            tested << UserRef("Fred")

    def test_list_attribute_misspelling(self):
        tested = TestAttributeSetters.TestElem()
        with self.assertRaises(AttributeError):
            tested << LocationRef("Site 22")


class TestODM(unittest.TestCase):

    def test_valid_children(self):
        """We can add Study, AdminData or ClinicalData"""
        obj = ODM("Test User", fileoid="1234", description="Some Great Study")
        obj << Study(oid="Study1")
        obj << AdminData(study_oid="Study1")
        obj << ClinicalData(projectname="Study1", environment="Prod")
        tested = ET.fromstring(str(obj))
        self.assertEqual("{http://www.cdisc.org/ns/odm/v1.3}ODM", tested.tag)
        self.assertEqual("Transactional", tested.get('FileType'))
        self.assertEqual("Some Great Study", tested.get('Description'))
        self.assertEqual(3, len(list(tested)))

    def test_invalid_children(self):
        """We can add Study, AdminData or ClinicalData"""
        obj = ODM("Test User", fileoid="1234")
        with self.assertRaises(ValueError) as exc:
            obj << SubjectData("Site1", "Subject 1")
        self.assertEqual("ODM object can only receive ClinicalData, Study or AdminData object", str(exc.exception))

    def test_valid_granularity(self):
        """We can add Study, AdminData or ClinicalData"""
        with self.assertRaises(ValueError) as exc:
            obj = ODM("Test User", fileoid="1234",
                      description="Some Great Study", granularity="NomNom")
        if (sys.version_info > (3, 0)):
            self.assertEqual("Should be an instance of GranularityType not <class 'str'>", str(exc.exception))
        else:
            self.assertEqual("Should be an instance of GranularityType not <type 'str'>", str(exc.exception))

    def test_source_system(self):
        """We can add a SourceSystem, SourceSystemVersion """
        obj = ODM("Test User", fileoid="1234", source_system="Battlestar", source_system_version="1.04")
        tested = obj_to_doc(obj=obj)
        self.assertEqual("Battlestar", tested.get('SourceSystem'))
        self.assertEqual("1.04", tested.get('SourceSystemVersion'))

    def test_creation_datetime(self):
        """Create multiple ODM and get different datetimes"""
        obj_1 = ODM("Test User", fileoid="1234", source_system="Battlestar", source_system_version="1.04")
        tested_1 = obj_to_doc(obj=obj_1)
        with patch('rwslib.builders.common.datetime') as mock_dt:
            # offset the time to ensure we don't overlap
            mock_dt.utcnow.return_value = datetime.datetime.utcnow() + datetime.timedelta(seconds=61)
            obj_2 = ODM("Test User", fileoid="1235", source_system="Battlestar", source_system_version="1.04")
            tested_2 = obj_to_doc(obj=obj_2)
        self.assertEqual(tested_1.get('Originator'), tested_2.get('Originator'))
        self.assertEqual(tested_1.get('SourceSystem'), tested_2.get('SourceSystem'))
        self.assertNotEqual(tested_1.get('FileOID'), tested_2.get('FileOID'))
        self.assertNotEqual(tested_1.get('CreationDateTime'), tested_2.get('CreationDateTime'))