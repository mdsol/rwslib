# -*- coding: utf-8 -*-

__author__ = 'glow'

import unittest
from six.moves.urllib_parse import quote
from rwslib.rws_requests.odm_adapter import SignatureDefinitionsRequest, UsersRequest, \
    SitesMetadataRequest, VersionFoldersRequest, AuditRecordsRequest


class TestSignatureDefinitionsRequest(unittest.TestCase):
    def create_request_object(self, project_name):
        t = SignatureDefinitionsRequest(project_name=project_name)
        return t

    def test_sig_def_requests(self):
        """Create a SignatureDefinitionsRequest"""
        project_name = "Mediflex(Prod)"
        t = self.create_request_object(project_name)
        self.assertEqual('datasets/Signatures.odm?studyid=%s' % quote(project_name),
                         t.url_path())


class TestUsersRequest(unittest.TestCase):
    def create_request_object(self,
                              project_name="Mediflex",
                              environment="Dev",
                              location_oid=None):
        t = UsersRequest(project_name=project_name,
                         environment_name=environment,
                         location_oid=location_oid)
        return t

    def test_users_request(self):
        """Create a UsersRequest"""
        t = self.create_request_object()
        self.assertEqual('datasets/Users.odm?studyoid=%s' % quote(t.studyoid),
                         t.url_path())
        t = self.create_request_object(location_oid="1002")
        self.assertTrue('locationoid=%s' % quote("1002") in t.url_path())
        self.assertTrue('studyoid=%s' % quote(t.studyoid) in t.url_path())


class TestSitesMetadataRequest(unittest.TestCase):
    def create_request_object(self,
                              project_name="Mediflex",
                              environment_name="Dev"):
        t = SitesMetadataRequest(project_name=project_name,
                                environment_name=environment_name)
        return t

    def test_create_a_sites_metadata_request(self):
        """Create a SitesMetadataRequest"""
        t = self.create_request_object()
        self.assertEqual('datasets/Sites.odm?studyoid=%s' % quote(t.studyoid),
                         t.url_path())
        t = self.create_request_object(project_name=None,
                                       environment_name=None)
        self.assertEqual('datasets/Sites.odm',
                         t.url_path())

    def test_error_cases(self):
        """Create a SitesMetadataRequest, with error cases"""
        with self.assertRaises(AttributeError) as exc:
            t = self.create_request_object(environment_name=None)
        self.assertEqual("environment_name cannot be empty if project_name is set",
                         str(exc.exception))
        with self.assertRaises(AttributeError) as exc:
            t = self.create_request_object(environment_name='')
        self.assertEqual("environment_name cannot be empty if project_name is set",
                         str(exc.exception))
        with self.assertRaises(AttributeError) as exc:
            t = self.create_request_object(project_name=None)
        self.assertEqual("project_name cannot be empty if environment_name is set",
                         str(exc.exception))
        with self.assertRaises(AttributeError) as exc:
            t = self.create_request_object(project_name='')
        self.assertEqual("project_name cannot be empty if environment_name is set",
                         str(exc.exception))


class TestVersionFoldersRequest(unittest.TestCase):
    def create_request_object(self,
                              project_name="Mediflex",
                              environment_name="Dev"):
        t = VersionFoldersRequest(project_name=project_name,
                                environment_name=environment_name)
        return t

    def test_happy_case(self):
        """we can create a VersionFoldersRequest"""
        t = self.create_request_object()
        self.assertEqual("datasets/VersionFolders.odm?studyoid=%s" % quote(t.studyoid),
                         t.url_path())


class TestAuditRecordsRequest(unittest.TestCase):
    def create_request_object(self,
                              project_name="Mediflex",
                              environment_name="Dev",
                              startid=1,
                              per_page=100):
        t = AuditRecordsRequest(project_name=project_name,
                                environment_name=environment_name,
                                startid=startid,
                                per_page=per_page)
        return t

    def test_create_audit_records_request(self):
        """We can create an AuditRecordsRequest"""
        t = self.create_request_object()
        self.assertTrue('datasets/ClinicalAuditRecords.odm' in t.url_path())
        self.assertTrue('studyoid=%s' % quote(t.studyoid) in t.url_path())
        self.assertTrue('startid=1' in t.url_path())
        self.assertTrue('per_page=100' in t.url_path())
        t = self.create_request_object(startid=2569, per_page=50)
        self.assertTrue('startid=2569' in t.url_path())
        self.assertTrue('per_page=50' in t.url_path())

if __name__ == '__main__':
    unittest.main()
