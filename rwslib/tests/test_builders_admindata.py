# -*- coding: utf-8 -*-
from rwslib.builders.constants import LocationType, UserType

__author__ = 'glow'

import unittest
from rwslib.tests.common import obj_to_doc
from rwslib.builders.admindata import AdminData, User, FirstName, LastName, Location, DisplayName


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

