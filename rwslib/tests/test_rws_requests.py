# -*- coding: utf-8 -*-

__author__ = 'glow'

import unittest
from rwslib.rws_requests import StudySubjectsRequest

class TestStudySubjectsRequest(unittest.TestCase):

    def setUp(self):
        self.project_name = "A Project"
        self.environment = "Dev"

    def test_subj_key_type_is_valid(self):
        """
        Confirm that only valid SubjectKeyTypes are accepted
        """
        with self.assertRaises(ValueError) as err:
            request = StudySubjectsRequest(self.project_name, self.environment, subject_key_type="AnApple")
        self.assertEqual(err.exception.message, "SubjectKeyType AnApple is not a valid value")
        request = StudySubjectsRequest(self.project_name, self.environment, subject_key_type="SubjectName")
        self.assertEqual(self.project_name, request.project_name)

    def test_request_uuid_type(self):
        """
        Confirm we request the UUID Subject Key Type
        """
        request = StudySubjectsRequest(self.project_name, self.environment, subject_key_type="SubjectUUID")
        self.assertTrue("subjectKeyType=SubjectUUID" in request.url_path())

    def test_request_without_type(self):
        """
        Confirm we request the UUID Subject Key Type
        """
        request = StudySubjectsRequest(self.project_name, self.environment)
        self.assertFalse("subjectKeyType" in request.url_path())

    def test_request_with_status(self):
        """
        Confirm we request the status when asked to
        """
        request = StudySubjectsRequest(self.project_name, self.environment, status=True)
        self.assertTrue("status=all" in request.url_path())

    def test_request_with_include(self):
        """
        Confirm we request the status when asked to
        """
        request = StudySubjectsRequest(self.project_name, self.environment, include="inactive")
        self.assertTrue("include=inactive" in request.url_path())
        request = StudySubjectsRequest(self.project_name, self.environment, include="inactiveAndDeleted")
        self.assertTrue("include=inactiveAndDeleted" in request.url_path())
        request = StudySubjectsRequest(self.project_name, self.environment, include="deleted")
        self.assertTrue("include=deleted" in request.url_path())
        with self.assertRaises(ValueError) as err:
            request = StudySubjectsRequest(self.project_name, self.environment, include="kitchen_sink")
        self.assertEqual("If provided, included must be one of inactive,deleted,inactiveAndDeleted",
                         err.exception.message)

if __name__ == '__main__':
    unittest.main()
