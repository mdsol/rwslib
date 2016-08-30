# -*- coding: utf-8 -*-

from unittest import TestCase
from six.moves.urllib.parse import urlparse, parse_qsl, unquote_plus
from rwslib.rws_requests import ConfigurableDatasetRequest


class Url(object):
    """
    Taken from: http://stackoverflow.com/questions/5371992/comparing-two-urls-in-python
    A url object that can be compared with other url orbjects
    without regard to the vagaries of encoding, escaping, and ordering
    of parameters in query strings.
    """

    def __init__(self, url):
        parts = urlparse(url)
        _query = frozenset(parse_qsl(parts.query))
        _path = unquote_plus(parts.path)
        parts = parts._replace(query=_query, path=_path)
        self.parts = parts

    def __eq__(self, other):
        return self.parts == other.parts

    def __hash__(self):
        return hash(self.parts)


class TestGenericConfigurableDataset(TestCase):
    def test_url_is_constructed_as_expected(self):
        """Given the arguments to the function, we get the correct URL"""
        t = ConfigurableDatasetRequest('SomeCoolSet',
                                       dataset_format="json",
                                       params=dict(subjectid='45838',
                                                   locale='eng',
                                                   app_instance_uuid='1234'))
        self.assertEqual(Url('datasets/SomeCoolSet.json?subjectid=45838&'
                             'locale=eng&'
                             'app_instance_uuid=1234'), Url(t.url_path()))

    def test_specify_format(self):
        """catch the dataset_format if supplied"""
        t = ConfigurableDatasetRequest('SomeCoolSet',
                                       params=dict(subjectid='45838',
                                                   locale='eng',
                                                   app_instance_uuid='1234'))

        self.assertEqual(Url('datasets/SomeCoolSet?subjectid=45838&'
                             'locale=eng&'
                             'app_instance_uuid=1234'), Url(t.url_path()))
        t = ConfigurableDatasetRequest('SomeCoolSet',
                                       dataset_format="csv",
                                       params=dict(subjectid='45838',
                                                   locale='eng',
                                                   app_instance_uuid='1234'))

        self.assertEqual(Url('datasets/SomeCoolSet.csv?subjectid=45838&'
                             'locale=eng&'
                             'app_instance_uuid=1234'), Url(t.url_path()))

    def test_validate_format(self):
        """validate the dataset_format if required"""

        class WidgetConfigurableDataset(ConfigurableDatasetRequest):
            VALID_DATASET_FORMATS = ('json', 'xml')

        t = WidgetConfigurableDataset('SomeCoolSet',
                                      params=dict(subjectid='45838',
                                                  locale='eng',
                                                  app_instance_uuid='1234'))

        self.assertEqual(Url('datasets/SomeCoolSet?subjectid=45838&'
                             'locale=eng&'
                             'app_instance_uuid=1234'), Url(t.url_path()))

        with self.assertRaises(ValueError) as err:
            t = WidgetConfigurableDataset('SomeCoolSet',
                                          dataset_format="tsv",
                                          params=dict(subjectid='45838',
                                                      locale='eng',
                                                      app_instance_uuid='1234'))

        self.assertEqual("Dataset format tsv is not valid for SomeCoolSet", str(err.exception))
