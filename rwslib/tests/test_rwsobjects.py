# -*- coding: utf-8 -*-
__author__ = 'isparks'

import unittest
from rwslib import rwsobjects

class TestParse(unittest.TestCase):

    def test_parse_with_bom(self):
        """Test parser can throw away BOM"""
        text = u"""\xef\xbb\xbf<?xml version="1.0" encoding="utf-8"?><ODM/>"""
        self.assertEqual("ODM",rwsobjects.parseXMLString(text).tag)

    def test_parse_without_bom(self):
        """Test parser can throw away BOM"""
        text = u"""<?xml version="1.0" encoding="utf-8"?><ODM/>"""
        self.assertEqual("ODM",rwsobjects.parseXMLString(text).tag)

    def test_parse_empty_string(self):
        text = u""""""
        self.assertEqual("",rwsobjects.parseXMLString(text))


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
    </Response>"""

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
         xmlns="http://www.cdisc.org/ns/odm/v1.3" />"""

        err = rwsobjects.RWSError(text)

        self.assertEqual("1.3", err.ODMVersion)
        self.assertEqual("Snapshot", err.filetype)
        self.assertEqual("4d13722a-ceb6-4419-a917-b6ad5d0bc30e", err.fileoid)
        self.assertEqual("Incorrect login and password combination. [RWS00008]", err.errordescription)
        self.assertEqual("2013-04-08T10:28:49.578-00:00", err.creationdatetime)


class TestRWSResponse(unittest.TestCase):
    """Test that RWSResponse correctly reads an RWS response"""

    def test_parse(self):
        text = """<Response ReferenceNumber="82e942b0-48e8-4cf4-b299-51e2b6a89a1b"
              InboundODMFileOID=""
              IsTransactionSuccessful="1"
              SuccessStatistics="Rave objects touched: Subjects=1; Folders=2; Forms=3; Fields=4; LogLines=5" NewRecords="">
    </Response>"""

        response = rwsobjects.RWSResponse(text)

        self.assertEqual("82e942b0-48e8-4cf4-b299-51e2b6a89a1b", response.referencenumber)
        self.assertEqual(True, response.istransactionsuccessful)
        self.assertEqual(1, response.subjects_touched)
        self.assertEqual(2, response.folders_touched)
        self.assertEqual(3, response.forms_touched)
        self.assertEqual(4, response.fields_touched)
        self.assertEqual(5, response.loglines_touched)

class TestRWSSubjects(unittest.TestCase):
    """Test RWSSubjects"""

    def test_parse(self):
        """
        Parse a simple response
        """
        text = """<ODM xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.cdisc.org/ns/odm/v1.3" FileType="Snapshot" FileOID="0d2dcb32-16ca-4ab9-9917-c4b3eef2fb4a" CreationDateTime="2013-09-10T09:33:07.808-00:00" ODMVersion="1.3">
  <ClinicalData StudyOID="SIMPLESTUDY(TEST)" MetaDataVersionOID="1128">
    <SubjectData SubjectKey="1" mdsol:Overdue="No" mdsol:Touched="Yes" mdsol:Empty="No" mdsol:Incomplete="No" mdsol:NonConformant="No" mdsol:RequiresSecondPass="No" mdsol:RequiresReconciliation="No" mdsol:RequiresVerification="No" mdsol:Verified="No" mdsol:Frozen="No" mdsol:Locked="No" mdsol:RequiresReview="No" mdsol:PendingReview="No" mdsol:Reviewed="No" mdsol:RequiresAnswerQuery="No" mdsol:RequiresPendingCloseQuery="No" mdsol:RequiresCloseQuery="No" mdsol:StickyPlaced="No" mdsol:Signed="No" mdsol:SignatureCurrent="No" mdsol:RequiresTranslation="No" mdsol:RequiresCoding="No" mdsol:RequiresPendingAnswerQuery="No" mdsol:RequiresSignature="No" mdsol:ReadyForFreeze="No" mdsol:ReadyForLock="Yes">
      <SiteRef LocationOID="TESTSITE"/>
    </SubjectData>
  </ClinicalData>
  <ClinicalData StudyOID="SIMPLESTUDY(TEST)" MetaDataVersionOID="1128">
    <SubjectData SubjectKey="2">
      <SiteRef LocationOID="TESTSITE"/>
    </SubjectData>
  </ClinicalData>
  <ClinicalData StudyOID="SIMPLESTUDY(TEST)" MetaDataVersionOID="1128">
    <SubjectData SubjectKey="3" mdsol:Overdue="No" mdsol:Touched="Yes" mdsol:Empty="No" mdsol:Incomplete="Yes" mdsol:NonConformant="No" mdsol:RequiresSecondPass="No" mdsol:RequiresReconciliation="No" mdsol:RequiresVerification="No" mdsol:Verified="No" mdsol:Frozen="No" mdsol:Locked="No" mdsol:RequiresReview="No" mdsol:PendingReview="No" mdsol:Reviewed="No" mdsol:RequiresAnswerQuery="No" mdsol:RequiresPendingCloseQuery="No" mdsol:RequiresCloseQuery="No" mdsol:StickyPlaced="No" mdsol:Signed="No" mdsol:SignatureCurrent="No" mdsol:RequiresTranslation="No" mdsol:RequiresCoding="No" mdsol:RequiresPendingAnswerQuery="No" mdsol:RequiresSignature="No" mdsol:ReadyForFreeze="No" mdsol:ReadyForLock="Yes">
      <SiteRef LocationOID="TESTSITE"/>
    </SubjectData>
  </ClinicalData>
</ODM>"""

        subjects = rwsobjects.RWSSubjects(text)

        self.assertEqual("0d2dcb32-16ca-4ab9-9917-c4b3eef2fb4a", subjects.fileoid)
        self.assertEqual(3, len(subjects))
        self.assertEqual(True, subjects[0].touched)
        self.assertEqual(False, subjects[0].overdue)
        self.assertEqual(None, subjects[1].overdue)  # Example where status was not asked for.
        self.assertEqual(True, subjects[2].incomplete)
        self.assertEqual(text,str(subjects))

    def test_parse_no_uuid(self):
        """
        subject_name works when there is no SubjectKeyType
        """
        text = """<ODM xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.cdisc.org/ns/odm/v1.3" FileType="Snapshot" FileOID="0d2dcb32-16ca-4ab9-9917-c4b3eef2fb4a" CreationDateTime="2013-09-10T09:33:07.808-00:00" ODMVersion="1.3">
  <ClinicalData StudyOID="SIMPLESTUDY(TEST)" MetaDataVersionOID="1128">
    <SubjectData SubjectKey="1" mdsol:Overdue="No" mdsol:Touched="Yes" mdsol:Empty="No" mdsol:Incomplete="No" mdsol:NonConformant="No" mdsol:RequiresSecondPass="No" mdsol:RequiresReconciliation="No" mdsol:RequiresVerification="No" mdsol:Verified="No" mdsol:Frozen="No" mdsol:Locked="No" mdsol:RequiresReview="No" mdsol:PendingReview="No" mdsol:Reviewed="No" mdsol:RequiresAnswerQuery="No" mdsol:RequiresPendingCloseQuery="No" mdsol:RequiresCloseQuery="No" mdsol:StickyPlaced="No" mdsol:Signed="No" mdsol:SignatureCurrent="No" mdsol:RequiresTranslation="No" mdsol:RequiresCoding="No" mdsol:RequiresPendingAnswerQuery="No" mdsol:RequiresSignature="No" mdsol:ReadyForFreeze="No" mdsol:ReadyForLock="Yes">
      <SiteRef LocationOID="TESTSITE"/>
    </SubjectData>
  </ClinicalData>
  <ClinicalData StudyOID="SIMPLESTUDY(TEST)" MetaDataVersionOID="1128">
    <SubjectData SubjectKey="2">
      <SiteRef LocationOID="TESTSITE"/>
    </SubjectData>
  </ClinicalData>
  <ClinicalData StudyOID="SIMPLESTUDY(TEST)" MetaDataVersionOID="1128">
    <SubjectData SubjectKey="3" mdsol:Overdue="No" mdsol:Touched="Yes" mdsol:Empty="No" mdsol:Incomplete="Yes" mdsol:NonConformant="No" mdsol:RequiresSecondPass="No" mdsol:RequiresReconciliation="No" mdsol:RequiresVerification="No" mdsol:Verified="No" mdsol:Frozen="No" mdsol:Locked="No" mdsol:RequiresReview="No" mdsol:PendingReview="No" mdsol:Reviewed="No" mdsol:RequiresAnswerQuery="No" mdsol:RequiresPendingCloseQuery="No" mdsol:RequiresCloseQuery="No" mdsol:StickyPlaced="No" mdsol:Signed="No" mdsol:SignatureCurrent="No" mdsol:RequiresTranslation="No" mdsol:RequiresCoding="No" mdsol:RequiresPendingAnswerQuery="No" mdsol:RequiresSignature="No" mdsol:ReadyForFreeze="No" mdsol:ReadyForLock="Yes">
      <SiteRef LocationOID="TESTSITE"/>
    </SubjectData>
  </ClinicalData>
</ODM>"""

        subjects = rwsobjects.RWSSubjects(text)

        self.assertEqual("0d2dcb32-16ca-4ab9-9917-c4b3eef2fb4a", subjects.fileoid)
        self.assertEqual(3, len(subjects))
        self.assertEqual(True, subjects[0].touched)
        self.assertEqual(False, subjects[0].overdue)
        self.assertEqual(None, subjects[1].overdue) # Example where status was not asked for.
        self.assertEqual(0, len(subjects[1].links))    # Example where link was not asked for
        self.assertEqual(True, subjects[2].incomplete)
        self.assertEqual(text,str(subjects))
        self.assertEqual("1", subjects[0].subject_name)
        self.assertEqual("2", subjects[1].subject_name)
        self.assertEqual("3", subjects[2].subject_name)

    def test_parse_out_subject_key_where_uuid(self):
        """
        when there is a SubjectKeyType='SubjectUUID' then we return Subject ID consistently
        """
        text = """<ODM xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.cdisc.org/ns/odm/v1.3" FileType="Snapshot" FileOID="0d2dcb32-16ca-4ab9-9917-c4b3eef2fb4a" CreationDateTime="2013-09-10T09:33:07.808-00:00" ODMVersion="1.3">
  <ClinicalData StudyOID="SIMPLESTUDY(TEST)" MetaDataVersionOID="1128">
    <SubjectData SubjectKey="0A663F39" mdsol:SubjectName="1" mdsol:SubjectKeyType="SubjectUUID" mdsol:Overdue="No" mdsol:Touched="Yes" mdsol:Empty="No" mdsol:Incomplete="No" mdsol:NonConformant="No" mdsol:RequiresSecondPass="No" mdsol:RequiresReconciliation="No" mdsol:RequiresVerification="No" mdsol:Verified="No" mdsol:Frozen="No" mdsol:Locked="No" mdsol:RequiresReview="No" mdsol:PendingReview="No" mdsol:Reviewed="No" mdsol:RequiresAnswerQuery="No" mdsol:RequiresPendingCloseQuery="No" mdsol:RequiresCloseQuery="No" mdsol:StickyPlaced="No" mdsol:Signed="No" mdsol:SignatureCurrent="No" mdsol:RequiresTranslation="No" mdsol:RequiresCoding="No" mdsol:RequiresPendingAnswerQuery="No" mdsol:RequiresSignature="No" mdsol:ReadyForFreeze="No" mdsol:ReadyForLock="Yes">
      <SiteRef LocationOID="TESTSITE"/>
    </SubjectData>
  </ClinicalData>
  <ClinicalData StudyOID="SIMPLESTUDY(TEST)" MetaDataVersionOID="1128">
    <SubjectData SubjectKey="0076F9FE" mdsol:SubjectName="2" mdsol:SubjectKeyType="SubjectUUID">
      <SiteRef LocationOID="TESTSITE"/>
    </SubjectData>
  </ClinicalData>
  <ClinicalData StudyOID="SIMPLESTUDY(TEST)" MetaDataVersionOID="1128">
    <SubjectData SubjectKey="B8CFE69E" mdsol:SubjectName="3" mdsol:SubjectKeyType="SubjectUUID" mdsol:Overdue="No" mdsol:Touched="Yes" mdsol:Empty="No" mdsol:Incomplete="Yes" mdsol:NonConformant="No" mdsol:RequiresSecondPass="No" mdsol:RequiresReconciliation="No" mdsol:RequiresVerification="No" mdsol:Verified="No" mdsol:Frozen="No" mdsol:Locked="No" mdsol:RequiresReview="No" mdsol:PendingReview="No" mdsol:Reviewed="No" mdsol:RequiresAnswerQuery="No" mdsol:RequiresPendingCloseQuery="No" mdsol:RequiresCloseQuery="No" mdsol:StickyPlaced="No" mdsol:Signed="No" mdsol:SignatureCurrent="No" mdsol:RequiresTranslation="No" mdsol:RequiresCoding="No" mdsol:RequiresPendingAnswerQuery="No" mdsol:RequiresSignature="No" mdsol:ReadyForFreeze="No" mdsol:ReadyForLock="Yes">
      <SiteRef LocationOID="TESTSITE"/>
    </SubjectData>
  </ClinicalData>
</ODM>"""

        subjects = rwsobjects.RWSSubjects(text)

        self.assertEqual("0d2dcb32-16ca-4ab9-9917-c4b3eef2fb4a", subjects.fileoid)
        self.assertEqual(3, len(subjects))
        self.assertEqual(True, subjects[0].touched)
        self.assertEqual(False, subjects[0].overdue)
        self.assertEqual(None, subjects[1].overdue) #Example where status was not asked for.
        self.assertEqual(True, subjects[2].incomplete)
        self.assertEqual(text, str(subjects))
        self.assertEqual("1", subjects[0].subject_name)
        self.assertEqual("2", subjects[1].subject_name)
        self.assertEqual("3", subjects[2].subject_name)
        self.assertEqual("0A663F39", subjects[0].subjectkey)
        self.assertEqual("0076F9FE", subjects[1].subjectkey)
        self.assertEqual("B8CFE69E", subjects[2].subjectkey)

    def test_parse_with_links(self):
        """
        Populate subject.link with URL when provided
        """
        text = """<ODM xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.cdisc.org/ns/odm/v1.3" FileType="Snapshot" FileOID="0d2dcb32-16ca-4ab9-9917-c4b3eef2fb4a" CreationDateTime="2013-09-10T09:33:07.808-00:00" ODMVersion="1.3">
  <ClinicalData StudyOID="SIMPLESTUDY(TEST)" MetaDataVersionOID="1128">
    <SubjectData SubjectKey="0A663F39" mdsol:SubjectName="1" mdsol:SubjectKeyType="SubjectUUID" mdsol:Overdue="No" mdsol:Touched="Yes" mdsol:Empty="No" mdsol:Incomplete="No" mdsol:NonConformant="No" mdsol:RequiresSecondPass="No" mdsol:RequiresReconciliation="No" mdsol:RequiresVerification="No" mdsol:Verified="No" mdsol:Frozen="No" mdsol:Locked="No" mdsol:RequiresReview="No" mdsol:PendingReview="No" mdsol:Reviewed="No" mdsol:RequiresAnswerQuery="No" mdsol:RequiresPendingCloseQuery="No" mdsol:RequiresCloseQuery="No" mdsol:StickyPlaced="No" mdsol:Signed="No" mdsol:SignatureCurrent="No" mdsol:RequiresTranslation="No" mdsol:RequiresCoding="No" mdsol:RequiresPendingAnswerQuery="No" mdsol:RequiresSignature="No" mdsol:ReadyForFreeze="No" mdsol:ReadyForLock="Yes">
      <SiteRef LocationOID="TESTSITE"/>
      <mdsol:Link xlink:type="simple" xlink:href="http://innovate.mdsol.com/MedidataRAVE/HandleLink.aspx?page=SubjectPage.aspx?ID=1234" />
    </SubjectData>
  </ClinicalData>
  <ClinicalData StudyOID="SIMPLESTUDY(TEST)" MetaDataVersionOID="1128">
    <SubjectData SubjectKey="0076F9FE" mdsol:SubjectName="2" mdsol:SubjectKeyType="SubjectUUID">
      <SiteRef LocationOID="TESTSITE"/>
      <mdsol:Link xlink:type="simple" xlink:href="http://innovate.mdsol.com/MedidataRAVE/HandleLink.aspx?page=SubjectPage.aspx?ID=5678" />
    </SubjectData>
  </ClinicalData>
  <ClinicalData StudyOID="SIMPLESTUDY(TEST)" MetaDataVersionOID="1128">
    <SubjectData SubjectKey="B8CFE69E" mdsol:SubjectName="3" mdsol:SubjectKeyType="SubjectUUID" mdsol:Overdue="No" mdsol:Touched="Yes" mdsol:Empty="No" mdsol:Incomplete="Yes" mdsol:NonConformant="No" mdsol:RequiresSecondPass="No" mdsol:RequiresReconciliation="No" mdsol:RequiresVerification="No" mdsol:Verified="No" mdsol:Frozen="No" mdsol:Locked="No" mdsol:RequiresReview="No" mdsol:PendingReview="No" mdsol:Reviewed="No" mdsol:RequiresAnswerQuery="No" mdsol:RequiresPendingCloseQuery="No" mdsol:RequiresCloseQuery="No" mdsol:StickyPlaced="No" mdsol:Signed="No" mdsol:SignatureCurrent="No" mdsol:RequiresTranslation="No" mdsol:RequiresCoding="No" mdsol:RequiresPendingAnswerQuery="No" mdsol:RequiresSignature="No" mdsol:ReadyForFreeze="No" mdsol:ReadyForLock="Yes">
      <SiteRef LocationOID="TESTSITE"/>
      <mdsol:Link xlink:type="simple" xlink:href="http://innovate.mdsol.com/MedidataRAVE/HandleLink.aspx?page=SubjectPage.aspx?ID=9012" />
    </SubjectData>
  </ClinicalData>
</ODM>"""

        subjects = rwsobjects.RWSSubjects(text)

        self.assertEqual("http://innovate.mdsol.com/MedidataRAVE/HandleLink.aspx?page=SubjectPage.aspx?ID=1234", subjects[0].links[0])
        self.assertEqual("http://innovate.mdsol.com/MedidataRAVE/HandleLink.aspx?page=SubjectPage.aspx?ID=5678", subjects[1].links[0])
        self.assertEqual("http://innovate.mdsol.com/MedidataRAVE/HandleLink.aspx?page=SubjectPage.aspx?ID=9012", subjects[2].links[0])


class TestMetaDataVersions(unittest.TestCase):
    """Test MetaDataVersions"""

    def test_parse(self):
        text = u"""<ODM ODMVersion="1.3" Granularity="Metadata" FileType="Snapshot" FileOID="d26b4d33-376d-4037-9747-684411190179" CreationDateTime=" 2013-04-08T01:29:13 " xmlns="http://www.cdisc.org/ns/odm/v1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata">
        <Study OID="IANTEST">
            <GlobalVariables>
                <StudyName>IANTEST</StudyName>
                <StudyDescription></StudyDescription>
                <ProtocolName>IANTEST</ProtocolName>
            </GlobalVariables>
            <MetaDataVersion OID="1203" Name="Webservice Outbound" />
            <MetaDataVersion OID="1195" Name="Demo_Draft1" />
            <MetaDataVersion OID="1165" Name="Initial" />
        </Study>
    </ODM>"""

        metadata = rwsobjects.RWSStudyMetadataVersions(text)

        self.assertEqual("1.3", metadata.ODMVersion)
        self.assertEqual("IANTEST", metadata.study.oid)
        self.assertEqual(3, len(metadata))
        self.assertEqual("Demo_Draft1",metadata[1].name)
        self.assertEqual("1165",metadata[2].oid)

class TestRWSPostResponse(unittest.TestCase):
    def test_parse(self):
        text = """<Response ReferenceNumber="82e942b0-48e8-4cf4-b299-51e2b6a89a1b"
              InboundODMFileOID=""
              IsTransactionSuccessful="1"
              SuccessStatistics="Rave objects touched: Subjects=0; Folders=0; Forms=0; Fields=0; LogLines=0" NewRecords=""
              SubjectNumberInStudy="1103" SubjectNumberInStudySite="55">
    </Response>"""

        parsed = rwsobjects.RWSPostResponse(text)

        self.assertEqual(True, parsed.istransactionsuccessful)
        self.assertEqual(1103, parsed.subjects_in_study)
        self.assertEqual(55, parsed.subjects_in_study_site)

    def test_bad_success_stats(self):
        """Test error when statistics contain info we don't recognize"""
        text = """<Response ReferenceNumber="82e942b0-48e8-4cf4-b299-51e2b6a89a1b"
              InboundODMFileOID=""
              IsTransactionSuccessful="1"
              SuccessStatistics="Rave objects touched: Subjects=0; Folders=0; Forms=0; Unknown=10; Fields=0; LogLines=0"
              NewRecords=""
              SubjectNumberInStudy="1103" SubjectNumberInStudySite="55">
    </Response>"""

        def doparse():
            parsed = rwsobjects.RWSPostResponse(text)

        self.assertRaises(KeyError,doparse)


class TestRWSPostErrorResponse(unittest.TestCase):
    def test_parse(self):
        text = """<Response
        ReferenceNumber="5b1fa9a3-0cf3-46b6-8304-37c2e3b7d04f5"
        InboundODMFileOID="1"
        IsTransactionSuccessful = "0"
        ReasonCode="RWS00024"
        ErrorOriginLocation="/ODM/ClinicalData[1]/SubjectData[1]"
        SuccessStatistics="Rave objects touched: Subjects=0; Folders=0; Forms=0; Fields=0; LogLines=0"
        ErrorClientResponseMessage="Subject already exists.">
        </Response>
        """

        parsed = rwsobjects.RWSPostErrorResponse(text)
        self.assertEqual("5b1fa9a3-0cf3-46b6-8304-37c2e3b7d04f5", parsed.referencenumber)
        self.assertEqual("Subject already exists.", parsed.error_client_response_message)
        self.assertEqual("/ODM/ClinicalData[1]/SubjectData[1]", parsed.error_origin_location)


class TestRWSStudies(unittest.TestCase):
    def test_parse(self):
        text = """<ODM FileType="Snapshot" FileOID="767a1f8b-7b72-4d12-adbe-37d4d62ba75e"
         CreationDateTime="2013-04-08T10:02:17.781-00:00"
         ODMVersion="1.3"
         xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata"
         xmlns:xlink="http://www.w3.org/1999/xlink"
         xmlns="http://www.cdisc.org/ns/odm/v1.3">
         <Study OID="Fixitol(Dev)">
            <GlobalVariables>
                  <StudyName>Fixitol (Dev)</StudyName>
                  <StudyDescription/>
                  <ProtocolName>Fixitol</ProtocolName>
            </GlobalVariables>
         </Study>
         <Study OID="IANTEST(Prod)">
            <GlobalVariables>
                  <StudyName>IANTEST</StudyName>
                  <StudyDescription/>
                  <ProtocolName>IANTEST</ProtocolName>
            </GlobalVariables>
         </Study>
    </ODM>"""
        parsed = rwsobjects.RWSStudies(text)
        self.assertEqual("1.3",parsed.ODMVersion)
        self.assertEqual(2,len(parsed))
        self.assertEqual(False,parsed[0].isProd())
        self.assertEqual(True,parsed[1].isProd())


class TestUtils(unittest.TestCase):
    def test_parse(self):
        text = """<ODM FileType="Snapshot" FileOID="767a1f8b-7b72-4d12-adbe-37d4d62ba75e"
         CreationDateTime="2013-04-08T10:02:17.781-00:00"
         ODMVersion="1.3"
         xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata"
         xmlns:xlink="http://www.w3.org/1999/xlink"
         xmlns="http://www.cdisc.org/ns/odm/v1.3">
         <Study OID="Fixitol(Dev)">
            <GlobalVariables>
                  <StudyName>Fixitol (Dev)</StudyName>
                  <StudyDescription/>
                  <ProtocolName>Fixitol</ProtocolName>
            </GlobalVariables>
         </Study>
         <Study OID="IANTEST(Prod)">
            <GlobalVariables>
                  <StudyName>IANTEST</StudyName>
                  <StudyDescription/>
                  <ProtocolName>IANTEST</ProtocolName>
            </GlobalVariables>
         </Study>
    </ODM>"""
        parsed = rwsobjects.RWSStudies(text)
        self.assertEqual("1.3",parsed.ODMVersion)
        self.assertEqual(2,len(parsed))
        self.assertEqual(False,parsed[0].isProd())
        self.assertEqual(True,parsed[1].isProd())



if __name__ == '__main__':
    unittest.main()
