__author__ = 'isparks'

import unittest
import rws
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
        rave = rws.RWSConnection('https://innovate.mdsol.com')
        v = rave.version()

        self.assertEqual(v, '1.0.0')
        self.assertEqual(rave.last_result.status_code,200)





if __name__ == '__main__':
    unittest.main()
