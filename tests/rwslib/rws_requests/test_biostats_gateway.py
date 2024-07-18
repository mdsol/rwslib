# -*- coding: utf-8 -*-

__author__ = 'glow'

import unittest

from six.moves.urllib_parse import quote

from rwslib.rws_requests.biostats_gateway import check_dataset_format, DATASET_FORMATS, \
    dataset_format_to_extension, CVMetaDataRequest, FormDataRequest, MetaDataRequest, \
    ProjectMetaDataRequest, ViewMetaDataRequest, CommentDataRequest, ProtocolDeviationsRequest, \
    DataDictionariesRequest


class TestCheckDatasetFormat(unittest.TestCase):
    def test_good_cases(self):
        """Good happy case for check_dataset_format"""
        try:
            check_dataset_format("CSV")
            check_dataset_format("XML")
            check_dataset_format("csv")
            check_dataset_format("xml")
        except ValueError:
            self.fail()

    def test_poor_cases(self):
        """Bad formats for check_dataset_format"""
        for nonsense in ['xls', 'dat', 'xslx']:
            with self.assertRaises(ValueError) as exc:
                check_dataset_format(nonsense)
            self.assertEqual("dataset_format is expected to be one of "
                             "%s. '%s' is not valid" % (', '.join(DATASET_FORMATS.keys()),
                                                        nonsense),
                             str(exc.exception))


class TestDatasetFormatToExtension(unittest.TestCase):
    def test_good_cases(self):
        """Good happy case for check_dataset_format"""
        for dsf, format_ in DATASET_FORMATS.items():
            match = dataset_format_to_extension(dsf)
            self.assertEqual(format_, match)

    def test_poor_cases(self):
        """Bad formats for check_dataset_format"""
        for nonsense in ['xls', 'dat', 'xslx']:
            with self.assertRaises(ValueError) as exc:
                dataset_format_to_extension(nonsense)
            self.assertEqual("dataset_format is expected to be one of "
                             "%s. '%s' is not valid" % (', '.join(DATASET_FORMATS.keys()),
                                                        nonsense),
                             str(exc.exception))


class TestCVMetaDataRequest(unittest.TestCase):
    def create_request_object(self,
                              project_name,
                              environment_name,
                              versionitem=None,
                              rawsuffix=None,
                              codelistsuffix=None,
                              decodesuffix=None):
        t = CVMetaDataRequest(project_name,
                              environment_name,
                              versionitem=versionitem,
                              rawsuffix=rawsuffix,
                              codelistsuffix=codelistsuffix,
                              decodesuffix=decodesuffix)
        return t

    def test_create_cv_metadata_request(self):
        """Create a CVMetaDataRequest"""
        t = self.create_request_object("Mediflex", "Dev")
        self.assertEqual("Mediflex(Dev)", t.studyname_environment())
        self.assertEqual("studies/Mediflex(Dev)/datasets/metadata/regular", t.url_path())


class TestFormDataRequest(unittest.TestCase):
    def create_request_object(self,
                              project_name,
                              environment_name,
                              dataset_type,
                              form_oid,
                              start=None,
                              dataset_format="csv"):
        t = FormDataRequest(project_name,
                            environment_name,
                            dataset_type,
                            form_oid,
                            start=start,
                            dataset_format=dataset_format)
        return t

    def test_successful_configuration(self):
        """We can successfully request FormData"""
        t = self.create_request_object("Mediflex", "Dev", "raw", "DM")
        self.assertEqual('studies/Mediflex(Dev)/datasets/raw/DM.csv', t.url_path())
        t = self.create_request_object("Mediflex", "Dev", "raw", "DM", dataset_format="xml")
        self.assertEqual('studies/Mediflex(Dev)/datasets/raw/DM', t.url_path())


class TestMetaDataRequest(unittest.TestCase):
    def create_request_object(self,
                              dataset_format="csv"):
        t = MetaDataRequest(dataset_format=dataset_format)
        return t

    def test_successful_configuration(self):
        """We can successfully request MetaData"""
        t = self.create_request_object()
        self.assertEqual('datasets/ClinicalViewMetadata.csv', t.url_path())
        t = self.create_request_object(dataset_format="xml")
        self.assertEqual('datasets/ClinicalViewMetadata', t.url_path())


class TestProjectMetaDataRequest(unittest.TestCase):
    def create_request_object(self,
                              project_name="Mediflex",
                              dataset_format="csv"):
        t = ProjectMetaDataRequest(project_name=project_name,
                                   dataset_format=dataset_format)
        return t

    def test_successful_configuration(self):
        """We can successfully request ProjectMetaData"""
        t = self.create_request_object()
        self.assertEqual('datasets/ClinicalViewMetadata.csv?ProjectName=Mediflex', t.url_path())
        t = self.create_request_object(dataset_format="xml")
        self.assertEqual('datasets/ClinicalViewMetadata?ProjectName=Mediflex', t.url_path())


class TestViewMetaDataRequest(unittest.TestCase):
    def create_request_object(self,
                              view_name="DM",
                              dataset_format="csv"):
        t = ViewMetaDataRequest(view_name=view_name,
                                dataset_format=dataset_format)
        return t

    def test_successful_configuration(self):
        """We can successfully request ViewMetaData"""
        t = self.create_request_object()
        self.assertEqual('datasets/ClinicalViewMetadata.csv?ViewName=DM', t.url_path())
        t = self.create_request_object(dataset_format="xml")
        self.assertEqual('datasets/ClinicalViewMetadata?ViewName=DM', t.url_path())


class TestCommentDataRequest(unittest.TestCase):
    def create_request_object(self,
                              project_name,
                              environment_name,
                              dataset_format="csv"):
        t = CommentDataRequest(project_name=project_name,
                               environment_name=environment_name,
                                dataset_format=dataset_format)
        return t

    def test_successful_configuration(self):
        """We can successfully request CommentData"""
        t = self.create_request_object('Mediflex', 'Dev')
        self.assertEqual('datasets/SDTMComments.csv?studyid=%s' % quote(t.studyname_environment()),
                         t.url_path())
        t = self.create_request_object('Mediflex', 'Dev', dataset_format="xml")
        self.assertEqual('datasets/SDTMComments?studyid=%s' % quote(t.studyname_environment()),
                         t.url_path())


class TestProtocolDeviationsRequest(unittest.TestCase):
    def create_request_object(self,
                              project_name,
                              environment_name,
                              dataset_format="csv"):
        t = ProtocolDeviationsRequest(project_name=project_name,
                                      environment_name=environment_name,
                                      dataset_format=dataset_format)
        return t

    def test_successful_configuration(self):
        """We can successfully request ProtocolDeviations"""
        t = self.create_request_object('Mediflex', 'Dev')
        self.assertEqual('datasets/SDTMProtocolDeviations.csv?studyid=%s' % quote(t.studyname_environment()),
                         t.url_path())
        t = self.create_request_object('Mediflex', 'Dev', dataset_format="xml")
        self.assertEqual('datasets/SDTMProtocolDeviations?studyid=%s' % quote(t.studyname_environment()),
                         t.url_path())


class TestDataDictionariesRequest(unittest.TestCase):
    def create_request_object(self,
                              project_name,
                              environment_name,
                              dataset_format="csv"):
        t = DataDictionariesRequest(project_name=project_name,
                                    environment_name=environment_name,
                                    dataset_format=dataset_format)
        return t

    def test_successful_configuration(self):
        """We can successfully request ProtocolDeviations"""
        t = self.create_request_object('Mediflex', 'Dev')
        self.assertEqual('datasets/SDTMDataDictionaries.csv?studyid=%s' % quote(t.studyname_environment()),
                         t.url_path())
        t = self.create_request_object('Mediflex', 'Dev', dataset_format="xml")
        self.assertEqual('datasets/SDTMDataDictionaries?studyid=%s' % quote(t.studyname_environment()),
                         t.url_path())
