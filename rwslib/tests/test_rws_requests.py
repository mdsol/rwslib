# -*- coding: utf-8 -*-
import datetime

__author__ = 'glow'

import unittest
try:
    import mock
except ImportError:
    from unittest import mock

import requests
from rwslib.rwsobjects import RWSPostResponse, RWSSubjects, RWSSubjectListItem, \
    RWSStudyMetadataVersions, RWSStudies, RWSResponse
from rwslib.rws_requests import StudySubjectsRequest, check_dataset_type, SubjectDatasetRequest, \
    VersionDatasetRequest, StudyDatasetRequest, PostDataRequest, PostMetadataRequest, \
    GlobalLibraryVersionRequest, GlobalLibraryVersionsRequest, GlobalLibraryDraftsRequest, \
    GlobalLibrariesRequest, StudyVersionRequest, StudyVersionsRequest, StudyDraftsRequest, \
    MetadataStudiesRequest, ClinicalStudiesRequest, CacheFlushRequest, DiagnosticsRequest, \
    BuildVersionRequest, ODMDatasetBase


class TestStudySubjectsRequest(unittest.TestCase):
    def setUp(self):
        self.project_name = "A Project"
        self.environment = "Dev"

    def test_subj_key_type_is_valid(self):
        """
        Confirm that only valid SubjectKeyTypes are accepted
        """
        with self.assertRaises(ValueError) as err:
            request = StudySubjectsRequest(self.project_name, self.environment,
                                           subject_key_type="AnApple")
        self.assertEqual(str(err.exception), "SubjectKeyType AnApple is not a valid value")
        request = StudySubjectsRequest(self.project_name, self.environment,
                                       subject_key_type="SubjectName")
        self.assertEqual(self.project_name, request.project_name)

    def test_request_uuid_type(self):
        """
        Confirm we request the UUID Subject Key Type
        """
        request = StudySubjectsRequest(self.project_name, self.environment,
                                       subject_key_type="SubjectUUID")
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
        request = StudySubjectsRequest(self.project_name, self.environment,
                                       include="inactiveAndDeleted")
        self.assertTrue("include=inactiveAndDeleted" in request.url_path())
        request = StudySubjectsRequest(self.project_name, self.environment, include="deleted")
        self.assertTrue("include=deleted" in request.url_path())
        with self.assertRaises(ValueError) as err:
            request = StudySubjectsRequest(self.project_name, self.environment,
                                           include="kitchen_sink")
        self.assertEqual(
            "If provided, included must be one of inactive,deleted,inactiveAndDeleted",
            str(err.exception))

    def test_maps_response(self):
        """We map the response to a RWSSubjects instance"""
        response_content = """    <ODM FileType="Snapshot"
         FileOID="770f1758-db33-4ab2-af72-38db863734aa"
         CreationDateTime="2013-04-08T14:08:06.875-00:00"
         ODMVersion="1.3">

         <ClinicalData StudyOID="Fixitol(Dev)" MetaDataVersionOID="1111">
            <SubjectData SubjectKey="000001">
               <SiteRef LocationOID="BP001"/>
            </SubjectData>
         </ClinicalData>

         <ClinicalData StudyOID="Fixitol(Dev)" MetaDataVersionOID="1111">
             <SubjectData SubjectKey="1111">
                <SiteRef LocationOID="335566"/>
             </SubjectData>
         </ClinicalData>
    </ODM>
"""
        request = StudySubjectsRequest("Fixitol",
                                       "Dev")
        req = mock.Mock(requests.Request, text=response_content)
        response = request.result(req)
        self.assertTrue(isinstance(response, RWSSubjects))
        for subject in response:
            self.assertTrue(isinstance(subject, RWSSubjectListItem))
            self.assertTrue(subject.subject_name in ['000001', "1111"])


class TestCheckDatasetType(unittest.TestCase):
    def test_with_valid_input(self):
        """We match when the input is what we expect it to be"""
        for dataset_type in ['regular', 'raw', 'REGULAR', 'RAW']:
            try:
                check_dataset_type(dataset_type)
            except ValueError:
                self.fail("Dataset {0} should be valid".format(dataset_type))

    def test_with_invalid_input(self):
        """We error with incorrect dataset_type"""
        for dataset_type in ['ruler', 'pencil', 'cheese']:
            with self.assertRaises(ValueError) as exc:
                check_dataset_type(dataset_type)
            self.assertEqual("Dataset type not 'regular' or 'raw' is %s" % dataset_type,
                             str(exc.exception))


class TestSubjectDatasetRequest(unittest.TestCase):
    def create_request_object(self, **kwargs):
        """
        Helper class
        :param args:
        :return: a SubjectDatasetRequest
        """
        default = dict(project_name="Mediflex",
                       environment_name="Prod",
                       subjectkey="1001",
                       dataset_type='regular',
                       start=None,
                       rawsuffix=None,
                       formoid=None,
                       versionitem=None,
                       codelistsuffix=None,
                       decodesuffix=None,
                       stdsuffix=None)
        default.update(kwargs)
        t = SubjectDatasetRequest(**default)
        return t

    def test_default_subjects_path(self):
        """We create a SubjectDatasetRequest with the defaults"""
        t = self.create_request_object()
        self.assertEqual("Mediflex", t.project_name)
        self.assertEqual("Prod", t.environment_name)
        self.assertEqual("studies/Mediflex(Prod)/subjects/1001/datasets/regular", t.url_path())

    def test_raw_subjects_path(self):
        """We create a SubjectDatasetRequest with raw"""
        t = self.create_request_object(dataset_type="raw")
        self.assertEqual("Mediflex", t.project_name)
        self.assertEqual("Prod", t.environment_name)
        self.assertEqual("studies/Mediflex(Prod)/subjects/1001/datasets/raw", t.url_path())

    def test_raw_subjects_path_with_form(self):
        """We create a SubjectDatasetRequest with raw"""
        t = self.create_request_object(dataset_type="raw", formoid="DM")
        self.assertEqual("Mediflex", t.project_name)
        self.assertEqual("Prod", t.environment_name)
        self.assertEqual("studies/Mediflex(Prod)/subjects/1001/datasets/raw/DM", t.url_path())

    def test_banana_subjects_path(self):
        """We create a SubjectDatasetRequest with nonsense"""
        with self.assertRaises(ValueError) as exc:
            t = self.create_request_object(dataset_type="pineapple")
        self.assertEqual("Dataset type not 'regular' or 'raw' is pineapple",
                         str(exc.exception))

    def test_create_start_using_datetime(self):
        """We can pass a datetime instance as the start argument"""
        jan = datetime.datetime(year=2012, month=12, day=1, hour=12, minute=12, second=23)
        t = self.create_request_object(dataset_type="raw", formoid="DM", start=jan)
        self.assertEqual("Mediflex", t.project_name)
        self.assertEqual("Prod", t.environment_name)
        self.assertEqual("studies/Mediflex(Prod)/subjects/1001/datasets/raw/DM?start=2012-12-01T12%3A12%3A23", t.url_path())

    def test_create_start_using_string_datetime(self):
        """We can pass a string (iso8601) instance as the start argument"""
        t = self.create_request_object(dataset_type="raw", formoid="DM", start="2012-12-01T12:12:23")
        self.assertEqual("Mediflex", t.project_name)
        self.assertEqual("Prod", t.environment_name)
        self.assertEqual("studies/Mediflex(Prod)/subjects/1001/datasets/raw/DM?start=2012-12-01T12%3A12%3A23", t.url_path())

    def test_create_start_using_string_date(self):
        """We can pass a string (iso8601) instance as the start argument"""
        t = self.create_request_object(dataset_type="raw", formoid="DM", start="2012-12-01")
        self.assertEqual("Mediflex", t.project_name)
        self.assertEqual("Prod", t.environment_name)
        self.assertEqual("studies/Mediflex(Prod)/subjects/1001/datasets/raw/DM?start=2012-12-01",
                         t.url_path())


class TestVersionDatasetRequest(unittest.TestCase):
    def create_request_object(self, **kwargs):
        """
        Helper class
        :param args:
        :return: a VersionDatasetRequest
        """
        default = dict(project_name="Mediflex",
                       environment_name="Prod",
                       version_oid='1001',
                       dataset_type='regular',
                       start=None,
                       rawsuffix=None,
                       formoid=None,
                       versionitem=None,
                       codelistsuffix=None,
                       decodesuffix=None,
                       stdsuffix=None)
        default.update(kwargs)
        t = VersionDatasetRequest(**default)
        return t

    def test_default_versions_path(self):
        """We create a VersionDatasetRequest with the defaults"""
        t = self.create_request_object()
        self.assertEqual("Mediflex", t.project_name)
        self.assertEqual("Prod", t.environment_name)
        self.assertEqual("studies/Mediflex(Prod)/versions/1001/datasets/regular", t.url_path())

    def test_raw_versions_path(self):
        """We create a VersionDatasetRequest with raw"""
        t = self.create_request_object(dataset_type="raw")
        self.assertEqual("Mediflex", t.project_name)
        self.assertEqual("Prod", t.environment_name)
        self.assertEqual("studies/Mediflex(Prod)/versions/1001/datasets/raw", t.url_path())

    def test_raw_versions_path_with_form(self):
        """We create a SubjectDatasetRequest with raw"""
        t = self.create_request_object(dataset_type="raw", formoid="DM")
        self.assertEqual("Mediflex", t.project_name)
        self.assertEqual("Prod", t.environment_name)
        self.assertEqual("studies/Mediflex(Prod)/versions/1001/datasets/raw/DM", t.url_path())

    def test_banana_versions_path(self):
        """We create a VersionDatasetRequest with nonsense"""
        with self.assertRaises(ValueError) as exc:
            t = self.create_request_object(dataset_type="pineapple")
        self.assertEqual("Dataset type not 'regular' or 'raw' is pineapple",
                        str(exc.exception))

    def test_create_start_using_datetime(self):
        """We can pass a datetime instance as the start argument"""
        jan = datetime.datetime(year=2012, month=12, day=1, hour=12, minute=12, second=23)
        t = self.create_request_object(dataset_type="raw", formoid="DM", start=jan)
        self.assertEqual("Mediflex", t.project_name)
        self.assertEqual("Prod", t.environment_name)
        self.assertEqual("studies/Mediflex(Prod)/versions/1001/datasets/raw/DM?start=2012-12-01T12%3A12%3A23", t.url_path())

    def test_create_start_using_string_datetime(self):
        """We can pass a string (iso8601) instance as the start argument"""
        t = self.create_request_object(dataset_type="raw", formoid="DM", start="2012-12-01T12:12:23")
        self.assertEqual("Mediflex", t.project_name)
        self.assertEqual("Prod", t.environment_name)
        self.assertEqual("studies/Mediflex(Prod)/versions/1001/datasets/raw/DM?start=2012-12-01T12%3A12%3A23", t.url_path())

    def test_create_start_using_string_date(self):
        """We can pass a string (iso8601) instance as the start argument"""
        t = self.create_request_object(dataset_type="raw", formoid="DM", start="2012-12-01")
        self.assertEqual("Mediflex", t.project_name)
        self.assertEqual("Prod", t.environment_name)
        self.assertEqual("studies/Mediflex(Prod)/versions/1001/datasets/raw/DM?start=2012-12-01", t.url_path())


class TestStudyDatasetRequest(unittest.TestCase):
    def create_request_object(self, **kwargs):
        """
        Helper class
        :param args:
        :return: a VersionDatasetRequest
        """
        default = dict(project_name="Mediflex",
                       environment_name="Prod",
                       dataset_type='regular',
                       start=None,
                       rawsuffix=None,
                       formoid=None,
                       versionitem=None,
                       codelistsuffix=None,
                       decodesuffix=None,
                       stdsuffix=None)
        default.update(kwargs)
        t = StudyDatasetRequest(**default)
        return t

    def test_default_versions_path(self):
        """We create a StudyDatasetRequest with the defaults"""
        t = self.create_request_object()
        self.assertEqual("Mediflex", t.project_name)
        self.assertEqual("Prod", t.environment_name)
        self.assertEqual("studies/Mediflex(Prod)/datasets/regular", t.url_path())

    def test_raw_versions_path(self):
        """We create a StudyDatasetRequest with raw"""
        t = self.create_request_object(dataset_type="raw")
        self.assertEqual("Mediflex", t.project_name)
        self.assertEqual("Prod", t.environment_name)
        self.assertEqual("studies/Mediflex(Prod)/datasets/raw", t.url_path())

    def test_raw_versions_path_query_param(self):
        """We create a StudyDatasetRequest with raw and a query param"""
        t = self.create_request_object(dataset_type="raw", rawsuffix="RX")
        self.assertEqual("Mediflex", t.project_name)
        self.assertEqual("Prod", t.environment_name)
        self.assertEqual("studies/Mediflex(Prod)/datasets/raw?rawsuffix=RX", t.url_path())

    def test_raw_versions_path_with_form(self):
        """We create a StudyDatasetRequest with raw"""
        t = self.create_request_object(dataset_type="raw", formoid="DM")
        self.assertEqual("Mediflex", t.project_name)
        self.assertEqual("Prod", t.environment_name)
        self.assertEqual("studies/Mediflex(Prod)/datasets/raw/DM", t.url_path())

    def test_banana_versions_path(self):
        """We create a StudyDatasetRequest with nonsense"""
        with self.assertRaises(ValueError) as exc:
            t = self.create_request_object(dataset_type="pineapple")
        self.assertEqual("Dataset type not 'regular' or 'raw' is pineapple",
                         str(exc.exception))

    def test_create_start_using_datetime(self):
        """We can pass a datetime instance as the start argument"""
        jan = datetime.datetime(year=2012, month=12, day=1, hour=12, minute=12, second=23)
        t = self.create_request_object(dataset_type="raw", formoid="DM", start=jan)
        self.assertEqual("Mediflex", t.project_name)
        self.assertEqual("Prod", t.environment_name)
        self.assertEqual("studies/Mediflex(Prod)/datasets/raw/DM?start=2012-12-01T12%3A12%3A23", t.url_path())

    def test_create_start_using_string_datetime(self):
        """We can pass a string (iso8601) instance as the start argument"""
        t = self.create_request_object(dataset_type="raw", formoid="DM", start="2012-12-01T12:12:23")
        self.assertEqual("Mediflex", t.project_name)
        self.assertEqual("Prod", t.environment_name)
        self.assertEqual("studies/Mediflex(Prod)/datasets/raw/DM?start=2012-12-01T12%3A12%3A23", t.url_path())

    def test_create_start_using_string_date(self):
        """We can pass a string (iso8601) instance as the start argument"""
        t = self.create_request_object(dataset_type="raw", formoid="DM", start="2012-12-01")
        self.assertEqual("Mediflex", t.project_name)
        self.assertEqual("Prod", t.environment_name)
        self.assertEqual("studies/Mediflex(Prod)/datasets/raw/DM?start=2012-12-01", t.url_path())


class TestPostDataRequest(unittest.TestCase):
    def test_post_data_request_response(self):
        """We can POST data and reformat the response"""
        response_content = """    <Response ReferenceNumber="82e942b0-48e8-4cf4-b299-51e2b6a89a1b"
              InboundODMFileOID=""
              IsTransactionSuccessful="1"
              SuccessStatistics="Rave objects touched: Subjects=0; Folders=0; Forms=0; Fields=0; LogLines=0" NewRecords=""
              SubjectNumberInStudy="1103" SubjectNumberInStudySite="55">
        </Response>"""
        t = PostDataRequest("""some data""")
        req = mock.Mock(requests.Request, text=response_content)
        response = t.result(req)
        self.assertTrue(isinstance(response, RWSPostResponse))
        self.assertTrue(55, response.subjects_in_study_site)
        self.assertTrue(1103, response.subjects_in_study)


class TestPostMetadataRequest(unittest.TestCase):
    def test_post_data_request_response(self):
        """We can POST data and reformat the response"""
        response_content = """    <Response ReferenceNumber="82e942b0-48e8-4cf4-b299-51e2b6a89a1b"
              InboundODMFileOID=""
              IsTransactionSuccessful="1"
              SuccessStatistics="Rave objects touched: Subjects=0; Folders=0; Forms=0; Fields=0; LogLines=0" NewRecords=""
              SubjectNumberInStudy="1103" SubjectNumberInStudySite="55">
        </Response>"""
        t = PostMetadataRequest("Fixitol(Dev)", "Some Data")
        self.assertEqual("Fixitol(Dev)", t.project_name)
        self.assertEqual('metadata/studies/Fixitol(Dev)/drafts', t.url_path())
        self.assertEqual({'Content-type': 'text/xml'}, t.args().get('headers'))
        self.assertEqual('Some Data', t.args().get('data'))
        req = mock.Mock(requests.Request, text=response_content)
        response = t.result(req)
        self.assertTrue(isinstance(response, RWSPostResponse))
        self.assertTrue(55, response.subjects_in_study_site)
        self.assertTrue(1103, response.subjects_in_study)


class TestGlobalLibraryVersionRequest(unittest.TestCase):
    def create_request_object(self, **kwargs):
        default = dict(project_name="Fixitol(Dev)", oid="1234")
        default.update(kwargs)
        return GlobalLibraryVersionRequest(**default)

    def test_computed_url(self):
        """We get the correct URL for GlobalLibraryVersionRequest"""
        t = self.create_request_object()
        self.assertEqual("metadata/libraries/Fixitol(Dev)/versions/1234", t.url_path())

    def test_checks_for_numeric_oid(self):
        """We get the correct URL for GlobalLibraryVersionRequest"""
        with self.assertRaises(ValueError) as exc:
            t = self.create_request_object(oid='Study1234')
        self.assertEqual('oid must be an integer', str(exc.exception))

class TestGlobalLibraryVersionsRequest(unittest.TestCase):
    def create_request_object(self, project_name="Fixitol(Dev)"):
        t = GlobalLibraryVersionsRequest(project_name=project_name)
        return t

    def test_computed_url(self):
        t = self.create_request_object()
        self.assertEqual("metadata/libraries/Fixitol(Dev)/versions", t.url_path())

    def test_post_data_request_response(self):
        """We can POST data and reformat the response"""
        response_content = """<ODM ODMVersion="1.3" Granularity="Metadata" FileType="Snapshot" FileOID="d26b4d33-376d-4037-9747-684411190179" CreationDateTime=" 2013-04-08T01:29:13 " xmlns="http://www.cdisc.org/ns/odm/v1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata">
        <Study OID="IANTEST">
            <GlobalVariables>
                <StudyName>IANTEST</StudyName>
                <StudyDescription></StudyDescription>
                <ProtocolName>IANTEST</ProtocolName>
            </GlobalVariables>
            <MetaDataVersion OID="1203" Name="Webservice Outbound" />
            <MetaDataVersion OID="1195" Name="JC_Demo_Draft1" />
            <MetaDataVersion OID="1165" Name="Initial" />
        </Study>
    </ODM>
        """
        t = self.create_request_object()
        self.assertEqual("Fixitol(Dev)", t.project_name)
        self.assertEqual('metadata/libraries/Fixitol(Dev)/versions', t.url_path())
        req = mock.Mock(requests.Request, text=response_content)
        response = t.result(req)
        self.assertTrue(isinstance(response, RWSStudyMetadataVersions))
        for mdv in response:
            self.assertTrue(mdv.oid in ['1203', '1195', '1165'])
            self.assertTrue(mdv.name in ['Webservice Outbound', 'JC_Demo_Draft1','Initial'])


class TestGlobalLibraryDraftsRequest(unittest.TestCase):
    def create_request_object(self, project_name="Fixitol(Dev)"):
        t = GlobalLibraryDraftsRequest(project_name=project_name)
        return t

    def test_computed_url(self):
        t = self.create_request_object()
        self.assertEqual("metadata/libraries/Fixitol(Dev)/drafts", t.url_path())

    def test_post_data_request_response(self):
        """We can POST data and reformat the response"""
        response_content = """<ODM ODMVersion="1.3" Granularity="Metadata" FileType="Snapshot" FileOID="d26b4d33-376d-4037-9747-684411190179" CreationDateTime=" 2013-04-08T01:29:13 " xmlns="http://www.cdisc.org/ns/odm/v1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata">
        <Study OID="IANTEST">
            <GlobalVariables>
                <StudyName>IANTEST</StudyName>
                <StudyDescription></StudyDescription>
                <ProtocolName>IANTEST</ProtocolName>
            </GlobalVariables>
            <MetaDataVersion OID="1203" Name="Webservice Outbound" />
            <MetaDataVersion OID="1195" Name="JC_Demo_Draft1" />
            <MetaDataVersion OID="1165" Name="Initial" />
        </Study>
    </ODM>
        """
        t = self.create_request_object()
        self.assertEqual("Fixitol(Dev)", t.project_name)
        self.assertEqual('metadata/libraries/Fixitol(Dev)/drafts', t.url_path())
        req = mock.Mock(requests.Request, text=response_content)
        response = t.result(req)
        self.assertTrue(isinstance(response, RWSStudyMetadataVersions))
        for mdv in response:
            self.assertTrue(mdv.oid in ['1203', '1195', '1165'])
            self.assertTrue(mdv.name in ['Webservice Outbound', 'JC_Demo_Draft1','Initial'])


class TestGlobalLibrariesRequest(unittest.TestCase):
    def create_request_object(self, project_name="Fixitol(Dev)"):
        t = GlobalLibrariesRequest()
        return t

    def test_computed_url(self):
        t = self.create_request_object()
        self.assertEqual("metadata/libraries", t.url_path())

    def test_post_data_request_response(self):
        """We can POST data and reformat the response"""
        response_content = """    <ODM FileType="Snapshot" FileOID="767a1f8b-7b72-4d12-adbe-37d4d62ba75e"
         CreationDateTime="2013-04-08T10:02:17.781-00:00"
         ODMVersion="1.3"
         xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata"
         xmlns:xlink="http://www.w3.org/1999/xlink"
         xmlns="http://www.cdisc.org/ns/odm/v1.3">
         <Study OID="Fixitol(Dev)">
            <GlobalVariables>
                  <StudyName>Fixitol(Dev)</StudyName>
                  <StudyDescription/>
                  <ProtocolName>Fixitol</ProtocolName>
            </GlobalVariables>
         </Study>
         <Study OID="IANTEST(Prod)">
            <GlobalVariables>
                  <StudyName>IANTEST(Prod)</StudyName>
                  <StudyDescription/>
                  <ProtocolName>IANTEST</ProtocolName>
            </GlobalVariables>
         </Study>
    </ODM>

        """
        t = self.create_request_object()
        self.assertEqual('metadata/libraries', t.url_path())
        req = mock.Mock(requests.Request, text=response_content)
        response = t.result(req)
        self.assertTrue(isinstance(response, RWSStudies))
        for study in response:
            self.assertTrue(study.oid in ["IANTEST(Prod)", "Fixitol(Dev)"])
            self.assertTrue(study.environment in ["Prod", "Dev"],
                            "Unexpected environment (%s)" % study.environment)


class TestStudyVersionRequest(unittest.TestCase):

    def create_request_object(self, project_name="Fixitol(Dev)", oid="1234"):
        t = StudyVersionRequest(project_name=project_name, oid=oid)
        return t

    def test_computed_url(self):
        t = self.create_request_object()
        self.assertEqual('1234', t.oid)
        self.assertEqual("metadata/studies/Fixitol(Dev)/versions/1234", t.url_path())

    def test_post_data_request_response(self):
        """We can POST data and reformat the response"""
        response_content = """    <ODM FileType="Snapshot" FileOID="767a1f8b-7b72-4d12-adbe-37d4d62ba75e"
         CreationDateTime="2013-04-08T10:02:17.781-00:00"
         ODMVersion="1.3"
         xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata"
         xmlns:xlink="http://www.w3.org/1999/xlink"
         xmlns="http://www.cdisc.org/ns/odm/v1.3">
         <Study OID="Fixitol(Dev)">
            <GlobalVariables>
                  <StudyName>Fixitol(Dev)</StudyName>
                  <StudyDescription/>
                  <ProtocolName>Fixitol</ProtocolName>
            </GlobalVariables>
         </Study>
         <Study OID="IANTEST(Prod)">
            <GlobalVariables>
                  <StudyName>IANTEST(Prod)</StudyName>
                  <StudyDescription/>
                  <ProtocolName>IANTEST</ProtocolName>
            </GlobalVariables>
         </Study>
    </ODM>
        """
        t = self.create_request_object()
        req = mock.Mock(requests.Request, text=response_content)
        response = t.result(req)
        self.assertEqual(response_content, response)


class TestStudyVersionsRequest(unittest.TestCase):
    def create_request_object(self, project_name="Fixitol(Dev)"):
        t = StudyVersionsRequest(project_name=project_name)
        return t

    def test_computed_url(self):
        t = self.create_request_object()
        self.assertEqual("metadata/studies/Fixitol(Dev)/versions", t.url_path())

    def test_post_data_request_response(self):
        """We can POST data and reformat the response"""
        response_content = """<ODM ODMVersion="1.3" Granularity="Metadata" FileType="Snapshot" FileOID="d26b4d33-376d-4037-9747-684411190179" CreationDateTime=" 2013-04-08T01:29:13 " xmlns="http://www.cdisc.org/ns/odm/v1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata">
        <Study OID="IANTEST">
            <GlobalVariables>
                <StudyName>IANTEST</StudyName>
                <StudyDescription></StudyDescription>
                <ProtocolName>IANTEST</ProtocolName>
            </GlobalVariables>
            <MetaDataVersion OID="1203" Name="Webservice Outbound" />
            <MetaDataVersion OID="1195" Name="JC_Demo_Draft1" />
            <MetaDataVersion OID="1165" Name="Initial" />
        </Study>
    </ODM>
        """
        t = self.create_request_object()
        self.assertEqual("Fixitol(Dev)", t.project_name)
        self.assertEqual('metadata/studies/Fixitol(Dev)/versions', t.url_path())
        req = mock.Mock(requests.Request, text=response_content)
        response = t.result(req)
        self.assertTrue(isinstance(response, RWSStudyMetadataVersions))
        for mdv in response:
            self.assertTrue(mdv.oid in ['1203', '1195', '1165'])
            self.assertTrue(mdv.name in ['Webservice Outbound', 'JC_Demo_Draft1','Initial'])


class TestStudyDraftsRequest(unittest.TestCase):
    def create_request_object(self, project_name="Fixitol(Dev)"):
        t = StudyDraftsRequest(project_name=project_name)
        return t

    def test_computed_url(self):
        t = self.create_request_object()
        self.assertEqual("metadata/studies/Fixitol(Dev)/drafts", t.url_path())

    def test_post_data_request_response(self):
        """We can POST data and reformat the response"""
        response_content = """<ODM ODMVersion="1.3" Granularity="Metadata" FileType="Snapshot" FileOID="d26b4d33-376d-4037-9747-684411190179" CreationDateTime=" 2013-04-08T01:29:13 " xmlns="http://www.cdisc.org/ns/odm/v1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata">
        <Study OID="IANTEST">
            <GlobalVariables>
                <StudyName>IANTEST</StudyName>
                <StudyDescription></StudyDescription>
                <ProtocolName>IANTEST</ProtocolName>
            </GlobalVariables>
            <MetaDataVersion OID="1203" Name="Webservice Outbound" />
            <MetaDataVersion OID="1195" Name="JC_Demo_Draft1" />
            <MetaDataVersion OID="1165" Name="Initial" />
        </Study>
    </ODM>
        """
        t = self.create_request_object()
        self.assertEqual("Fixitol(Dev)", t.project_name)
        self.assertEqual('metadata/studies/Fixitol(Dev)/drafts', t.url_path())
        req = mock.Mock(requests.Request, text=response_content)
        response = t.result(req)
        self.assertTrue(isinstance(response, RWSStudyMetadataVersions))
        for mdv in response:
            self.assertTrue(mdv.oid in ['1203', '1195', '1165'])
            self.assertTrue(mdv.name in ['Webservice Outbound', 'JC_Demo_Draft1','Initial'])


class TestMetadataStudiesRequest(unittest.TestCase):
    def create_request_object(self, project_name="Fixitol(Dev)"):
        t = MetadataStudiesRequest()
        return t

    def test_computed_url(self):
        t = self.create_request_object()
        self.assertEqual("metadata/studies", t.url_path())

    def test_post_data_request_response(self):
        """We can POST data and reformat the response"""
        response_content = """    <ODM FileType="Snapshot" FileOID="767a1f8b-7b72-4d12-adbe-37d4d62ba75e"
         CreationDateTime="2013-04-08T10:02:17.781-00:00"
         ODMVersion="1.3"
         xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata"
         xmlns:xlink="http://www.w3.org/1999/xlink"
         xmlns="http://www.cdisc.org/ns/odm/v1.3">
         <Study OID="Fixitol(Dev)">
            <GlobalVariables>
                  <StudyName>Fixitol(Dev)</StudyName>
                  <StudyDescription/>
                  <ProtocolName>Fixitol</ProtocolName>
            </GlobalVariables>
         </Study>
         <Study OID="IANTEST(Prod)">
            <GlobalVariables>
                  <StudyName>IANTEST(Prod)</StudyName>
                  <StudyDescription/>
                  <ProtocolName>IANTEST</ProtocolName>
            </GlobalVariables>
         </Study>
    </ODM>

        """
        t = self.create_request_object()
        self.assertEqual('metadata/studies', t.url_path())
        req = mock.Mock(requests.Request, text=response_content)
        response = t.result(req)
        self.assertTrue(isinstance(response, RWSStudies))
        for study in response:
            self.assertTrue(study.oid in ["IANTEST(Prod)", "Fixitol(Dev)"])
            self.assertTrue(study.environment in ["Prod", "Dev"],
                            "Unexpected environment (%s)" % study.environment)


class TestClinicalStudiesRequest(unittest.TestCase):

    def create_request_object(self):
        t = ClinicalStudiesRequest()
        return t

    def test_computed_url(self):
        """We evaluate the path for ClinicalStudiesRequest"""
        t = self.create_request_object()
        self.assertEqual("studies", t.url_path())

    def test_process_response(self):
        """We process the response"""
        t = self.create_request_object()
        response_content = """<ODM FileType="Snapshot" FileOID="" CreationDateTime="" ODMVersion="1.3"
xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata" xmlns="http://www.cdisc.org/ns/odm/v1.3">
 <Study OID="Lab Test">
   <GlobalVariables>
      <StudyName>Lab Test</StudyName>
      <StudyDescription />
      <ProtocolName>Lab Test</ProtocolName>
   </GlobalVariables>
 </Study>
 <Study OID="Mediflex">
   <GlobalVariables>
      <StudyName>Mediflex</StudyName>
      <StudyDescription />
      <ProtocolName>Mediflex</ProtocolName>
   </GlobalVariables>
 </Study>
</ODM>"""
        req = mock.Mock(requests.Request, text=response_content)
        response = t.result(req)
        self.assertTrue(isinstance(response, RWSStudies))
        for study in response:
            self.assertTrue(study.oid in ['Lab Test', 'Mediflex'])


class TestCacheFlushRequest(unittest.TestCase):
    def create_request_object(self):
        t = CacheFlushRequest()
        return t

    def test_computed_url(self):
        """We evaluate the path for ClinicalStudiesRequest"""
        t = self.create_request_object()
        self.assertEqual("webservice.aspx?CacheFlush", t.url_path())

    def test_process_response(self):
        """We process the response"""
        t = self.create_request_object()
        response_content = """    <Response ReferenceNumber="82e942b0-48e8-4cf4-b299-51e2b6a89a1b"
        InboundODMFileOID=""
        IsTransactionSuccessful="1"
        SuccessStatistics="Rave objects touched: Subjects=0; Folders=0; Forms=0; Fields=0; LogLines=0" NewRecords="">
    </Response>
    """
        req = mock.Mock(requests.Request, text=response_content)
        response = t.result(req)
        self.assertTrue(isinstance(response, RWSResponse))


class TestDiagnosticsRequest(unittest.TestCase):
    def create_request_object(self):
        t = DiagnosticsRequest()
        return t

    def test_computed_url(self):
        """We evaluate the path for DiagnosticsRequest"""
        t = self.create_request_object()
        self.assertEqual("diagnostics", t.url_path())


class TestBuildVersionRequest(unittest.TestCase):
    def create_request_object(self):
        t = BuildVersionRequest()
        return t

    def test_computed_url(self):
        """We evaluate the path for BuildVersionRequest"""
        t = self.create_request_object()
        self.assertEqual("version/build", t.url_path())


class TimeoutTest(unittest.TestCase):
    """
    Strictly belongs in test_rwslib but it interacts with HttPretty which is used in that unit
    """
    def test_timeout(self):
        """Test against an external website to verify timeout (mocking doesn't help as far as I can work out)"""
        import rwslib

        # Test that unauthorised request times out
        rave = rwslib.RWSConnection('http://innovate.mdsol.com')
        with self.assertRaises(requests.exceptions.Timeout):
            rave.send_request(rwslib.rws_requests.ClinicalStudiesRequest(),timeout=0.0001, verify=False)

        # Raise timeout and check no timeout occurs.  An exception will be raised because the request is unauthorised
        with self.assertRaises(rwslib.AuthorizationException):
            rave.send_request(rwslib.rws_requests.ClinicalStudiesRequest(),timeout=3600, verify=False)


if __name__ == '__main__':
    unittest.main()
