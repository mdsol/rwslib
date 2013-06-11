__author__ = 'isparks'

import unittest
import rwsobjects
import httpretty

class TestParseEnvironment(unittest.TestCase):
    """Test for extraction of environment"""
    def test_simple(self):
        env = rwsobjects.getEnvironmentFromNameAndProtocol('TEST (DEV)', 'TEST')
        self.assertEqual(env, 'DEV')

    def test_braces_in_name(self):
        env = rwsobjects.getEnvironmentFromNameAndProtocol('TEST (1) (ZZZ)', 'TEST (1)')
        self.assertEqual(env, 'ZZZ')

    def test_single_right_brace_in_name(self):
        env = rwsobjects.getEnvironmentFromNameAndProtocol('TEST :) (PROD)', 'TEST :)')
        self.assertEqual(env, 'PROD')

    def test_single_left_brace_in_name(self):
        env = rwsobjects.getEnvironmentFromNameAndProtocol('TEST :( (PROD)', 'TEST :(')
        self.assertEqual(env, 'PROD')


    def test_braces_tight_spaces(self):
        env = rwsobjects.getEnvironmentFromNameAndProtocol('TEST(99)(AUX)', 'TEST(99)')
        self.assertEqual(env, 'AUX')

    def test_no_env(self):
        """Note. This is probably not wanted behaviour but I am documenting here!
           What this is saying is that the study name is TEST(99) and there is no
           environment supplied.
        """
        env = rwsobjects.getEnvironmentFromNameAndProtocol('TEST(99)', 'TEST(99)')
        self.assertEqual(env, '')

class TestRWSErrorResponse(unittest.TestCase):
    """Test that RWSErrorResponse correctly reads an error response"""

    def test_parse(self):
        text = """<Response ReferenceNumber="0b47fe86-542f-4070-9e7d-16396a5ef08a"
    InboundODMFileOID="Not Supplied"
    IsTransactionSuccessful="0"
    ReasonCode="RWS00092"
    ErrorClientResponseMessage="CRF version not found">
    </Response>""".decode('utf-8')

        resp = rwsobjects.RWSErrorResponse(text)

        self.assertEqual(False, resp.istransactionsuccessful)
        self.assertEqual("CRF version not found", resp.errordescription)
        self.assertEqual("Not Supplied", resp.inboundodmfileoid)
        self.assertEqual("RWS00092", resp.reasoncode)
        self.assertEqual("0b47fe86-542f-4070-9e7d-16396a5ef08a", resp.referencenumber)

class TestRWSError(unittest.TestCase):
    """Test that RWSError correctly reads an error response"""

    def test_parse(self):
        text = """<?xml version="1.0" encoding="utf-8"?>
         <ODM xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata"
         FileType="Snapshot"
         CreationDateTime="2013-04-08T10:28:49.578-00:00"
         FileOID="4d13722a-ceb6-4419-a917-b6ad5d0bc30e"
         ODMVersion="1.3"
         mdsol:ErrorDescription="Incorrect login and password combination. [RWS00008]"
         xmlns="http://www.cdisc.org/ns/odm/v1.3" />""".decode('utf-8')

        err = rwsobjects.RWSError(text)

        self.assertEqual("1.3", err.ODMVersion)
        self.assertEqual("Snapshot", err.filetype)
        self.assertEqual("4d13722a-ceb6-4419-a917-b6ad5d0bc30e", err.fileoid)
        self.assertEqual("Incorrect login and password combination. [RWS00008]", err.errordescription)
        self.assertEqual("2013-04-08T10:28:49.578-00:00", err.creationdatetime)


class TestRWSResponse(unittest.TestCase):
    """Test that RWResponse correctly reads an RWS response"""

    def test_parse(self):
        text = """<Response ReferenceNumber="82e942b0-48e8-4cf4-b299-51e2b6a89a1b"
              InboundODMFileOID=""
              IsTransactionSuccessful="1"
              SuccessStatistics="Rave objects touched: Subjects=1; Folders=2; Forms=3; Fields=4; LogLines=5" NewRecords="">
    </Response>""".decode('utf-8')

        response = rwsobjects.RWSResponse(text)

        self.assertEqual("82e942b0-48e8-4cf4-b299-51e2b6a89a1b", response.referencenumber)
        self.assertEqual(True, response.istransactionsuccessful)
        self.assertEqual(1, response.subjects_touched)
        self.assertEqual(2, response.folders_touched)
        self.assertEqual(3, response.forms_touched)
        self.assertEqual(4, response.fields_touched)
        self.assertEqual(5, response.loglines_touched)






if __name__ == '__main__':
    unittest.main()
