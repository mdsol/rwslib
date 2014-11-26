__author__ = 'isparks'

import unittest
import rwslib
import httpretty
import requests

class VersionTest(unittest.TestCase):
    """Test for the version method"""
    @httpretty.activate
    def test_version(self):
        """A simple test, patching the get request so that it does not hit a website"""

        httpretty.register_uri(
            httpretty.GET, "https://innovate.mdsol.com/RaveWebServices/version",
            status=200,
            body="1.0.0")

        #Now my test
        rave = rwslib.RWSConnection('https://innovate.mdsol.com')
        v = rave.send_request(rwslib.rws_requests.VersionRequest())

        self.assertEqual(v, '1.0.0')
        self.assertEqual(rave.last_result.status_code,200)


class TestMustBeRWSRequestSubclass(unittest.TestCase):
    """Test that request object passed must be RWSRequest subclass"""
    def test_basic(self):
        """Must be rwssubclass or ValueError"""

        def do():
            rave = rwslib.RWSConnection('test')
            v = rave.send_request(object())


        self.assertRaises(ValueError, do)


class RequestTime(unittest.TestCase):
    """Test for the last request time property"""
    @httpretty.activate
    def test_request_time(self):
        """A simple test, patching the get request so that it does not hit a website"""

        httpretty.register_uri(
            httpretty.GET, "https://innovate.mdsol.com/RaveWebServices/version",
            status=200,
            body="1.0.0")

        #Now my test
        rave = rwslib.RWSConnection('https://innovate.mdsol.com')
        v = rave.send_request(rwslib.rws_requests.VersionRequest())
        request_time = rave.request_time
        self.assertIs(type(request_time),float)

class Timeout(unittest.TestCase):

    def test_timeout(self):
        """Test against an external website to verify timeout (mocking doesn't help as far as I can work out)"""

        #Test that unauthorised request times out
        rave = rwslib.RWSConnection('https://innovate.mdsol.com',timeout=0.0001)
        with self.assertRaises(requests.exceptions.Timeout):
            rave.send_request(rwslib.rws_requests.ClinicalStudiesRequest())

        #Raise timeout and check no timeout occurs.  An exception will be raised because the request is unauthorised
        rave.timeout=3600
        with self.assertRaises(rwslib.RWSException):
            rave.send_request(rwslib.rws_requests.ClinicalStudiesRequest())


if __name__ == '__main__':
    unittest.main()
