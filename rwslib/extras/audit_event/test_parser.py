# -*- coding: utf-8 -*-
__author__ = 'isparks'

import unittest
from rwslib.extras.audit_event import parser
import datetime


class TestUtils(unittest.TestCase):
    """Tests of utilities in the parser unit"""
    def test_make_int(self):
        self.assertEqual(-1, parser.make_int(None))
        self.assertEqual(-1, parser.make_int(''))
        self.assertEqual(5, parser.make_int('5'))

        with self.assertRaises(ValueError):
            self.assertEqual(-1, parser.make_int('five'))


class ParserTestCaseBase(unittest.TestCase):

    def setUp(self):

        class EventReporter(object):
            """Parser that will collect data"""
            def __init__(self):
                """We will just collect contexts as they fire from the default"""
                self.contexts = []
                self.subjects_created = 0

            def SubjectCreated(self, context):
                """As a test of calling non-default handler, we'll count subjects"""
                self.default(context)
                self.subjects_created += 1

            def default(self, context):
                self.contexts.append(context)

            @property
            def context(self):
                """Return the first context"""
                return self.contexts[0] if self.contexts else None

        self.count = 0
        self.eventer = EventReporter()

    @property
    def context(self):
        """Shortcut"""
        return self.eventer.context

    def parse(self, data):
        """Parse data, causing EventReporter to fire"""
        self.count = parser.parse(data, self.eventer)


class ParserTestCase(ParserTestCaseBase):

    def test_subject_created(self):
        """Test basics with subject created"""

        self.parse(u"""<?xml version="1.0" encoding="UTF-8"?>
<ODM xmlns="http://www.cdisc.org/ns/odm/v1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata" ODMVersion="1.3" FileType="Transactional" FileOID="4d690eda-4f08-48d1-af26-3bab40f6118f" CreationDateTime="2014-11-04T16:37:05">
  <ClinicalData StudyOID="MOVE-2014(DEV)" MetaDataVersionOID="2867" mdsol:AuditSubCategoryName="SubjectCreated">
    <SubjectData SubjectKey="538bdc4d-78b7-4ff9-a59c-3d13c8d8380b" mdsol:SubjectKeyType="SubjectUUID" mdsol:SubjectName="01" TransactionType="Upsert">
      <AuditRecord>
        <UserRef UserOID="isparks" />
        <LocationRef LocationOID="1001" />
        <DateTimeStamp>2014-08-13T10:40:06</DateTimeStamp>
        <ReasonForChange />
        <SourceID>6434193</SourceID>
      </AuditRecord>
      <SiteRef LocationOID="1001" />
    </SubjectData>
  </ClinicalData></ODM>""".encode('ascii'))

        sc = self.context

        self.assertEqual("SubjectCreated", sc.subcategory)
        self.assertEqual("MOVE-2014(DEV)", sc.study_oid)
        self.assertEqual(2867, sc.metadata_version)
        self.assertEqual("01", sc.subject.name)
        self.assertEqual("538bdc4d-78b7-4ff9-a59c-3d13c8d8380b", sc.subject.key)
        self.assertEqual(6434193, sc.audit_record.source_id)
        self.assertEqual(None, sc.audit_record.reason_for_change)
        self.assertEqual(datetime.datetime(2014, 8, 13, 10, 40, 6), sc.audit_record.datetimestamp)
        self.assertEqual("1001", sc.audit_record.location_oid)
        self.assertEqual("isparks", sc.audit_record.user_oid)

        # Check the SubjectCreated event fired
        self.assertEqual(1, self.eventer.subjects_created)

    def test_data_entered(self):
        """Test data entered with folder refs, reasons for change etc"""

        self.parse(u"""<?xml version="1.0" encoding="UTF-8"?>
<ODM xmlns="http://www.cdisc.org/ns/odm/v1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata" ODMVersion="1.3" FileType="Transactional" FileOID="4d690eda-4f08-48d1-af26-3bab40f6118f" CreationDateTime="2014-11-04T16:37:05">
   <ClinicalData StudyOID="MOVE-2014(DEV)" MetaDataVersionOID="2867" mdsol:AuditSubCategoryName="EnteredWithChangeCode">
      <SubjectData SubjectKey="538bdc4d-78b7-4ff9-a59c-3d13c8d8380b" mdsol:SubjectKeyType="SubjectUUID" mdsol:SubjectName="01">
         <SiteRef LocationOID="1001" />
         <StudyEventData StudyEventOID="VISIT1" StudyEventRepeatKey="VISIT1[1]" mdsol:InstanceId="227392">
            <FormData FormOID="VISIT" FormRepeatKey="1" mdsol:DataPageId="853098">
               <ItemGroupData ItemGroupOID="VISIT" mdsol:RecordId="1693434">
                  <ItemData ItemOID="VISIT.VISITDAT" TransactionType="Upsert" Value="7 Aug 2014">
                     <AuditRecord>
                        <UserRef UserOID="isparks" />
                        <LocationRef LocationOID="1001" />
                        <DateTimeStamp>2014-08-13T10:53:57</DateTimeStamp>
                        <ReasonForChange>Data Entry Error</ReasonForChange>
                        <SourceID>6434227</SourceID>
                     </AuditRecord>
                  </ItemData>
               </ItemGroupData>
            </FormData>
         </StudyEventData>
      </SubjectData>
   </ClinicalData>
</ODM>""".encode('ascii'))

        sc = self.context

        self.assertEqual("EnteredWithChangeCode", sc.subcategory)
        self.assertEqual("VISIT1[1]", sc.event.repeat_key)
        self.assertEqual("Upsert", sc.item.transaction_type)
        self.assertEqual("VISIT", sc.form.oid)
        self.assertEqual(1, sc.form.repeat_key)
        self.assertEqual("VISIT", sc.itemgroup.oid)
        self.assertEqual("7 Aug 2014", sc.item.value)
        self.assertEqual("VISIT.VISITDAT", sc.item.oid)
        self.assertEqual("Data Entry Error", sc.audit_record.reason_for_change)
        self.assertEqual(227392, sc.event.instance_id)
        self.assertEqual(853098, sc.form.datapage_id)
        self.assertEqual(1693434, sc.itemgroup.record_id)

    def test_query(self):
        """Test data entered with queries"""
        self.parse(u"""<?xml version="1.0" encoding="UTF-8"?>
<ODM xmlns="http://www.cdisc.org/ns/odm/v1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata" ODMVersion="1.3" FileType="Transactional" FileOID="4d690eda-4f08-48d1-af26-3bab40f6118f" CreationDateTime="2014-11-04T16:37:05">
  <ClinicalData StudyOID="MOVE-2014(DEV)" MetaDataVersionOID="2867" mdsol:AuditSubCategoryName="QueryOpen">
    <SubjectData SubjectKey="a7d8d74f-66c9-49d3-be97-33b399bd1477" mdsol:SubjectKeyType="SubjectUUID" mdsol:SubjectName="03">
      <SiteRef LocationOID="1001" />
      <StudyEventData StudyEventOID="VISIT1" StudyEventRepeatKey="VISIT1[1]">
        <FormData FormOID="VISIT" FormRepeatKey="1">
          <ItemGroupData ItemGroupOID="VISIT">
            <ItemData ItemOID="VISIT.VISITTM" TransactionType="Upsert">
              <AuditRecord>
                <UserRef UserOID="systemuser" />
                <LocationRef LocationOID="1001" />
                <DateTimeStamp>2014-08-13T12:20:35</DateTimeStamp>
                <ReasonForChange />
                <SourceID>6434490</SourceID>
              </AuditRecord>
              <mdsol:Query QueryRepeatKey="5606" Value="Data is required.  Please complete." Status="Open" Recipient="Site from System" />
            </ItemData>
          </ItemGroupData>
        </FormData>
      </StudyEventData>
    </SubjectData>
  </ClinicalData>
  </ODM>""".encode('ascii'))

        sc = self.context

        self.assertEqual("QueryOpen", sc.subcategory)
        self.assertEqual(5606, sc.query.repeat_key)
        self.assertEqual("Data is required.  Please complete.", sc.query.value)
        self.assertEqual("Open", sc.query.status)
        self.assertEqual("Site from System", sc.query.recipient)

    def test_comment(self):
        """Test data entered with comment"""
        self.parse("""<?xml version="1.0" encoding="UTF-8"?>
<ODM xmlns="http://www.cdisc.org/ns/odm/v1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata" ODMVersion="1.3" FileType="Transactional" FileOID="4d690eda-4f08-48d1-af26-3bab40f6118f" CreationDateTime="2014-11-04T16:37:05">
  <ClinicalData StudyOID="MEDICILLIN-RD7(DEMO)" MetaDataVersionOID="5" mdsol:AuditSubCategoryName="CommentAdd">
    <SubjectData SubjectKey="038f41bb-47bf-4776-8190-aaf442246f51" mdsol:SubjectKeyType="SubjectUUID" mdsol:SubjectName="10001001">
      <SiteRef LocationOID="1000" />
      <StudyEventData StudyEventOID="SCREEN" StudyEventRepeatKey="SCREEN[1]">
        <FormData FormOID="SERCHOL" FormRepeatKey="1">
          <ItemGroupData ItemGroupOID="SERCHOL">
            <ItemData ItemOID="SERCHOL.CHOL_GROUP" TransactionType="Upsert">
              <AuditRecord>
                <UserRef UserOID="systemuser" />
                <LocationRef LocationOID="1000" />
                <DateTimeStamp>2013-08-26T19:11:01</DateTimeStamp>
                <ReasonForChange />
                <SourceID>47697</SourceID>
              </AuditRecord>
              <mdsol:Comment CommentRepeatKey="2" TransactionType="Insert" Value="This subject is now able to be randomized. Please navigate to the Randomization form to randomize the subject." />
            </ItemData>
          </ItemGroupData>
        </FormData>
      </StudyEventData>
    </SubjectData>
  </ClinicalData>
  </ODM>""".encode('ascii'))

        sc = self.context

        self.assertEqual("CommentAdd", sc.subcategory)
        self.assertEqual(2, sc.comment.repeat_key)
        com = "This subject is now able to be randomized. Please navigate to the Randomization form to randomize the subject."
        self.assertEqual(com, sc.comment.value)
        self.assertEqual("Insert", sc.comment.transaction_type)

    def test_instance_name_changed(self):
        """ObjectNameChanged subcategory for changes of Instance names"""
        self.parse(u"""<?xml version="1.0" encoding="UTF-8"?>
<ODM xmlns="http://www.cdisc.org/ns/odm/v1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata" ODMVersion="1.3" FileType="Transactional" FileOID="4d690eda-4f08-48d1-af26-3bab40f6118f" CreationDateTime="2014-11-04T16:37:05">
  <ClinicalData StudyOID="MEDICILLIN-RD7(DEMO)" MetaDataVersionOID="5" mdsol:AuditSubCategoryName="ObjectNameChanged">
    <SubjectData SubjectKey="038f41bb-47bf-4776-8190-aaf442246f51" mdsol:SubjectKeyType="SubjectUUID" mdsol:SubjectName="10001001">
      <SiteRef LocationOID="1000" />
      <StudyEventData StudyEventOID="UNSCHEDULED" StudyEventRepeatKey="UNSCHEDULED[1]" TransactionType="Upsert" mdsol:InstanceName="Unscheduled Visit 22 Aug 2013">
        <AuditRecord>
          <UserRef UserOID="systemuser" />
          <LocationRef LocationOID="1000" />
          <DateTimeStamp>2013-08-26T21:09:25</DateTimeStamp>
          <ReasonForChange />
          <SourceID>47976</SourceID>
        </AuditRecord>
      </StudyEventData>
    </SubjectData>
  </ClinicalData></ODM>""".encode('ascii'))

        sc = self.context

        self.assertEqual("ObjectNameChanged", sc.subcategory)
        self.assertEqual("Upsert", sc.event.transaction_type)
        self.assertEqual("UNSCHEDULED[1]", sc.event.repeat_key)
        self.assertEqual("Unscheduled Visit 22 Aug 2013", sc.event.instance_name)
        self.assertIsNone(sc.event.instance_overdue)

    def test_datapage_name_changed(self):
        """ObjectNameChanged subcategory for changes of datapage names"""
        self.parse(u"""<?xml version="1.0" encoding="UTF-8"?>
<ODM xmlns="http://www.cdisc.org/ns/odm/v1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata" ODMVersion="1.3" FileType="Transactional" FileOID="4d690eda-4f08-48d1-af26-3bab40f6118f" CreationDateTime="2014-11-04T16:37:05">
  <ClinicalData StudyOID="MEDICILLIN-RD7(DEMO)" MetaDataVersionOID="5" mdsol:AuditSubCategoryName="ObjectNameChanged">
    <SubjectData SubjectKey="038f41bb-47bf-4776-8190-aaf442246f51" mdsol:SubjectKeyType="SubjectUUID" mdsol:SubjectName="10001001">
      <SiteRef LocationOID="1000" />
      <StudyEventData StudyEventOID="UNSCHEDULED" StudyEventRepeatKey="UNSCHEDULED[1]">
        <FormData FormOID="VS" FormRepeatKey="1" TransactionType="Upsert" mdsol:DataPageName="Vital signs">
            <AuditRecord>
              <UserRef UserOID="systemuser" />
              <LocationRef LocationOID="1000" />
              <DateTimeStamp>2013-08-26T21:09:25</DateTimeStamp>
              <ReasonForChange />
              <SourceID>47976</SourceID>
            </AuditRecord>
        </FormData>
      </StudyEventData>
    </SubjectData>
  </ClinicalData></ODM>""".encode('ascii'))

        sc = self.context

        self.assertEqual("ObjectNameChanged", sc.subcategory)
        self.assertEqual("Upsert", sc.form.transaction_type)
        self.assertEqual(1, sc.form.repeat_key)
        self.assertEqual("Vital signs", sc.form.datapage_name)

    def test_instance_overdue(self):
        """When instance overdue date is set"""
        self.parse(u"""<?xml version="1.0" encoding="UTF-8"?>
<ODM xmlns="http://www.cdisc.org/ns/odm/v1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata" ODMVersion="1.3" FileType="Transactional" FileOID="4d690eda-4f08-48d1-af26-3bab40f6118f" CreationDateTime="2014-11-04T16:37:05">
  <ClinicalData StudyOID="MEDICILLIN-RD7(DEMO)" MetaDataVersionOID="5" mdsol:AuditSubCategoryName="InstanceOverdue">
    <SubjectData SubjectKey="038f41bb-47bf-4776-8190-aaf442246f51" mdsol:SubjectKeyType="SubjectUUID" mdsol:SubjectName="10001001">
      <SiteRef LocationOID="1000" />
      <StudyEventData StudyEventOID="WEEK_03" StudyEventRepeatKey="WEEK_03[1]" TransactionType="Upsert" mdsol:InstanceOverdue="9/3/2013 12:00:00 AM">
        <AuditRecord>
          <UserRef UserOID="systemuser" />
          <LocationRef LocationOID="1000" />
          <DateTimeStamp>2013-08-26T20:04:59</DateTimeStamp>
          <ReasonForChange />
          <SourceID>47815</SourceID>
        </AuditRecord>
      </StudyEventData>
    </SubjectData>
  </ClinicalData>
</ODM>""".encode('ascii'))

        sc = self.context

        self.assertEqual("InstanceOverdue", sc.subcategory)
        self.assertEqual("Upsert", sc.event.transaction_type)
        self.assertEqual("WEEK_03[1]", sc.event.repeat_key)
        self.assertEqual("9/3/2013 12:00:00 AM", sc.event.instance_overdue)
        self.assertIsNone(sc.event.instance_name)

    def test_protocol_deviation(self):
        """Protocol deviation creation"""
        self.parse(u"""<?xml version="1.0" encoding="UTF-8"?>
<ODM xmlns="http://www.cdisc.org/ns/odm/v1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata" ODMVersion="1.3" FileType="Transactional" FileOID="4d690eda-4f08-48d1-af26-3bab40f6118f" CreationDateTime="2014-11-04T16:37:05">
  <ClinicalData StudyOID="MEDICILLIN-RD7(DEMO)" MetaDataVersionOID="5" mdsol:AuditSubCategoryName="CreatePD">
    <SubjectData SubjectKey="162685e7-7445-46e2-9178-04276fbcfc92" mdsol:SubjectKeyType="SubjectUUID" mdsol:SubjectName="10161001">
      <SiteRef LocationOID="1016" />
      <StudyEventData StudyEventOID="WEEK_01" StudyEventRepeatKey="WEEK_01[1]">
        <FormData FormOID="VS" FormRepeatKey="1">
          <ItemGroupData ItemGroupOID="VS">
            <ItemData ItemOID="VS.VSBMI" TransactionType="Upsert">
              <AuditRecord>
                <UserRef UserOID="systemuser" />
                <LocationRef LocationOID="1016" />
                <DateTimeStamp>2013-10-04T20:57:39</DateTimeStamp>
                <ReasonForChange />
                <SourceID>80966</SourceID>
              </AuditRecord>
              <mdsol:ProtocolDeviation TransactionType="Insert" Value="Body Mass Index is out of the prescribed range of LT 20 or GT 30" Status="Open" Class="Incl/Excl Criteria not met" Code="Deviation" ProtocolDeviationRepeatKey="218" />
            </ItemData>
          </ItemGroupData>
        </FormData>
      </StudyEventData>
    </SubjectData>
  </ClinicalData>
</ODM>""".encode('ascii'))

        sc = self.context

        self.assertEqual("CreatePD", sc.subcategory)
        self.assertEqual("Insert", sc.protocol_deviation.transaction_type)
        self.assertEqual("Body Mass Index is out of the prescribed range of LT 20 or GT 30", sc.protocol_deviation.value)
        self.assertEqual("Open", sc.protocol_deviation.status)
        self.assertEqual("Incl/Excl Criteria not met", sc.protocol_deviation.klass)
        self.assertEqual(218, sc.protocol_deviation.repeat_key)
        self.assertEqual("Deviation", sc.protocol_deviation.code)

    def test_review(self):
        """Test for reviews"""
        self.parse(u"""<?xml version="1.0" encoding="UTF-8"?>
<ODM xmlns="http://www.cdisc.org/ns/odm/v1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata" ODMVersion="1.3" FileType="Transactional" FileOID="4d690eda-4f08-48d1-af26-3bab40f6118f" CreationDateTime="2014-11-04T16:37:05">
  <ClinicalData StudyOID="MEDICILLIN-RD7(DEMO)" MetaDataVersionOID="5" mdsol:AuditSubCategoryName="Review">
    <SubjectData SubjectKey="7d6d3179-2da2-4521-9068-3618f8f71e10" mdsol:SubjectKeyType="SubjectUUID" mdsol:SubjectName="10081003">
      <SiteRef LocationOID="1008" />
      <StudyEventData StudyEventOID="SCREEN" StudyEventRepeatKey="SCREEN[1]">
        <FormData FormOID="VS" FormRepeatKey="1">
          <ItemGroupData ItemGroupOID="VS">
            <ItemData ItemOID="VS.TEMP" TransactionType="Upsert">
              <AuditRecord>
                <UserRef UserOID="jdustin.cdm@gmail.com" />
                <LocationRef LocationOID="1008" />
                <DateTimeStamp>2013-10-29T17:46:20</DateTimeStamp>
                <ReasonForChange>Data Management</ReasonForChange>
                <SourceID>134487</SourceID>
              </AuditRecord>
              <mdsol:Review GroupName="Data Management" Reviewed="Yes" />
            </ItemData>
          </ItemGroupData>
        </FormData>
      </StudyEventData>
    </SubjectData>
  </ClinicalData> </ODM>""".encode('ascii'))

        sc = self.context

        self.assertEqual("Review", sc.subcategory)
        self.assertTrue(sc.review.reviewed)
        self.assertEqual("Data Management", sc.review.group_name)

    def test_verify(self):
        """Test data verification"""
        self.parse(u"""<?xml version="1.0" encoding="UTF-8"?>
<ODM xmlns="http://www.cdisc.org/ns/odm/v1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata" ODMVersion="1.3" FileType="Transactional" FileOID="4d690eda-4f08-48d1-af26-3bab40f6118f" CreationDateTime="2014-11-04T16:37:05">
  <ClinicalData StudyOID="MEDICILLIN-RD7(DEMO)" MetaDataVersionOID="5" mdsol:AuditSubCategoryName="Verify">
    <SubjectData SubjectKey="b5fb9054-0ba7-428a-8b82-678f25e346c0" mdsol:SubjectKeyType="SubjectUUID" mdsol:SubjectName="10101001">
      <SiteRef LocationOID="1010" />
      <StudyEventData StudyEventOID="SCREEN" StudyEventRepeatKey="SCREEN[1]">
        <FormData FormOID="VISIT" FormRepeatKey="1">
          <ItemGroupData ItemGroupOID="VISIT">
            <ItemData ItemOID="VISIT.DTC" TransactionType="Upsert" mdsol:Verify="Yes">
              <AuditRecord>
                <UserRef UserOID="walbrocra" />
                <LocationRef LocationOID="1010" />
                <DateTimeStamp>2013-09-10T21:00:35</DateTimeStamp>
                <ReasonForChange />
                <SourceID>59545</SourceID>
              </AuditRecord>
            </ItemData>
          </ItemGroupData>
        </FormData>
      </StudyEventData>
    </SubjectData>
  </ClinicalData>  </ODM>""".encode('ascii'))

        sc = self.context

        self.assertEqual(True, sc.item.verify)

    def test_signature(self):
        """Test signatures"""
        self.parse(u"""<?xml version="1.0" encoding="UTF-8"?>
<ODM xmlns="http://www.cdisc.org/ns/odm/v1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata" ODMVersion="1.3" FileType="Transactional" FileOID="4d690eda-4f08-48d1-af26-3bab40f6118f" CreationDateTime="2014-11-04T16:37:05">
  <ClinicalData StudyOID="MEDICILLIN-RD7(DEMO)" MetaDataVersionOID="5" mdsol:AuditSubCategoryName="ValidESigCredential">
    <SubjectData SubjectKey="c8717df8-cb50-4150-88c6-a6395c6653f5" mdsol:SubjectKeyType="SubjectUUID" mdsol:SubjectName="10011001">
      <SiteRef LocationOID="1001" />
      <StudyEventData StudyEventOID="SCREEN" StudyEventRepeatKey="SCREEN[1]">
        <FormData FormOID="IE" FormRepeatKey="1" TransactionType="Upsert">
          <AuditRecord>
            <UserRef UserOID="mwissner.INV@gmail.com" />
            <LocationRef LocationOID="1001" />
            <DateTimeStamp>2013-08-29T16:11:31</DateTimeStamp>
            <ReasonForChange />
            <SourceID>52222</SourceID>
          </AuditRecord>
          <Signature>
            <UserRef UserOID="mwissner.INV@gmail.com" />
            <LocationRef LocationOID="1001" />
            <SignatureRef SignatureOID="5" />
            <DateTimeStamp>2013-08-29T16:11:31</DateTimeStamp>
          </Signature>
        </FormData>
      </StudyEventData>
    </SubjectData>
  </ClinicalData>
    </ODM>""".encode('ascii'))

        sc = self.context

        self.assertEqual("ValidESigCredential", sc.subcategory)
        self.assertEqual("5", sc.signature.oid)
        self.assertEqual("1001", sc.signature.location_oid)
        self.assertEqual("mwissner.INV@gmail.com", sc.signature.user_oid)
        self.assertEqual(datetime.datetime(2013, 8, 29, 16, 11, 31), sc.signature.datetimestamp)

    def test_form_datapage_id(self):
        """Test data entered with folder refs, reasons for change etc"""

        self.parse(u"""<?xml version="1.0" encoding="UTF-8"?>
<ODM xmlns="http://www.cdisc.org/ns/odm/v1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata" ODMVersion="1.3" FileType="Transactional" FileOID="4d690eda-4f08-48d1-af26-3bab40f6118f" CreationDateTime="2014-11-04T16:37:05">
  <ClinicalData StudyOID="MOVE-2014(DEV)" MetaDataVersionOID="2867" mdsol:AuditSubCategoryName="EnteredWithChangeCode">
    <SubjectData SubjectKey="538bdc4d-78b7-4ff9-a59c-3d13c8d8380b" mdsol:SubjectKeyType="SubjectUUID" mdsol:SubjectName="01">
      <SiteRef LocationOID="1001" />
      <StudyEventData StudyEventOID="VISIT1" StudyEventRepeatKey="VISIT1[1]">
        <FormData FormOID="VISIT" FormRepeatKey="1" mdsol:DataPageId="123">
          <ItemGroupData ItemGroupOID="VISIT">
            <ItemData ItemOID="VISIT.VISITDAT" TransactionType="Upsert" Value="7 Aug 2014">
              <AuditRecord>
                <UserRef UserOID="isparks" />
                <LocationRef LocationOID="1001" />
                <DateTimeStamp>2014-08-13T10:53:57</DateTimeStamp>
                <ReasonForChange>Data Entry Error</ReasonForChange>
                <SourceID>6434227</SourceID>
              </AuditRecord>
            </ItemData>
          </ItemGroupData>
        </FormData>
      </StudyEventData>
    </SubjectData>
  </ClinicalData>
  </ODM>""".encode('ascii'))

        sc = self.context

        self.assertEqual("EnteredWithChangeCode", sc.subcategory)
        self.assertEqual("VISIT1[1]", sc.event.repeat_key)
        self.assertEqual("Upsert", sc.item.transaction_type)
        self.assertEqual("VISIT", sc.form.oid)
        self.assertEqual(123, sc.form.datapage_id)

if __name__ == '__main__':
    unittest.main()
