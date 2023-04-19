from rwslib.extras.audit_event import parser
import unittest
import os


class MockEventer:
    """
    Mock Event Sink instance for the purposes of testing (capturing all ASC)
    """

    def __init__(self):
        self.__events = {}

    def default(self, event):
        self.__events.setdefault(event.subcategory, []).append(event)

    def get_audit_subcategory_events(self, audit_subcategory):
        return self.__events[audit_subcategory]

    @property
    def eventlist(self):
        return self.__events.keys()


class MockEventerEntered:
    """
    Mock Event Sink instance for the purposes of testing (capturing only 'Entered' ASC)
    """

    def __init__(self):
        self.__events = {}

    def get_audit_subcategory_events(self, audit_subcategory):
        return self.__events.get(audit_subcategory, [])

    def Entered(self, event):
        self.__events.setdefault(event.subcategory, []).append(event)

    @property
    def eventlist(self):
        return self.__events.keys()


class TestAuditEvent(unittest.TestCase):
    """
    Test Case for Audit Event Processor
    """
    def test_parses_audit_message(self):
        """parses an audit message from a CAR message"""
        with open(
            os.path.join(os.path.dirname(__file__), "fixtures", "car_message.xml")
        ) as fh:
            content = fh.read()
        eventer = MockEventer()
        message = parser.parse(content, eventer)
        # get the events
        self.assertTrue(len(eventer.eventlist) > 1)
        self.assertTrue("EnteredEmpty" in eventer.eventlist)
        self.assertEqual(60, len(eventer.get_audit_subcategory_events("EnteredEmpty")))
        self.assertEqual(501, len(eventer.get_audit_subcategory_events("Entered")))

    def test_parses_audit_message_entered(self):
        """parses an audit message, but only subscribe to Entered Events from a CAR message"""
        with open(
            os.path.join(os.path.dirname(__file__), "fixtures", "car_message.xml")
        ) as fh:
            content = fh.read()
        eventer = MockEventerEntered()
        message = parser.parse(content, eventer)
        # get the events
        self.assertTrue(len(eventer.eventlist) == 1)
        self.assertTrue("EnteredEmpty" not in eventer.eventlist)
        self.assertEqual(0, len(eventer.get_audit_subcategory_events("EnteredEmpty")))
        self.assertEqual(501, len(eventer.get_audit_subcategory_events("Entered")))

    def test_parses_audit_message_subject_created(self):
        """parses an audit message, but only subscribe to Entered Events from a CAR message"""
        with open(
            os.path.join(os.path.dirname(__file__), "fixtures", "car_message.xml")
        ) as fh:
            content = fh.read()
        eventer = MockEventer()
        message = parser.parse(content, eventer)
        # get the events
        self.assertEqual(
            92, len(eventer.get_audit_subcategory_events("SubjectCreated"))
        )
        subject_123_ABC = eventer.get_audit_subcategory_events("SubjectCreated")[0]
        self.assertEqual(
            "e983f330-c108-45ab-8f16-b4a566c7089c", subject_123_ABC.subject.key
        )
        self.assertEqual("123 ABC", subject_123_ABC.subject.name)

    def test_parses_specify_value(self):
        """Extracts a specified value from a CAR message"""
        content = """<ODM ODMVersion="1.3" FileType="Transactional" FileOID="552a8cac-7c4e-4ba5-9f71-a20b90865531" CreationDateTime="2021-06-02T10:21:02" xmlns="http://www.cdisc.org/ns/odm/v1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata">
            <ClinicalData StudyOID="Mediflex" MetaDataVersionOID="16"  mdsol:AuditSubCategoryName="Entered">
        <SubjectData SubjectKey="e983f330-c108-45ab-8f16-b4a566c7089c" mdsol:SubjectKeyType="SubjectUUID" mdsol:SubjectName="123 ABC"  >
            <SiteRef LocationOID="MDSOL" />
            <StudyEventData StudyEventOID="SCREEN"  StudyEventRepeatKey="SCREEN[1]"   mdsol:InstanceId="50" >
                <FormData FormOID="DM" FormRepeatKey="1"  mdsol:DataPageId="179" >
                    <ItemGroupData ItemGroupOID="DM"   mdsol:RecordId="251" >
                        <ItemData ItemOID="DM.SEX" TransactionType="Upsert"  Value="Specify" mdsol:SpecifyValue="UNDEF"	 >
                            <AuditRecord>
                                <UserRef UserOID="pvummudi"/>
                                <LocationRef LocationOID="MDSOL" />
                                <DateTimeStamp>2008-12-04T16:59:07</DateTimeStamp>
                                <ReasonForChange></ReasonForChange>
                                <SourceID>3284</SourceID>
                            </AuditRecord>
                        </ItemData>
                    </ItemGroupData>
                </FormData>
            </StudyEventData>
        </SubjectData>
    </ClinicalData>
        </ODM>
        """
        eventer = MockEventer()
        message = parser.parse(content, eventer)
        event = eventer.get_audit_subcategory_events("Entered")[0]
        self.assertEqual("UNDEF", event.item.specify_value)
        self.assertEqual("Specify", event.item.value)
        self.assertEqual("DM.SEX", event.item.oid)

    def test_parses_signature_broken(self):
        """mdsol:SignatureBroken parsing for case when broken from a CAR message"""
        content = """<ODM ODMVersion="1.3" FileType="Transactional" FileOID="552a8cac-7c4e-4ba5-9f71-a20b90865531" CreationDateTime="2021-06-02T10:21:02" xmlns="http://www.cdisc.org/ns/odm/v1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata">
            <ClinicalData StudyOID="Mediflex" MetaDataVersionOID="16"  mdsol:AuditSubCategoryName="Entered">
        <SubjectData SubjectKey="e983f330-c108-45ab-8f16-b4a566c7089c" mdsol:SubjectKeyType="SubjectUUID" mdsol:SubjectName="123 ABC"  >
            <SiteRef LocationOID="MDSOL" />
            <StudyEventData StudyEventOID="SCREEN"  StudyEventRepeatKey="SCREEN[1]"   mdsol:InstanceId="50" >
                <FormData FormOID="DM" FormRepeatKey="1"  mdsol:DataPageId="179" >
                    <ItemGroupData ItemGroupOID="DM"   mdsol:RecordId="251" >
                        <ItemData ItemOID="DM.SEX" TransactionType="Upsert"  Value="Specify" mdsol:SpecifyValue="UNDEF"	mdsol:SignatureBroken="Yes" >
                            <AuditRecord>
                                <UserRef UserOID="pvummudi"/>
                                <LocationRef LocationOID="MDSOL" />
                                <DateTimeStamp>2008-12-04T16:59:07</DateTimeStamp>
                                <ReasonForChange></ReasonForChange>
                                <SourceID>3284</SourceID>
                            </AuditRecord>
                        </ItemData>
                    </ItemGroupData>
                </FormData>
            </StudyEventData>
        </SubjectData>
    </ClinicalData>
        </ODM>
        """
        eventer = MockEventer()
        message = parser.parse(content, eventer)
        event = eventer.get_audit_subcategory_events("Entered")[0]
        self.assertEqual("UNDEF", event.item.specify_value)
        self.assertEqual("Specify", event.item.value)
        self.assertEqual("DM.SEX", event.item.oid)
        self.assertTrue(event.item.signature_broken)

    def test_parses_signature_not_broken(self):
        """mdsol:SignatureBroken parsing for case when not broken from a CAR message"""
        content = """<ODM ODMVersion="1.3" FileType="Transactional" FileOID="552a8cac-7c4e-4ba5-9f71-a20b90865531" CreationDateTime="2021-06-02T10:21:02" xmlns="http://www.cdisc.org/ns/odm/v1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata">
            <ClinicalData StudyOID="Mediflex" MetaDataVersionOID="16"  mdsol:AuditSubCategoryName="Entered">
        <SubjectData SubjectKey="e983f330-c108-45ab-8f16-b4a566c7089c" mdsol:SubjectKeyType="SubjectUUID" mdsol:SubjectName="123 ABC"  >
            <SiteRef LocationOID="MDSOL" />
            <StudyEventData StudyEventOID="SCREEN"  StudyEventRepeatKey="SCREEN[1]"   mdsol:InstanceId="50" >
                <FormData FormOID="DM" FormRepeatKey="1"  mdsol:DataPageId="179" >
                    <ItemGroupData ItemGroupOID="DM"   mdsol:RecordId="251" >
                        <ItemData ItemOID="DM.SEX" TransactionType="Upsert"  Value="Specify" mdsol:SpecifyValue="UNDEF"	mdsol:SignatureBroken="No" >
                            <AuditRecord>
                                <UserRef UserOID="pvummudi"/>
                                <LocationRef LocationOID="MDSOL" />
                                <DateTimeStamp>2008-12-04T16:59:07</DateTimeStamp>
                                <ReasonForChange></ReasonForChange>
                                <SourceID>3284</SourceID>
                            </AuditRecord>
                        </ItemData>
                    </ItemGroupData>
                </FormData>
            </StudyEventData>
        </SubjectData>
    </ClinicalData>
        </ODM>
        """
        eventer = MockEventer()
        message = parser.parse(content, eventer)
        event = eventer.get_audit_subcategory_events("Entered")[0]
        self.assertEqual("UNDEF", event.item.specify_value)
        self.assertEqual("Specify", event.item.value)
        self.assertEqual("DM.SEX", event.item.oid)
        self.assertFalse(event.item.signature_broken)

