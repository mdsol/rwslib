# -*- coding: utf-8 -*-

__author__ = 'anewbigging'

from rwslib.extras.rwscmd import data_scrambler
from rwslib.extras.rwscmd.odmutils import E_ODM, A_ODM
import unittest
import datetime
from lxml import etree
from six import string_types

class TestDuckTyping(unittest.TestCase):
    def setUp(self):
        self.values = {
            0: 'int',
            1: 'int',
            -1: 'int',
            '1': 'int',
            '1.0': 'float',
            1.1: 'float',
            'a': 'string',
            '10 MAR 2016': 'date',
            'MAR 2016': 'date',
            '2016': 'date',
            '10 03 2016': 'date',
            '03 2016': 'date',
            '10/MAR/2016': 'date',
            'MAR/2016': 'date',
            '10/03/2016': 'date',
            '03/2016': 'date',
            '10 31 2016': 'string',  # TODO:  check if this is valid Rave date format
            '9999': 'int',
            '16': 'int',
            'MAR': 'string',
            '20:45:23': 'time',
            '20:45': 'time',
            '10:45:23': 'time',
            '10:45': 'time',
            '10:45:23 AM': 'time',
            '10:45 PM': 'time'
        }


    def test_ducktype(self):
        """Test duck typing integers"""
        for value, expected_type in self.values.items():
            rave_type, _ = data_scrambler.typeof_rave_data(value)
            self.assertEqual(expected_type, rave_type,
                            msg='{0} should be of type {1} not {2}'.format(value, expected_type, rave_type))


class TestBasicScrambling(unittest.TestCase):
    def setUp(self):
        self.scr = data_scrambler.Scramble()

    def test_scramble_int(self):
        """Test scrambling integers"""
        i = self.scr.scramble_int(5)
        self.assertEqual(i, str(int(i)))

    def test_scramble_float(self):
        """Test scrambling floats"""
        i = self.scr.scramble_float(5, 2)
        self.assertIsInstance(float(i), float)
        i = self.scr.scramble_float(5, 0)
        self.assertIsInstance(float(i), float)

    def test_scramble_strings(self):
        """Test scrambling strings"""
        i = self.scr.scramble_string(4)
        self.assertEqual(len(i), 4)
        i = self.scr.scramble_string(200)
        self.assertIsInstance(i, string_types)

    def test_scramble_date(self):
        """Test scrambling dates"""
        dt = self.scr.scramble_date('10 MAR 2016')
        self.assertTrue(datetime.datetime.strptime(dt, '%d %b %Y'))
        dt = self.scr.scramble_date('MAR 2016', '%b %Y')
        self.assertTrue(datetime.datetime.strptime(dt, '%b %Y'))

    def test_scramble_time(self):
        """Test scrambling times"""
        dt = self.scr.scramble_time('18:12:14')
        self.assertTrue(datetime.datetime.strptime(dt, '%H:%M:%S'))
        dt = self.scr.scramble_time( '%H:%M')
        self.assertTrue(datetime.datetime.strptime(dt, '%H:%M'))

class TestDuckTypeScrambling(unittest.TestCase):
    def setUp(self):
        self.scr = data_scrambler.Scramble()

    def test_scramble_int(self):
        """Test scrambling integers"""
        i = self.scr.scramble_value('12345')
        self.assertEqual(i, str(int(i)))

    def test_scramble_float(self):
        """Test scrambling floats"""
        i = self.scr.scramble_value('123.45')
        self.assertIsInstance(float(i), float)
        i = self.scr.scramble_value('12345')
        self.assertIsInstance(float(i), float)

    def test_scramble_strings(self):
        """Test scrambling strings"""
        s = 'asdf'
        i = self.scr.scramble_value(s)
        self.assertEqual(len(s), len(i))
        self.assertNotEqual(s, i)
        s = 'This is a large string to test scrambling of large strings'
        i = self.scr.scramble_value(s)
        self.assertNotEqual(s, i)

    def test_scramble_date(self):
        """Test scrambling dates"""
        dt = self.scr.scramble_value('10 MAR 2016')
        self.assertTrue(datetime.datetime.strptime(dt, '%d %b %Y'))
        dt = self.scr.scramble_value('MAR 2016')
        self.assertTrue(datetime.datetime.strptime(dt, '%b %Y'))

    def test_scramble_time(self):
        """Test scrambling times"""
        dt = self.scr.scramble_value('18:12:14')
        self.assertTrue(datetime.datetime.strptime(dt, '%H:%M:%S'))
        dt = self.scr.scramble_value('18:12')
        self.assertTrue(datetime.datetime.strptime(dt, '%H:%M'))

class TestScramblingWithMetadata(unittest.TestCase):
    def setUp(self):
        metadata = """
<ODM FileType="Snapshot" Granularity="Metadata" CreationDateTime="2016-02-29T13:47:23.654-00:00" FileOID="d460fc96-4f08-445f-89b1-0182e8e810c1" ODMVersion="1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata" xmlns="http://www.cdisc.org/ns/odm/v1.3">
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
        self.scr = data_scrambler.Scramble(metadata=metadata)

    def test_scramble_item_data(self):
        """Test scrambling using metadata"""
        dt = self.scr.scramble_itemdata('VSDT', '')
        self.assertTrue(datetime.datetime.strptime(dt, '%d %b %Y'))

        tm = self.scr.scramble_itemdata('TIME', '')
        self.assertTrue(datetime.datetime.strptime(tm, '%H:%M:%S'))

        st = self.scr.scramble_itemdata('SAE', '')
        self.assertNotEqual(str, st)

        cd = self.scr.scramble_itemdata('YN', '')
        self.assertIn(cd, ['0','1','97'])


    def test_fill_empty(self):
        """Test filling empty values in ODM document"""
        odm = """
<ODM xmlns="http://www.cdisc.org/ns/odm/v1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata" ODMVersion="1.3" FileType="Transactional" FileOID="c3f15f2d-eb69-42e6-bed4-811bff27ebf9" CreationDateTime="2016-03-02T09:27:14.000-00:00">
  <ClinicalData StudyOID="Test(Prod)" MetaDataVersionOID="1">
    <SubjectData SubjectKey="9e15f698-327e-4e9c-8ed5-8be9b27b67b0" mdsol:SubjectKeyType="SubjectUUID" mdsol:SubjectName="0100-90005">
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
</ODM>
"""

        output = etree.fromstring(self.scr.fill_empty(None, odm))
        path = ".//{0}[@{1}='{2}']".format(E_ODM.ITEM_DATA.value, A_ODM.ITEM_OID.value, 'YN')
        elem = output.find(path)
        self.assertIn(elem.get(A_ODM.VALUE.value), ['0', '1', '97'])


    def test_fill_empty_remove_values(self):
        """Test filling empty values in ODM document"""
        odm = """
<ODM xmlns="http://www.cdisc.org/ns/odm/v1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata" ODMVersion="1.3" FileType="Transactional" FileOID="c3f15f2d-eb69-42e6-bed4-811bff27ebf9" CreationDateTime="2016-03-02T09:27:14.000-00:00">
  <ClinicalData StudyOID="Test(Prod)" MetaDataVersionOID="1">
    <SubjectData SubjectKey="9e15f698-327e-4e9c-8ed5-8be9b27b67b0" mdsol:SubjectKeyType="SubjectUUID" mdsol:SubjectName="0100-90005">
      <SiteRef LocationOID="0100"/>
      <StudyEventData StudyEventOID="SCRN">
        <FormData FormOID="FORM1" FormRepeatKey="1">
          <ItemGroupData ItemGroupOID="FORM1">
            <ItemData ItemOID="YN" Value="1"/>
          </ItemGroupData>
        </FormData>
      </StudyEventData>
    </SubjectData>
  </ClinicalData>
</ODM>
"""
        output = etree.fromstring(self.scr.fill_empty(None, odm))

        for el in [E_ODM.ITEM_DATA, E_ODM.ITEM_GROUP_DATA, E_ODM.FORM_DATA, E_ODM.STUDY_EVENT_DATA]:
            path = ".//{0}".format(el.value)
            self.assertIsNone(output.find(path))


    def test_fill_empty_remove_values_ny(self):
        """Test filling empty values in ODM document with OID"""
        odm = """
<ODM xmlns="http://www.cdisc.org/ns/odm/v1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata" ODMVersion="1.3" FileType="Transactional" FileOID="c3f15f2d-eb69-42e6-bed4-811bff27ebf9" CreationDateTime="2016-03-02T09:27:14.000-00:00">
  <ClinicalData StudyOID="Test(Prod)" MetaDataVersionOID="1">
    <SubjectData SubjectKey="9e15f698-327e-4e9c-8ed5-8be9b27b67b0" mdsol:SubjectKeyType="SubjectUUID" mdsol:SubjectName="0100-90005">
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
</ODM>
"""
        fixed_values = {}
        fixed_values['YN'] = '3'
        output = etree.fromstring(self.scr.fill_empty(fixed_values, odm))
        path = ".//{0}[@{1}='{2}']".format(E_ODM.ITEM_DATA.value, A_ODM.ITEM_OID.value, 'YN')
        elem = output.find(path)
        self.assertEqual(elem.get(A_ODM.VALUE.value), '3')


if __name__ == '__main__':
    unittest.main()
