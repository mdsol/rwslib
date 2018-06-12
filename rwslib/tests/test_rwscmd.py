# -*- coding: utf-8 -*-

__author__ = 'anewbigging'

import unittest

import httpretty
from click.testing import CliRunner

from rwslib.extras.rwscmd import rwscmd


class TestRWSCMD(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    @httpretty.activate
    def test_version(self):
        httpretty.register_uri(
            httpretty.GET, "https://innovate.mdsol.com/RaveWebServices/version",
            status=200,
            body='1.0.0')

        result = self.runner.invoke(rwscmd.rws, ['https://innovate.mdsol.com', 'version'], input="\n\n")
        self.assertIn('1.0.0', result.output)
        self.assertEqual(result.exit_code, 0)

    @httpretty.activate
    def test_data_studies(self):
        httpretty.register_uri(
            httpretty.GET, "https://innovate.mdsol.com/RaveWebServices/studies",
            status=200,
            body="""<ODM FileType="Snapshot" FileOID="" CreationDateTime="" ODMVersion="1.3"
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
</ODM>""")

        result = self.runner.invoke(rwscmd.rws, ['https://innovate.mdsol.com', 'data'],
                                    input="defuser\npassword\n")
        self.assertIn('Lab Test\nMediflex', result.output)
        self.assertEqual(result.exit_code, 0)

    @httpretty.activate
    def test_data_subjects(self):
        httpretty.register_uri(
            httpretty.GET, "https://innovate.mdsol.com/RaveWebServices/studies/Mediflex(Dev)/subjects",
            status=200,
            body="""<ODM FileType="Snapshot" FileOID="97794848-9e60-4d7c-a8f9-423ea8d08556" CreationDateTime="2016-03-07T20:59:34.175-00:00" ODMVersion="1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.cdisc.org/ns/odm/v1.3">
  <ClinicalData StudyOID="Mediflex(Dev)" MetaDataVersionOID="23">
    <SubjectData SubjectKey="0004-bbc-003" mdsol:SubjectKeyType="SubjectName">
      <SiteRef LocationOID="MDSOL" />
    </SubjectData>
  </ClinicalData>
  <ClinicalData StudyOID="Mediflex(Dev)" MetaDataVersionOID="23">
    <SubjectData SubjectKey="001 atn" mdsol:SubjectKeyType="SubjectName">
      <SiteRef LocationOID="MDSOL" />
    </SubjectData>
  </ClinicalData>
    </ODM>""")

        result = self.runner.invoke(rwscmd.rws, ['https://innovate.mdsol.com', 'data', 'Mediflex', 'Dev'],
                                    input="defuser\npassword\n")
        self.assertIn('0004-bbc-003\n001 atn', result.output)
        self.assertEqual(result.exit_code, 0)

    @httpretty.activate
    def test_data_subject_data(self):
        odm = """<ODM xmlns="http://www.cdisc.org/ns/odm/v1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata" ODMVersion="1.3" FileType="Transactional" FileOID="7b63fdca-6868-4bdf-9b41-66835c881c38" CreationDateTime="2016-03-01T10:52:02.000-00:00">
  <ClinicalData StudyOID="Fixitol(Dev)" MetaDataVersionOID="158">
    <SubjectData SubjectKey="c01343a3-d3d5-4005-9ea3-93f87b038d62" mdsol:SubjectKeyType="SubjectUUID" mdsol:SubjectName="001">
      <SiteRef LocationOID="0100"/>
      <StudyEventData StudyEventOID="SCRN">
        <FormData FormOID="PTVISIT" FormRepeatKey="1">
          <ItemGroupData ItemGroupOID="PTVISIT">
            <ItemData ItemOID="PTVISIT.VS" Value=""/>
          </ItemGroupData>
        </FormData>
      </StudyEventData>
    </SubjectData>
  </ClinicalData>
</ODM>"""

        # path = "datasets/rwscmd_getdata.odm?StudyOID=Fixitol(Dev)&SubjectKey=001&IncludeIDs=0&IncludeValues=0"
        path = "datasets/rwscmd_getdata.odm"

        httpretty.register_uri(
            httpretty.GET,
            "https://innovate.mdsol.com/RaveWebServices/" + path,
            # "https://innovate.mdsol.com/RaveWebServices",
            status=200,
            body=odm)

        result = self.runner.invoke(rwscmd.rws, ['https://innovate.mdsol.com', 'data', 'Fixitol', 'Dev', '001'],
                                    input="defuser\npassword\n")

        self.assertIn(odm, result.output)
        self.assertEqual(result.exit_code, 0)

    @httpretty.activate
    def test_post_data(self):
        post_odm = """<ODM xmlns="http://www.cdisc.org/ns/odm/v1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata" ODMVersion="1.3" FileType="Transactional" FileOID="7b63fdca-6868-4bdf-9b41-66835c881c38" CreationDateTime="2016-03-01T10:52:02.000-00:00">
  <ClinicalData StudyOID="Fixitol(Dev)" MetaDataVersionOID="158">
    <SubjectData SubjectKey="c01343a3-d3d5-4005-9ea3-93f87b038d62" mdsol:SubjectKeyType="SubjectUUID" mdsol:SubjectName="001">
      <SiteRef LocationOID="0100"/>
      <StudyEventData StudyEventOID="SCRN">
        <FormData FormOID="PTVISIT" FormRepeatKey="1">
          <ItemGroupData ItemGroupOID="PTVISIT">
            <ItemData ItemOID="PTVISIT.VS" Value="10 MAR 2016"/>
          </ItemGroupData>
        </FormData>
      </StudyEventData>
    </SubjectData>
  </ClinicalData>
</ODM>"""

        response_content = """<Response ReferenceNumber="82e942b0-48e8-4cf4-b299-51e2b6a89a1b"
              InboundODMFileOID=""
              IsTransactionSuccessful="1"
              SuccessStatistics="Rave objects touched: Subjects=0; Folders=0; Forms=0; Fields=1; LogLines=0" NewRecords=""
              SubjectNumberInStudy="1103" SubjectNumberInStudySite="55">
        </Response>"""

        httpretty.register_uri(
            httpretty.POST, "https://innovate.mdsol.com/RaveWebServices/webservice.aspx?PostODMClinicalData",
            status=200,
            body=response_content)

        with self.runner.isolated_filesystem():
            with open('odm.xml', 'w') as odm:
                odm.write(post_odm)
            result = self.runner.invoke(rwscmd.rws, ['--raw', 'https://innovate.mdsol.com', 'post', 'odm.xml'],
                                        input="defuser\npassword\n")
            self.assertIn(response_content, result.output)
            self.assertEqual(result.exit_code, 0)

    @httpretty.activate
    def test_direct(self):
        httpretty.register_uri(
            httpretty.GET, "https://innovate.mdsol.com/RaveWebServices/request?oid=1",
            status=200,
            body='<xml/>')

        result = self.runner.invoke(rwscmd.rws, ['https://innovate.mdsol.com', 'direct', 'request?oid=1'],
                                    input="defuser\npassword\n")
        self.assertIn('<xml/>', result.output)
        self.assertEqual(result.exit_code, 0)

    @httpretty.activate
    def test_metadata(self):
        httpretty.register_uri(
            httpretty.GET, "https://innovate.mdsol.com/RaveWebServices/metadata/studies",
            status=200,
            body="""<ODM FileType="Snapshot" FileOID="" CreationDateTime="" ODMVersion="1.3"
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
</ODM>""")

        result = self.runner.invoke(rwscmd.rws, ['https://innovate.mdsol.com', 'metadata'],
                                    input="defuser\npassword\n")
        self.assertIn('Lab Test\nMediflex', result.output)
        self.assertEqual(result.exit_code, 0)

    @httpretty.activate
    def test_metadata_versions(self):
        httpretty.register_uri(
            httpretty.GET, "https://innovate.mdsol.com/RaveWebServices/metadata/studies/Fixitol/versions",
            status=200,
            body="""<ODM ODMVersion="1.3" Granularity="Metadata" FileType="Snapshot" FileOID="d26b4d33-376d-4037-9747-684411190179" CreationDateTime=" 2013-04-08T01:29:13 " xmlns="http://www.cdisc.org/ns/odm/v1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata">
        <Study OID="Fixitol">
            <GlobalVariables>
                <StudyName>Fixitol</StudyName>
                <StudyDescription></StudyDescription>
                <ProtocolName>Fixitol</ProtocolName>
            </GlobalVariables>
            <MetaDataVersion OID="1203" Name="Webservice Outbound" />
            <MetaDataVersion OID="1195" Name="JC_Demo_Draft1" />
            <MetaDataVersion OID="1165" Name="Initial" />
        </Study>
    </ODM>""")

        result = self.runner.invoke(rwscmd.rws, ['https://innovate.mdsol.com', 'metadata', 'Fixitol'],
                                    input="defuser\npassword\n")
        self.assertIn('1203\n1195\n1165', result.output)
        self.assertEqual(result.exit_code, 0)

    @httpretty.activate
    def test_metadata_drafts(self):
        httpretty.register_uri(
            httpretty.GET, "https://innovate.mdsol.com/RaveWebServices/metadata/studies/Fixitol/drafts",
            status=200,
            body="""<ODM ODMVersion="1.3" Granularity="Metadata" FileType="Snapshot" FileOID="d26b4d33-376d-4037-9747-684411190179" CreationDateTime=" 2013-04-08T01:29:13 " xmlns="http://www.cdisc.org/ns/odm/v1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata">
        <Study OID="Fixitol">
            <GlobalVariables>
                <StudyName>Fixitol</StudyName>
                <StudyDescription></StudyDescription>
                <ProtocolName>Fixitol</ProtocolName>
            </GlobalVariables>
            <MetaDataVersion OID="1203" Name="Webservice Outbound" />
            <MetaDataVersion OID="1195" Name="JC_Demo_Draft1" />
            <MetaDataVersion OID="1165" Name="Initial" />
        </Study>
    </ODM>""")

        result = self.runner.invoke(rwscmd.rws, ['https://innovate.mdsol.com', 'metadata', '--drafts', 'Fixitol'],
                                    input="defuser\npassword\n")
        self.assertIn('1203\n1195\n1165', result.output)
        self.assertEqual(result.exit_code, 0)

    @httpretty.activate
    def test_metadata_version(self):
        odm = """<ODM FileType="Snapshot" FileOID="767a1f8b-7b72-4d12-adbe-37d4d62ba75e"
         CreationDateTime="2013-04-08T10:02:17.781-00:00"
         ODMVersion="1.3"
         xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata"
         xmlns:xlink="http://www.w3.org/1999/xlink"
         xmlns="http://www.cdisc.org/ns/odm/v1.3">
         <Study OID="Fixitol">
            <GlobalVariables>
                  <StudyName>Fixitol</StudyName>
                  <StudyDescription/>
                  <ProtocolName>Fixitol</ProtocolName>
            </GlobalVariables>
         </Study>
        """

        httpretty.register_uri(
            httpretty.GET, "https://innovate.mdsol.com/RaveWebServices/metadata/studies/Fixitol/versions/1165",
            status=200,
            body=odm)

        result = self.runner.invoke(rwscmd.rws, ['https://innovate.mdsol.com', 'metadata', 'Fixitol', '1165'],
                                    input="defuser\npassword\n")
        self.assertIn(odm, result.output)
        self.assertEqual(result.exit_code, 0)


class TestAutofill(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

        self.odm_metadata = """<ODM FileType="Snapshot" Granularity="Metadata" CreationDateTime="2016-02-29T13:47:23.654-00:00" FileOID="d460fc96-4f08-445f-89b1-0182e8e810c1" ODMVersion="1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata" xmlns="http://www.cdisc.org/ns/odm/v1.3">
  <Study OID="Test">
    <GlobalVariables>
      <StudyName>Test</StudyName>
      <StudyDescription></StudyDescription>
      <ProtocolName>Test</ProtocolName>
    </GlobalVariables>
    <BasicDefinitions/>
    <MetaDataVersion OID="1" Name="Metadata version 1">
      <ItemDef OID="VSDT" Name="VSDT" DataType="date" mdsol:DateTimeFormat="dd MMM yyyy" mdsol:VariableOID="VSDT" mdsol:Active="Yes" mdsol:ControlType="DateTime" mdsol:SourceDocument="Yes" mdsol:SASLabel="Visit Date" mdsol:QueryFutureDate="Yes" mdsol:Visible="Yes" mdsol:QueryNonConformance="Yes" mdsol:CanSetStudyEventDate="Yes" />
      <ItemDef OID="TIME" Name="TIME" DataType="time" mdsol:DateTimeFormat="HH:nn:ss" mdsol:VariableOID="TIME" mdsol:Active="Yes" mdsol:ControlType="DateTime" mdsol:SourceDocument="Yes" mdsol:SASLabel="Time" mdsol:QueryFutureDate="Yes" mdsol:Visible="Yes" mdsol:QueryNonConformance="Yes" mdsol:CanSetStudyEventDate="No" />
      <ItemDef OID="VSNUM" Name="VSNUM" DataType="integer" mdsol:VariableOID="VSNUM" Length="2" mdsol:Active="Yes" mdsol:ControlType="DropDownList" mdsol:SourceDocument="Yes" mdsol:SASLabel="Follow Up Visit" mdsol:Visible="Yes" mdsol:QueryNonConformance="Yes" />
      <ItemDef OID="SAE" Name="SAE" DataType="text" mdsol:VariableOID="SAE" Length="200" mdsol:Active="Yes" mdsol:ControlType="LongText" mdsol:SourceDocument="Yes" mdsol:SASLabel="eSAE Desription" mdsol:Visible="Yes" mdsol:QueryNonConformance="Yes" />
      <ItemDef OID="YN" Name="YN" DataType="integer" mdsol:VariableOID="YN" Length="1" mdsol:Active="Yes" mdsol:ControlType="DropDownList" mdsol:SourceDocument="Yes" mdsol:SASLabel="Subject Received Dose" mdsol:Visible="Yes" mdsol:QueryNonConformance="Yes">
        <CodeListRef CodeListOID="YES_NO_UNKNOWN" />
      </ItemDef>
      <CodeList OID="YES_NO_UNKNOWN" Name="YES_NO_UNKNOWN" DataType="integer">
        <CodeListItem CodedValue="0" mdsol:OrderNumber="1" />
        <CodeListItem CodedValue="1" mdsol:OrderNumber="2" />
        <CodeListItem CodedValue="97" mdsol:OrderNumber="3" />
      </CodeList>
    </MetaDataVersion>
  </Study>
</ODM>
"""

        self.odm_empty = """<ODM xmlns="http://www.cdisc.org/ns/odm/v1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata" ODMVersion="1.3" FileType="Transactional" FileOID="c3f15f2d-eb69-42e6-bed4-811bff27ebf9" CreationDateTime="2016-03-02T09:27:14.000-00:00">
  <ClinicalData StudyOID="Test(Prod)" MetaDataVersionOID="1">
    <SubjectData SubjectKey="9e15f698-327e-4e9c-8ed5-8be9b27b67b0" mdsol:SubjectKeyType="SubjectUUID" mdsol:SubjectName="001">
      <SiteRef LocationOID="0100"/>
      <StudyEventData StudyEventOID="SCRN">
        <FormData FormOID="FORM1" FormRepeatKey="1">
          <ItemGroupData ItemGroupOID="FORM1">
            <ItemData ItemOID="YN" Value=""/>
          </ItemGroupData>
        </FormData>
      </StudyEventData>
    </SubjectData>
  </ClinicalData>
</ODM>"""

        self.path = "datasets/rwscmd_getdata.odm"

        self.response_content = """<Response ReferenceNumber="82e942b0-48e8-4cf4-b299-51e2b6a89a1b"
              InboundODMFileOID=""
              IsTransactionSuccessful="1"
              SuccessStatistics="Rave objects touched: Subjects=0; Folders=0; Forms=0; Fields=1; LogLines=0" NewRecords=""
              SubjectNumberInStudy="1103" SubjectNumberInStudySite="55">
        </Response>"""

        # NOTE: HTTPretty is not supported on Python3, need to migrate this (get weird breakages in Travis)
        httpretty.enable()

        httpretty.register_uri(
            httpretty.GET, "https://innovate.mdsol.com/RaveWebServices/metadata/studies/Test/versions/1",
            status=200,
            body=self.odm_metadata)

        httpretty.register_uri(
            httpretty.GET, "https://innovate.mdsol.com/RaveWebServices/" + self.path,
            status=200,
            body=self.odm_empty)

        httpretty.register_uri(
            httpretty.POST, "https://innovate.mdsol.com/RaveWebServices/webservice.aspx?PostODMClinicalData",
            status=200,
            body=self.response_content)

    def test_autofill(self):
        result = self.runner.invoke(rwscmd.rws,
                                    ["--verbose", 'https://innovate.mdsol.com', 'autofill', 'Test', 'Prod', '001'],
                                    input="defuser\npassword\n")
        output = result.output
        self.assertIn("Step 1\nGetting data list", output)
        self.assertIn("Getting metadata version 1", output)
        self.assertIn("Step 10\nGetting data list", output)
        self.assertIn("Generating data", output)
        self.assertEqual(10, output.count("Generating data"))
        self.assertNotIn("Step 11", result.output)
        self.assertEqual(result.exit_code, 0)

    def test_autofill_steps(self):
        result = self.runner.invoke(rwscmd.rws,
                                    ['--verbose', 'https://innovate.mdsol.com', 'autofill', '--steps', '1',
                                     'Test', 'Prod', '001'],
                                    input="defuser\npassword\n")

        self.assertIn("Step 1\nGetting data list", result.output)
        self.assertIn("Getting metadata version 1\n", result.output)
        self.assertIn("Generating data", result.output)
        self.assertNotIn("Step 2", result.output)
        self.assertEqual(result.exit_code, 0)

    def test_autofill_no_data(self):
        odm = """
        <ODM xmlns="http://www.cdisc.org/ns/odm/v1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata" ODMVersion="1.3" FileType="Transactional" FileOID="c3f15f2d-eb69-42e6-bed4-811bff27ebf9" CreationDateTime="2016-03-02T09:27:14.000-00:00">
        </ODM>"""

        httpretty.register_uri(
            httpretty.GET, "https://innovate.mdsol.com/RaveWebServices/" + self.path,
            status=200,
            body=odm)

        result = self.runner.invoke(rwscmd.rws,
                                    ['--verbose', 'https://innovate.mdsol.com', 'autofill', 'Test', 'Prod', '001'],
                                    input="defuser\npassword\n")
        self.assertIn("Step 1\nGetting data list\n", result.output)
        self.assertIn("No data found", result.output)
        self.assertNotIn("Generating data", result.output)
        self.assertEqual(result.exit_code, 0)

    def test_autofill_fixed(self):
        with self.runner.isolated_filesystem():
            with open('fixed.txt', 'w') as f:
                f.write("YN,99")

            result = self.runner.invoke(rwscmd.rws,
                                        ['--verbose', 'https://innovate.mdsol.com', 'autofill', '--steps', '1',
                                         '--fixed', 'fixed.txt', 'Test', 'Prod', '001'],
                                        input=u"defuser\npassword\n", catch_exceptions=False)

        self.assertFalse(result.exception)
        self.assertIn("Step 1\nGetting data list", result.output)
        self.assertIn("Getting metadata version 1", result.output)
        self.assertIn("Generating data", result.output)
        self.assertIn('Fixing YN to value: 99', result.output)
        self.assertNotIn("Step 2", result.output)
        self.assertEqual(result.exit_code, 0)

    def test_autofill_metadata(self):
        with self.runner.isolated_filesystem():
            with open('odm.xml', 'w') as f:
                f.write(self.odm_metadata)

            result = self.runner.invoke(rwscmd.rws,
                                        ['--verbose', 'https://innovate.mdsol.com', 'autofill', '--steps', '1',
                                         '--metadata', 'odm.xml', 'Test', 'Prod', '001'],
                                        input=u"defuser\npassword\n", catch_exceptions=False)
        self.assertFalse(result.exception)
        self.assertIn("Step 1\nGetting data list", result.output)
        self.assertIn("Generating data", result.output)
        self.assertNotIn("Step 2", result.output)
        self.assertEqual(result.exit_code, 0)


if __name__ == '__main__':
    unittest.main()
