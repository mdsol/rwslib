# -*- coding: utf-8 -*-
import datetime

from rwslib.builders.constants import LocationType, UserType

__author__ = 'glow'

import unittest
from rwslib.tests.common import obj_to_doc
from rwslib.builders.admindata import AdminData, User, FirstName, LastName, Location, DisplayName, MetaDataVersionRef


class TestAdminData(unittest.TestCase):

    def test_create_admin_data(self):
        """Create an AdminData"""
        admin_data = AdminData("Mediflex(Prod)")
        tested = obj_to_doc(admin_data)
        self.assertEqual('Mediflex(Prod)', tested.get('StudyOID'))

    def test_create_admin_data_add_users(self):
        """Create an AdminData and add a User"""
        admin_data = AdminData("Mediflex(Prod)")
        user = User("harold")
        user << FirstName("Harold")
        user << LastName("Kumar")
        admin_data << user
        tested = obj_to_doc(admin_data)
        self.assertEqual('Mediflex(Prod)', tested.get('StudyOID'))
        self.assertEqual('harold', list(tested)[0].get('OID'))
        self.assertEqual('FirstName', list(list(tested)[0])[0].tag)
        self.assertEqual('Harold', list(list(tested)[0])[0].text)

    def test_create_admin_data_add_location(self):
        """Create an AdminData and add a Location"""
        admin_data = AdminData("Mediflex(Prod)")
        location = Location("site1", "Site 1")
        admin_data << location
        tested = obj_to_doc(admin_data)
        self.assertEqual('Mediflex(Prod)', tested.get('StudyOID'))
        self.assertEqual('site1', list(tested)[0].get('OID'))
        self.assertEqual('Site 1', list(tested)[0].get('Name'))

    def test_create_admin_data_and_add_nonsense(self):
        """We can't add what we shouldn't"""
        admin_data = AdminData("Mediflex(Prod)")
        with self.assertRaises(ValueError) as exc:
            admin_data << DisplayName("Happy")
        self.assertEqual("AdminData cannot accept a DisplayName as a child element", str(exc.exception))


class TestLocation(unittest.TestCase):

    def test_create_location(self):
        """Create a Location"""
        obj = Location("Site1", "Site One")
        tested = obj_to_doc(obj)
        self.assertEqual("Location", tested.tag)
        self.assertEqual("Site1", tested.get('OID'))
        self.assertEqual("Site One", tested.get('Name'))

    def test_create_location_of_type(self):
        """Create a Location with typ"""
        obj = Location("Site1", "Site One", location_type=LocationType.Site)
        tested = obj_to_doc(obj)
        self.assertEqual("Location", tested.tag)
        # this is an enum
        self.assertEqual("Site", tested.get('LocationType'))

    def test_create_location_with_metadata_version_refs(self):
        """Create a Location with mutiple MetaDataVersionRef"""
        mdv1 = MetaDataVersionRef(study_oid="Mediflex(Prod)",
                                  metadata_version_oid="1234",
                                  effective_date=datetime.datetime(2017, 1, 1))
        mdv2 = MetaDataVersionRef(study_oid="Mediflex(Prod)",
                                  metadata_version_oid="1235",
                                  effective_date=datetime.datetime(2017, 2, 1))
        obj = Location("Site1",
                       "Site One",
                       location_type=LocationType.Site,
                       metadata_versions=(mdv1, mdv2))
        tested = obj_to_doc(obj)
        self.assertEqual("Location", tested.tag)
        # this is an enum
        self.assertEqual("Site", tested.get('LocationType'))
        self.assertEqual(2, len(tested))

    def test_create_location_with_metadata_version_ref(self):
        """Create a Location with single MetaDataVersionRef"""
        mdv1 = MetaDataVersionRef(study_oid="Mediflex(Prod)",
                                  metadata_version_oid="1234",
                                  effective_date=datetime.datetime(2017, 1, 1))
        mdv2 = MetaDataVersionRef(study_oid="Mediflex(Prod)",
                                  metadata_version_oid="1235",
                                  effective_date=datetime.datetime(2017, 2, 1))
        obj = Location("Site1",
                       "Site One",
                       location_type=LocationType.Site,
                       metadata_versions=mdv1)
        tested = obj_to_doc(obj)
        self.assertEqual("Location", tested.tag)
        # this is an enum
        self.assertEqual("Site", tested.get('LocationType'))
        self.assertEqual(1, len(tested))


class TestUser(unittest.TestCase):

    def test_create_user(self):
        """Create a User"""
        obj = User("user1", user_type=UserType.Investigator)
        tested = obj_to_doc(obj)
        self.assertEqual("User", tested.tag)
        self.assertEqual("user1", tested.get('OID'))
        self.assertEqual("Investigator", tested.get('UserType'))

    def test_create_user_with_display_nae(self):
        """Create a Location"""
        obj = User("user1", user_type=UserType.Investigator)
        obj << DisplayName("Henrik")
        tested = obj_to_doc(obj)
        self.assertEqual("User", tested.tag)
        self.assertEqual("user1", tested.get('OID'))
        self.assertEqual("Investigator", tested.get('UserType'))
        self.assertEqual("DisplayName", list(tested)[0].tag)
        self.assertEqual("Henrik", list(tested)[0].text)

class TestMetaDataVersionRef(unittest.TestCase):

    def test_create_a_version_ref(self):
        """We create a MetaDataVersionRef"""
        obj = MetaDataVersionRef("Mediflex(Prod)", "1024", datetime.datetime.utcnow())
        tested = obj_to_doc(obj)
        self.assertEqual("MetaDataVersionRef", tested.tag)
        self.assertEqual("Mediflex(Prod)", tested.get('StudyOID'))
        self.assertEqual("1024", tested.get('MetaDataVersionOID'))
        self.assertTrue(tested.get('EffectiveDate').startswith(datetime.date.today().isoformat()))

    def test_create_a_version_ref_and_attach_to_location(self):
        """We create a MetaDataVersionRef"""
        this = MetaDataVersionRef("Mediflex(Prod)", "1024", datetime.datetime.utcnow() - datetime.timedelta(days=7))
        that = MetaDataVersionRef("Mediflex(Prod)", "1025", datetime.datetime.utcnow())
        obj = Location('Site01', 'Site 1')
        obj << this
        obj <<  that
        tested = obj_to_doc(obj)
        self.assertEqual("Location", tested.tag)
        self.assertTrue(len(list(tested)) == 2)
        _this = list(tested)[0]
        self.assertEqual("Mediflex(Prod)", _this.get('StudyOID'))
        self.assertEqual("1024", _this.get('MetaDataVersionOID'))
        self.assertTrue(_this.get('EffectiveDate').startswith((datetime.date.today() -
                                                               datetime.timedelta(days=7)).isoformat()))
        _that = list(tested)[1]
        self.assertEqual("Mediflex(Prod)", _that.get('StudyOID'))
        self.assertEqual("1025", _that.get('MetaDataVersionOID'))
        self.assertTrue(_that.get('EffectiveDate').startswith(datetime.date.today().isoformat()))
