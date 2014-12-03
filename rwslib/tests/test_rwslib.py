__author__ = 'isparks'

import unittest
import rwslib
import httpretty
import requests
import socket
import errno

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

    @httpretty.activate
    def test_connection_failure(self):
        """Test we get a failure if we do not retry"""
        rave = rwslib.RWSConnection('https://innovate.mdsol.com')


        class FailResponse():
            """A fake response that will raise a connection error as if socket connection failed"""
            def fill_filekind(self, fk):
                raise socket.error(errno.ECONNREFUSED, "Refused")


        httpretty.register_uri(
            httpretty.GET, "https://innovate.mdsol.com/RaveWebServices/version",
                 responses=[
                               FailResponse(), #First try
                            ])


        #Now my test
        def do():
            v = rave.send_request(rwslib.rws_requests.VersionRequest())

        self.assertRaises(requests.ConnectionError, do)


    @httpretty.activate
    def test_version_with_retry(self):
        """A simple test that fails with a socket error on first attempts"""
        rave = rwslib.RWSConnection('https://innovate.mdsol.com')


        class FailResponse():
            """A fake response that will raise a connection error as if socket connection failed"""
            def fill_filekind(self, fk):
                raise socket.error(errno.ECONNREFUSED, "Refused")


        httpretty.register_uri(
            httpretty.GET, "https://innovate.mdsol.com/RaveWebServices/version",
                 responses=[
                               FailResponse(), #First try
                               FailResponse(), # Retry 1
                               FailResponse(), # Retry 2
                               httpretty.Response(body='1.0.0', status=200), #Retry 3
                            ])


        #Make request
        v = rave.send_request(rwslib.rws_requests.VersionRequest(), retries=3)

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
        rave = rwslib.RWSConnection('https://innovate.mdsol.com')
        with self.assertRaises(requests.exceptions.Timeout):
            rave.send_request(rwslib.rws_requests.ClinicalStudiesRequest(),timeout=0.0001)

        #Raise timeout and check no timeout occurs.  An exception will be raised because the request is unauthorised
        with self.assertRaises(rwslib.RWSException):
            rave.send_request(rwslib.rws_requests.ClinicalStudiesRequest(),timeout=3600)


if __name__ == '__main__':
    unittest.main()
