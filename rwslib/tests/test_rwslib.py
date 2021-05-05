import os
import unittest

import httpretty
import requests
from mock import mock

import rwslib
from rwslib.rws_requests import StudyDatasetRequest
from rwslib.rwsobjects import RWSPostErrorResponse


# TODO: per the Repository, httpretty is not supporting Python3 - do we need to replace?


class TestVersion(unittest.TestCase):
    """Test for the version method"""

    @httpretty.activate
    def test_version(self):
        """A simple test, patching the get request so that it does not hit a website"""

        httpretty.register_uri(
            httpretty.GET,
            "https://innovate.mdsol.com/RaveWebServices/version",
            status=200,
            body="1.0.0",
        )

        # Now my test
        rave = rwslib.RWSConnection("https://innovate.mdsol.com")
        v = rave.send_request(rwslib.rws_requests.VersionRequest())

        self.assertEqual(v, "1.0.0")
        self.assertEqual(rave.last_result.status_code, 200)

    def test_connection_failure(self):
        """Test we get a failure if we do not retry"""
        with mock.patch("requests.sessions.Session.get") as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError()
            rave = rwslib.RWSConnection("https://innovate.mdsol.com")
            with self.assertRaises(requests.exceptions.ConnectionError) as exc:
                v = rave.send_request(rwslib.rws_requests.VersionRequest())

    """Test with only mdsol sub-domain"""

    @httpretty.activate
    def test_sub_domain(self):
        """A simple test, patching the get request so that it does not hit a website"""

        httpretty.register_uri(
            httpretty.GET,
            "https://innovate.mdsol.com/RaveWebServices/version",
            status=200,
            body="1.0.0",
        )

        # Now my test
        rave = rwslib.RWSConnection("innovate")
        v = rave.send_request(rwslib.rws_requests.VersionRequest())

        self.assertEqual("1.0.0", v)
        self.assertEqual(rave.domain, "https://innovate.mdsol.com")
        self.assertEqual(rave.last_result.status_code, 200)

    """Test for overriding the virtual directory"""

    @httpretty.activate
    def test_virtual_directory(self):
        """A simple test, patching the get request so that it does not hit a website"""

        httpretty.register_uri(
            httpretty.GET,
            "https://innovate.mdsol.com/RWS/version",
            status=200,
            body="1.0.0",
        )

        # Now my test
        rave = rwslib.RWSConnection("https://innovate.mdsol.com", virtual_dir="RWS")
        v = rave.send_request(rwslib.rws_requests.VersionRequest())

        self.assertEqual(v, "1.0.0")
        self.assertEqual(rave.last_result.status_code, 200)


class TestMustBeRWSRequestSubclass(unittest.TestCase):
    """Test that request object passed must be RWSRequest subclass"""

    def test_basic(self):
        """Must be rwssubclass or ValueError"""

        def do():
            rave = rwslib.RWSConnection("test")
            v = rave.send_request(object())

        self.assertRaises(ValueError, do)


class TestRequestTime(unittest.TestCase):
    """Test for the last request time property"""

    @httpretty.activate
    def test_request_time(self):
        """A simple test, patching the get request so that it does not hit a website"""

        httpretty.register_uri(
            httpretty.GET,
            "https://innovate.mdsol.com/RaveWebServices/version",
            status=200,
            body="1.0.0",
        )

        # Now my test
        rave = rwslib.RWSConnection("https://innovate.mdsol.com")
        v = rave.send_request(rwslib.rws_requests.VersionRequest())
        request_time = rave.request_time
        self.assertIs(type(request_time), float)


class TestErrorResponse(unittest.TestCase):
    @httpretty.activate
    def test_503_error(self):
        """Test that when we don't attempt to XMLParse a non-xml response"""

        httpretty.register_uri(
            httpretty.GET,
            "https://innovate.mdsol.com/RaveWebServices/version",
            status=503,
            body="HTTP 503 Service Temporarily Unavailable",
        )
        # Now my test
        rave = rwslib.RWSConnection("https://innovate.mdsol.com")
        with self.assertRaises(rwslib.RWSException) as exc:
            v = rave.send_request(rwslib.rws_requests.VersionRequest())
        self.assertEqual(
            "HTTP 503 Service Temporarily Unavailable", exc.exception.rws_error
        )
        self.assertEqual("Unexpected Status Code (503)", str(exc.exception))

    @httpretty.activate
    def test_500_error(self):
        """Test that when we don't attempt to XMLParse a non-xml response"""

        httpretty.register_uri(
            httpretty.GET,
            "https://innovate.mdsol.com/RaveWebServices/version",
            status=500,
            body="HTTP 500.13 Web server is too busy.",
        )
        # Now my test
        rave = rwslib.RWSConnection("https://innovate.mdsol.com")
        with self.assertRaises(rwslib.RWSException) as exc:
            v = rave.send_request(rwslib.rws_requests.VersionRequest())
        self.assertEqual("HTTP 500.13 Web server is too busy.", exc.exception.rws_error)
        self.assertEqual("Server Error (500)", str(exc.exception))

    @httpretty.activate
    def test_400_error_error_response(self):
        """Parse the IIS Response Error structure"""

        text = b"""<Response
        ReferenceNumber="5b1fa9a3-0cf3-46b6-8304-37c2e3b7d04f5"
        InboundODMFileOID="1"
        IsTransactionSuccessful = "0"
        ReasonCode="RWS00024"
        ErrorOriginLocation="/ODM/ClinicalData[1]/SubjectData[1]"
        SuccessStatistics="Rave objects touched: Subjects=0; Folders=0; Forms=0; Fields=0; LogLines=0"
        ErrorClientResponseMessage="Subject already exists.">
        </Response>
        """
        httpretty.register_uri(
            httpretty.POST,
            "https://innovate.mdsol.com/RaveWebServices/webservice.aspx?PostODMClinicalData",
            status=400,
            body=text,
        )

        # Now my test
        rave = rwslib.RWSConnection("https://innovate.mdsol.com")
        with self.assertRaises(rwslib.RWSException) as exc:
            v = rave.send_request(rwslib.rws_requests.PostDataRequest("<ODM/>"))
        self.assertEqual("Subject already exists.", str(exc.exception))
        rws_error = exc.exception.rws_error
        self.assertEqual("/ODM/ClinicalData[1]/SubjectData[1]", str(rws_error.error_origin_location))
        self.assertEqual("RWS00024", str(rws_error.reasoncode))
        self.assertTrue(isinstance(rws_error, (RWSPostErrorResponse, )))
        self.assertFalse(rws_error.istransactionsuccessful)

    @httpretty.activate
    def test_400_error_iis_error(self):
        """Test that when we don't attempt to XMLParse a non-xml response"""

        text = b"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8" />
            <title>OOPS! Error Occurred. Sorry about this.</title>
        </head>
        <body>
            <h2>OOPS! Error Occurred</h2>
        </body>
        </html>
        """

        httpretty.register_uri(
            httpretty.GET,
            "https://innovate.mdsol.com/RaveWebServices/version",
            status=400,
            body=text,
        )

        # Now my test
        rave = rwslib.RWSConnection("https://innovate.mdsol.com")
        with self.assertRaises(rwslib.RWSException) as exc:
            v = rave.send_request(rwslib.rws_requests.VersionRequest())
        self.assertEqual("IIS Error", str(exc.exception))

    @httpretty.activate
    def test_400_error_ODM_error(self):
        """Test that when we don't attempt to XMLParse a non-xml response"""

        text = b"""<?xml version="1.0" encoding="utf-8"?>
        <ODM xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata"
         FileType="Snapshot"
         CreationDateTime="2013-04-08T10:28:49.578-00:00"
         FileOID="4d13722a-ceb6-4419-a917-b6ad5d0bc30e"
         ODMVersion="1.3"
         mdsol:ErrorDescription="Incorrect login and password combination. [RWS00008]"
         xmlns="http://www.cdisc.org/ns/odm/v1.3" />
        """

        httpretty.register_uri(
            httpretty.GET,
            "https://innovate.mdsol.com/RaveWebServices/version",
            status=400,
            body=text,
        )

        # Now my test
        rave = rwslib.RWSConnection("https://innovate.mdsol.com")
        with self.assertRaises(rwslib.RWSException) as exc:
            v = rave.send_request(rwslib.rws_requests.VersionRequest())
        self.assertEqual(
            "Incorrect login and password combination. [RWS00008]", str(exc.exception)
        )

    @httpretty.activate
    def test_401_error_error_response_no_header(self):
        """Parse the IIS Response Error structure"""

        text = "Authorization Header not provided"

        httpretty.register_uri(
            httpretty.POST,
            "https://innovate.mdsol.com/RaveWebServices/webservice.aspx?PostODMClinicalData",
            status=401,
            body=text,
            content_type="text/html; charset=utf-8"
        )

        # Now my test
        rave = rwslib.RWSConnection("https://innovate.mdsol.com")
        with self.assertRaises(rwslib.AuthorizationException) as exc:
            v = rave.send_request(rwslib.rws_requests.PostDataRequest("<ODM/>"))
        self.assertEqual(text, str(exc.exception))

    @httpretty.activate
    def test_401_error_error_response_unauthorized(self):
        """Parse the IIS Response Error structure"""

        text = b"<h3>HTTP Error 401.0 - Unauthorized</h3>"

        httpretty.register_uri(
            httpretty.POST,
            "https://innovate.mdsol.com/RaveWebServices/webservice.aspx?PostODMClinicalData",
            status=401,
            body=text,
            content_type="text/html; charset=utf-8"
        )

        # Now my test
        rave = rwslib.RWSConnection("https://innovate.mdsol.com")
        with self.assertRaises(rwslib.RWSException) as exc:
            v = rave.send_request(rwslib.rws_requests.PostDataRequest("<ODM/>"))
        self.assertEqual("Unauthorized.", str(exc.exception))

    @httpretty.activate
    def test_401_error_error_response_unauthorized_but_wonky(self):
        """Parse the IIS Response Error structure"""

        text = b"""<Response
            ReferenceNumber="0b47fe86-542f-4070-9e7d-16396a5ef08a"
            InboundODMFileOID="Not Supplied"
            IsTransactionSuccessful="0"
            ReasonCode="RWS00092"
            ErrorClientResponseMessage="You shall not pass">
            </Response>
        """

        httpretty.register_uri(
            httpretty.POST,
            "https://innovate.mdsol.com/RaveWebServices/webservice.aspx?PostODMClinicalData",
            status=401,
            body=text,
            content_type="text/xml",
        )

        # Now my test
        rave = rwslib.RWSConnection("https://innovate.mdsol.com")
        with self.assertRaises(rwslib.RWSException) as exc:
            v = rave.send_request(rwslib.rws_requests.PostDataRequest("<ODM/>"))
        self.assertEqual("You shall not pass", str(exc.exception))

    @httpretty.activate
    def test_401_error_error_response_unauthorized_without_content_type(self):
        """Parse the IIS Response Error structure"""

        text = b"""<Response
            ReferenceNumber="0b47fe86-542f-4070-9e7d-16396a5ef08a"
            InboundODMFileOID="Not Supplied"
            IsTransactionSuccessful="0"
            ReasonCode="RWS00092"
            ErrorClientResponseMessage="You shall not pass">
            </Response>
        """

        httpretty.register_uri(
            httpretty.POST,
            "https://innovate.mdsol.com/RaveWebServices/webservice.aspx?PostODMClinicalData",
            status=401,
            body=text,
        )

        # Now my test
        rave = rwslib.RWSConnection("https://innovate.mdsol.com")
        with self.assertRaises(rwslib.RWSException) as exc:
            v = rave.send_request(rwslib.rws_requests.PostDataRequest("<ODM/>"))
        self.assertEqual("You shall not pass", str(exc.exception))

    @httpretty.activate
    def test_405_error_error_response_response_object(self):
        """Parse the IIS Response Error structure"""

        text = b"""<Response
            ReferenceNumber="0b47fe86-542f-4070-9e7d-16396a5ef08a"
            InboundODMFileOID="Not Supplied"
            IsTransactionSuccessful="0"
            ReasonCode="RWS00092"
            ErrorClientResponseMessage="You shall not pass">
            </Response>
        """

        httpretty.register_uri(
            httpretty.POST,
            "https://innovate.mdsol.com/RaveWebServices/webservice.aspx?PostODMClinicalData",
            status=405,
            body=text,
        )

        # Now my test
        rave = rwslib.RWSConnection("https://innovate.mdsol.com")
        with self.assertRaises(rwslib.RWSException) as exc:
            v = rave.send_request(rwslib.rws_requests.PostDataRequest(b"<ODM/>"))
        self.assertEqual("You shall not pass", str(exc.exception))

    @httpretty.activate
    def test_405_error_ODM_error(self):
        """Parse a 405 error represented as an ODM"""
        # NOTE: this is not a real response, 405's are handled by IIS and not
        #  put through the ODM wringer
        text = b"""\xef\xbb\xbf<?xml version="1.0" encoding="utf-8"?>
        <ODM xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata"
         FileType="Snapshot"
         CreationDateTime="2013-04-08T10:28:49.578-00:00"
         FileOID="4d13722a-ceb6-4419-a917-b6ad5d0bc30e"
         ODMVersion="1.3"
         mdsol:ErrorDescription="Incorrect login and password combination. [RWS00008]"
         xmlns="http://www.cdisc.org/ns/odm/v1.3" />

        """

        httpretty.register_uri(
            httpretty.GET,
            "https://innovate.mdsol.com/RaveWebServices/studies",
            status=405,
            body=text,
            content_type="text/xml"
        )

        # Now my test
        rave = rwslib.RWSConnection("https://innovate.mdsol.com")
        with self.assertRaises(rwslib.RWSException) as exc:
            v = rave.send_request(rwslib.rws_requests.ClinicalStudiesRequest())
        self.assertEqual(
            "Incorrect login and password combination. [RWS00008]", str(exc.exception)
        )

    @httpretty.activate
    def test_405_error_iis_error(self):
        """Test we handle the IIS error page"""

        text = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8" />
            <title>OOPS! Error Occurred. Sorry about this.</title>
        </head>
        <body>
            <h2>OOPS! Error Occurred</h2>
        </body>
        </html>
        """

        httpretty.register_uri(
            httpretty.GET,
            "https://innovate.mdsol.com/RaveWebServices/version",
            status=405,
            body=text,
        )

        # Now my test
        rave = rwslib.RWSConnection("https://innovate.mdsol.com")
        with self.assertRaises(rwslib.RWSException) as exc:
            v = rave.send_request(rwslib.rws_requests.VersionRequest())
        self.assertEqual("Unexpected Status Code (405)", str(exc.exception))

    @httpretty.activate
    def test_multibyte_character_encoding(self):
        """
        Test the output is properly encoded, Rave sends text/xml, but the underlying library doesn't seem to detect the
            encoding correctly
        """
        with open(
            os.path.join(
                os.path.dirname(__file__), "fixtures", "test_double_byte_chars.xml"
            ),
            "r+b",
        ) as fh:
            content = fh.read()
            httpretty.register_uri(
                httpretty.GET,
                "https://training1.mdsol.com/RaveWebServices/studies/RWS_Training_Japan(PROD)/datasets/regular/SURGERY",
                status=200,
                body=content,
                content_type="text/xml"
            )
        # Now my test
        r = rwslib.RWSConnection("https://training1.mdsol.com")
        result = r.send_request(
            StudyDatasetRequest("RWS_Training_Japan", "PROD", formoid="SURGERY")
        )
        # these don't match as the encoding of the characters fails
        self.assertNotEqual(content.decode('utf-8'), result)

        class UTF8StudyDatasetRequest(StudyDatasetRequest):
            """
            Force the encoding of the response
            """
            def result(self, response):
                response.encoding = 'utf-8'
                return response.text

        result = r.send_request(
            UTF8StudyDatasetRequest("RWS_Training_Japan", "PROD", formoid="SURGERY")
        )
        # these match as the encoding enforcement makes it so
        self.assertEqual(content.decode('utf-8'), result)


if __name__ == "__main__":
    unittest.main()

