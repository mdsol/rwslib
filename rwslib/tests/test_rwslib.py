__author__ = 'isparks'

import unittest
import rwslib
import httpretty

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


if __name__ == '__main__':
    unittest.main()
