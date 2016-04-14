__author__ = 'isparks'

import unittest
from rwslib.builders import *
from xml.etree import cElementTree as ET


def obj_to_doc(obj,*args, **kwargs):
    """Convert an object to am XML document object"""
    builder = ET.TreeBuilder()
    obj.build(builder, *args, **kwargs)
    return builder.close()


class TestInheritance(unittest.TestCase):
    """The things we do for 100% coverage."""
    def test_inheritance_warning(self):
        class NewObj(ODMElement):
            """We do not override the __lshift__ method"""
            pass

        with self.assertRaises(ValueError):
            # Exercise __lshift__
            NewObj() << object()


class TestAttributeSetters(unittest.TestCase):

    class TestElem(ODMElement):
        """Test class with a bad __lshift__ implementation"""
        def __init__(self):
            self.user = None
            self.locations = []

        def __lshift__(self, other):
            self.set_single_attribute(other, UserRef, "xxxuser")   #Incorrect spelling of user attribute
            self.set_list_attribute(other, LocationRef, "xxxlocations")   #Incorrect spelling of location attribute

    def test_single_attribute_misspelling(self):
        tested = TestAttributeSetters.TestElem()
        with self.assertRaises(AttributeError):
            tested << UserRef("Fred")

    def test_list_attribute_misspelling(self):
        tested = TestAttributeSetters.TestElem()
        with self.assertRaises(AttributeError):
            tested << LocationRef("Site 22")

class TestUserRef(unittest.TestCase):
    def test_accepts_no_children(self):
        with self.assertRaises(ValueError):
            UserRef("Gertrude") << object()

    def test_builder(self):
        """Test building XML"""
        tested = UserRef('Fred')
        doc = obj_to_doc(tested)

        self.assertEqual(doc.attrib['UserOID'],"Fred")
        self.assertEqual(doc.tag,"UserRef")

class TestLocationRef(unittest.TestCase):
    def test_accepts_no_children(self):
        with self.assertRaises(ValueError):
            LocationRef("Nowhereville") << object()

    def test_builder(self):
        """Test building XML"""
        tested = LocationRef('Gainesville')
        doc = obj_to_doc(tested)

        self.assertEqual(doc.attrib['LocationOID'], "Gainesville")
        self.assertEqual(doc.tag, "LocationRef")

class TestReasonForChange(unittest.TestCase):
    def test_accepts_no_children(self):
        with self.assertRaises(ValueError):
            ReasonForChange("Because I wanted to") << object()

    def test_builder(self):
        """Test building XML"""
        tested = ReasonForChange("Testing 1..2..3")
        doc = obj_to_doc(tested)

        self.assertEqual("Testing 1..2..3", doc.text)
        self.assertEqual(doc.tag, "ReasonForChange")

class TestDateTimeStamp(unittest.TestCase):
    def test_accepts_no_children(self):
        with self.assertRaises(ValueError):
            DateTimeStamp(datetime.now()) << object()

    def test_builder_with_datetime(self):
        dt = datetime(2015, 9, 11, 10, 15, 22, 80)
        tested = DateTimeStamp(dt)
        doc = obj_to_doc(tested)

        self.assertEqual(dt_to_iso8601(dt), doc.text)
        self.assertEqual(doc.tag, "DateTimeStamp")

    def test_builder_with_string(self):
        dt = "2009-02-04T14:10:32-05:00"
        tested = DateTimeStamp(dt)
        doc = obj_to_doc(tested)
        self.assertEqual(dt, doc.text)
        self.assertEqual(doc.tag, "DateTimeStamp")


class TestAuditRecord(unittest.TestCase):
    def setUp(self):
        self.tested = AuditRecord(edit_point=AuditRecord.EDIT_DATA_MANAGEMENT,
                                  used_imputation_method= False,
                                  identifier='X2011',
                                  include_file_oid=False)
        self.tested << UserRef("Fred")
        self.tested << LocationRef("Site102")
        self.tested << ReasonForChange("Data Entry Error")
        self.tested << DateTimeStamp(datetime(2015, 9, 11, 10, 15, 22, 80))

    def test_identifier_must_not_start_digit(self):
        with self.assertRaises(AttributeError):
            AuditRecord(identifier='2011')

        with self.assertRaises(AttributeError):
            AuditRecord(identifier='*Hello')

        # Underscore OK
        ar = AuditRecord(identifier='_Hello')
        self.assertEqual('_Hello', ar.id)

        # Letter OK
        ar = AuditRecord(identifier='Hello')
        self.assertEqual('Hello', ar.id)


    def test_accepts_no_invalid_children(self):
        with self.assertRaises(ValueError):
            AuditRecord() << object()

    def test_invalid_edit_point(self):
        with self.assertRaises(AttributeError):
            AuditRecord(edit_point='Blah')

    def test_builder(self):
        doc = obj_to_doc(self.tested)
        self.assertEqual(doc.tag, "AuditRecord")
        self.assertEqual(AuditRecord.EDIT_DATA_MANAGEMENT, doc.attrib["EditPoint"])
        self.assertEqual("No", doc.attrib["UsedImputationMethod"])
        self.assertEqual("No", doc.attrib["mdsol:IncludeFileOID"])
        self.assertEqual("UserRef", doc.getchildren()[0].tag)
        self.assertEqual("LocationRef", doc.getchildren()[1].tag)
        self.assertEqual("DateTimeStamp", doc.getchildren()[2].tag)
        self.assertEqual("ReasonForChange", doc.getchildren()[3].tag)

    def test_no_user_ref(self):
        """Test with no user ref should fail on build with a ValueError"""
        self.tested.user_ref = None
        with self.assertRaises(ValueError) as err:
            doc = obj_to_doc(self.tested)
            self.assertIn("UserRef", err.exception.message)

    def test_no_location_ref(self):
        """Test with no location ref should fail on build with a ValueError"""
        self.tested.location_ref = None
        with self.assertRaises(ValueError) as err:
            doc = obj_to_doc(self.tested)
            self.assertIn("LocationRef", err.exception.message)

    def test_no_datetime_stamp(self):
        """Test with no datetimestamp should fail on build with a ValueError"""
        self.tested.date_time_stamp = None
        with self.assertRaises(ValueError) as err:
            doc = obj_to_doc(self.tested)
            self.assertIn("DateTimeStamp", err.exception.message)

class TestMdsolQuery(unittest.TestCase):
    """Test extension MdsolQuery"""
    def get_tested(self):
        return MdsolQuery(status=QueryStatusType.Open, value="Data missing", query_repeat_key=123,
                            recipient="Site from System", requires_response=True)

    def test_basic(self):
        tested = self.get_tested()
        self.assertEqual("Data missing",tested.value)
        self.assertEqual(123,tested.query_repeat_key)
        self.assertEqual(QueryStatusType.Open,tested.status)
        self.assertEqual("Site from System",tested.recipient)
        self.assertEqual(True,tested.requires_response)

    def test_builder(self):
        tested = self.get_tested()
        tested.response = "Done"
        doc = obj_to_doc(tested)
        self.assertEqual("mdsol:Query", doc.tag)
        self.assertEqual("Yes", doc.attrib['RequiresResponse'])
        self.assertEqual("Site from System", doc.attrib['Recipient'])
        self.assertEqual("123", doc.attrib['QueryRepeatKey'])
        self.assertEqual("Data missing", doc.attrib['Value'])
        self.assertEqual("Done", doc.attrib['Response'])

    def test_invalid_status_value(self):
        """Status must come from QueryStatusType"""
        with self.assertRaises(AttributeError):
            MdsolQuery(status='A test')


class TestItemData(unittest.TestCase):
    """Test ItemData classes"""
    def setUp(self):
        self.tested = ItemData('FIELDA',"TEST")

    def test_basic(self):
        tested = self.tested
        self.assertEqual(tested.itemoid, "FIELDA")
        self.assertEqual(tested.value, "TEST")
        self.assertEqual(tested.lock, None)
        self.assertEqual(tested.freeze, None)
        self.assertEqual(tested.verify, None)

    def test_only_accepts_itemdata(self):
        """Test that an ItemData will not accept any old object"""
        with self.assertRaises(ValueError):
            self.tested << {"Field1" : "ValueC"}

    def test_accepts_query(self):
        """Test that an ItemData will accept a query"""
        query = MdsolQuery()
        self.tested << query
        self.assertEqual(query, self.tested.queries[0])

    def test_accepts_measurement_unit_ref(self):
        """Test that an ItemData will accept a measurement unit ref"""
        mur = MeasurementUnitRef("Celsius")
        self.tested << mur
        self.assertEqual(mur, self.tested.measurement_unit_ref)

    def test_isnull_not_set(self):
        """Isnull should not be set where we have a value not in '', None"""
        doc = obj_to_doc(self.tested)
        # Check IsNull attribute is missing
        def do():
            doc.attrib['IsNull']
        self.assertRaises(KeyError,do)

    def test_specify(self):
        """Test specify"""
        specify_value = 'A Specify'
        self.tested.specify_value = specify_value
        doc = obj_to_doc(self.tested)
        self.assertEqual(doc.attrib['mdsol:SpecifyValue'],specify_value)

    def test_freeze_lock_verify(self):
        tested = ItemData('FIELDA',"TEST", lock=True, verify=True, freeze=False)
        self.assertEqual(tested.lock, True)
        self.assertEqual(tested.freeze, False)
        self.assertEqual(tested.verify, True)

    def test_builder(self):
        """Test building XML"""
        tested = ItemData('FIELDA',"TEST", lock=True, verify=True, freeze=False)

        tested << AuditRecord(edit_point=AuditRecord.EDIT_DATA_MANAGEMENT,
                                  used_imputation_method= False,
                                  identifier="x2011",
                                  include_file_oid=False)(
            UserRef("Fred"),
            LocationRef("Site102"),
            ReasonForChange("Data Entry Error"),
            DateTimeStamp(datetime(2015, 9, 11, 10, 15, 22, 80))
        )
        tested << MdsolQuery()
        tested << MeasurementUnitRef("Celsius")


        doc = obj_to_doc(tested)

        self.assertEqual(doc.attrib['ItemOID'],"FIELDA")
        self.assertEqual(doc.attrib['Value'],"TEST")
        self.assertEqual(doc.attrib['mdsol:Verify'],"Yes")
        self.assertEqual(doc.attrib['mdsol:Lock'],"Yes")
        self.assertEqual(doc.attrib['mdsol:Freeze'],"No")
        self.assertEqual(doc.tag,"ItemData")
        self.assertEqual("AuditRecord",doc.getchildren()[0].tag)
        self.assertEqual("MeasurementUnitRef",doc.getchildren()[1].tag)
        self.assertEqual("mdsol:Query",doc.getchildren()[2].tag)

    def test_transaction_type(self):
        tested = self.tested
        tested.transaction_type = 'Update'
        doc = obj_to_doc(tested)
        self.assertEqual(doc.attrib['TransactionType'],"Update")

    def test_null_value(self):
        """Null or empty string values are treated specially with IsNull property and no value"""
        tested = self.tested
        tested.value = ''
        doc = obj_to_doc(tested)
        self.assertEqual(doc.attrib['IsNull'],"Yes")

        #Check Value attribute is also missing
        def do():
            doc.attrib["Value"]
        self.assertRaises(KeyError,do)


    def test_invalid_transaction_type(self):
        def do():
            ItemData("A","val",transaction_type='invalid')

        self.assertRaises(AttributeError, do )


class TestItemGroupData(unittest.TestCase):
    """Test ItemGroupData classes"""

    def setUp(self):
        self.tested = ItemGroupData()(
            ItemData("Field1","ValueA"),
            ItemData("Field2","ValueB")
        )

    def test_children(self):
        """Test there are 2 children"""
        self.assertEqual(2, len(self.tested.items))

    def test_two_same_invalid(self):
        """Test adding a duplicate field causes error"""
        def do():
            self.tested << ItemData("Field1","ValueC")
        self.assertRaises(ValueError,do)

    def test_only_accepts_itemdata(self):
        """Test that an ItemGroupData will only accept an ItemData element"""
        def do():
            self.tested << {"Field1" : "ValueC"}
        self.assertRaises(ValueError,do)

    def test_invalid_transaction_type(self):
        def do():
            ItemGroupData(transaction_type='invalid')
        self.assertRaises(AttributeError, do )

    def test_builders_basic(self):
        doc = obj_to_doc(self.tested,"TESTFORM")
        self.assertEqual(doc.attrib["ItemGroupOID"],"TESTFORM")
        self.assertEqual(len(doc),2)
        self.assertEqual(doc.tag,"ItemGroupData")

    def test_transaction_type(self):
        """Test transaction type inserted if set"""
        self.tested.transaction_type = 'Context'
        doc = obj_to_doc(self.tested,"TESTFORM")
        self.assertEqual(doc.attrib["TransactionType"],"Context")

    def test_whole_item_group(self):
        """mdsol:Submission should be wholeitemgroup or SpecifiedItemsOnly"""
        doc = obj_to_doc(self.tested,"TESTFORM")
        self.assertEqual(doc.attrib["mdsol:Submission"],"SpecifiedItemsOnly")

        self.tested.whole_item_group = True
        doc = obj_to_doc(self.tested,"TESTFORM")
        self.assertEqual(doc.attrib["mdsol:Submission"],"WholeItemGroup")


class TestFormData(unittest.TestCase):
    """Test FormData classes"""

    def setUp(self):
        self.tested = FormData("TESTFORM_A") (
            ItemGroupData()(
                ItemData("Field1","ValueA"),
                ItemData("Field2","ValueB")
            ),
            ItemGroupData()(
                ItemData("Field3","ValueC"),
            ),
            ItemGroupData()(
                ItemData("Field4","ValueD"),
            ),
        )

    def test_children(self):
        """Test there are 3 children"""
        self.assertEqual(3, len(self.tested.itemgroups))

    def test_invalid_transaction_type(self):
        """Can only be insert, update, upsert not context"""
        def do():
            FormData("MYFORM",transaction_type='context')
        self.assertRaises(AttributeError, do )

    def test_only_accepts_itemgroupdata(self):
        """Test that only ItemGroupData can be inserted"""
        def do():
            # Bzzzt. Should be ItemGroupData
            self.tested << ItemData("Field1","ValueC")
        self.assertRaises(ValueError,do)

    def test_only_add_itemgroup_once(self):
        """Test that an ItemGroupData can only be added once"""
        igd = ItemGroupData()
        self.tested << igd
        def do():
            self.tested << igd
        self.assertRaises(ValueError,do)

    def test_builders_basic(self):
        doc = obj_to_doc(self.tested)
        self.assertEqual(doc.attrib["FormOID"], "TESTFORM_A")
        self.assertEqual(len(doc), 3)
        self.assertEqual(doc.tag, "FormData")

    def test_transaction_type(self):
        """Test transaction type inserted if set"""
        self.tested.transaction_type = 'Update'
        doc = obj_to_doc(self.tested)
        self.assertEqual(doc.attrib["TransactionType"], self.tested.transaction_type)

    def test_invalid_transaction_type_direct_assign(self):
        """Test transaction type will not allow you to set to invalid choice"""
        def do():
            self.tested.transaction_type = 'invalid'
        self.assertRaises(AttributeError,do)

    def test_form_repeat_key(self):
        """Test transaction type inserted if set"""
        tested = FormData("TESTFORM_A", form_repeat_key=9) (
            ItemGroupData()(
                ItemData("Field1", "ValueA"),
                ItemData("Field2", "ValueB")
            )
       )
        doc = obj_to_doc(tested)
        self.assertEqual(doc.attrib["FormRepeatKey"],"9")


class TestStudyEventData(unittest.TestCase):
    """Test StudyEventData classes"""
    def setUp(self):
         self.tested = StudyEventData('VISIT_1') (
            FormData("TESTFORM_A") (
                ItemGroupData()(
                    ItemData("Field1", "ValueA"),
                    ItemData("Field2", "ValueB")
                ),
                ItemGroupData(item_group_repeat_key=2)(
                    ItemData("Field3", "ValueC"),
                ),
            )
        )

    def test_transaction_type(self):
        """Test transaction type inserted if set"""
        self.tested.transaction_type = 'Update'
        doc = obj_to_doc(self.tested)
        self.assertEqual(doc.attrib["TransactionType"],self.tested.transaction_type)

    def test_builders_basic(self):
        doc = obj_to_doc(self.tested)
        self.assertEqual(doc.attrib["StudyEventOID"],"VISIT_1")
        self.assertIsNone(doc.attrib.get("StudyEventRepeatKey"))
        self.assertEqual(len(doc),1)
        self.assertEqual(doc.tag,"StudyEventData")

    def test_only_add_formdata_once(self):
        """Test that an FormData object can only be added once"""
        fd = FormData("FORM1")
        self.tested << fd
        def do():
            self.tested << fd
        self.assertRaises(ValueError,do)

    def test_invalid_transaction_type_direct_assign(self):
        """Test transaction type will not allow you to set to invalid choice"""
        def do():
            self.tested.transaction_type = 'upsert'
        self.assertRaises(AttributeError,do)

    def test_invalid_transaction_type(self):
        """According to docs does not permit upserts"""
        def do():
            StudyEventData("V2",transaction_type='upsert')
        self.assertRaises(AttributeError, do )

    def test_only_accepts_formdata(self):
        """Test that only FormData can be inserted"""
        def do():
            # Bzzzt. Should be ItemGroupData
            self.tested << ItemData("Field1", "ValueC")
        self.assertRaises(ValueError,do)


class TestSubjectData(unittest.TestCase):
    """Test SubjectData classes"""
    def setUp(self):
        self.tested = SubjectData("SITE1","SUBJECT1")(
            StudyEventData('VISIT_1')(
                FormData("TESTFORM_A")(
                    ItemGroupData()(
                        ItemData("Field1", "ValueA"),
                        ItemData("Field2", "ValueB")
                    ),
                    ItemGroupData(item_group_repeat_key=2)(
                        ItemData("Field3", "ValueC"),
                    ),
                )
            )
        )

    def test_basic(self):
        """Test there are 3 children"""
        self.assertEqual("SITE1", self.tested.sitelocationoid)
        self.assertEqual("SUBJECT1", self.tested.subject_key)
        # Default transaction type
        self.assertEqual("Update", self.tested.transaction_type)

    def test_invalid_transaction_type_direct_assign(self):
        """Test transaction type will not allow you to set to invalid choice"""
        def do():
            self.tested.transaction_type = 'UpDateSert'
        self.assertRaises(AttributeError, do)

    def test_children(self):
        """Test there is 1 child"""
        self.assertEqual(1, len(self.tested.study_events))

    def test_invalid_transaction_type(self):
        """According to docs does not permit upserts"""
        def do():
            SubjectData("SITEA", "SUB1", transaction_type='upsert')

        self.assertRaises(AttributeError, do )

    def test_builder(self):
        """XML produced"""
        doc = obj_to_doc(self.tested)
        # Test default transaction tyoe
        self.assertEqual(doc.attrib["TransactionType"], "Update")
        self.assertEqual(doc.tag, "SubjectData")

    def test_only_add_studyeventdata_once(self):
        """Test that a StudyEventData object can only be added once"""
        sed = StudyEventData("V1")
        self.tested << sed
        def do():
            self.tested << sed
        self.assertRaises(ValueError,do)

    def test_does_not_accept_all_elements(self):
        """Test that,for example, ItemData cannot be accepted"""
        def do():
            self.tested << ItemData("Field1", "ValueC")
        self.assertRaises(ValueError, do)

    def test_accepts_auditrecord(self):
        """Test that AuditRecord can be inserted"""
        ar = AuditRecord(used_imputation_method=False,
                         identifier='ABC1',
                         include_file_oid=False)(
                            UserRef('test_user'),
                            LocationRef('test_site'),
                            ReasonForChange("Testing"),
                            DateTimeStamp(datetime.now())
                         )
        self.tested << ar
        self.assertEqual(self.tested.audit_record, ar)


class TestClinicalData(unittest.TestCase):
    """Test ClinicalData classes"""
    def setUp(self):
        self.tested = ClinicalData("STUDY1", "DEV")(
            SubjectData("SITE1","SUBJECT1")(
                StudyEventData('VISIT_1')(
                    FormData("TESTFORM_A")(
                        ItemGroupData()(
                            ItemData("Field1", "ValueA"),
                            ItemData("Field2", "ValueB")
                        ),
                        ItemGroupData(item_group_repeat_key=2)(
                            ItemData("Field3", "ValueC"),
                        ),
                    )
                )
            )
        )

    def test_basic(self):
        """Test there are 3 children"""
        self.assertEqual("STUDY1", self.tested.projectname)
        self.assertEqual("DEV", self.tested.environment)
        # Test default MetadataVersionOID
        self.assertEqual("1", self.tested.metadata_version_oid)


    def test_metadata_version_oid(self):
        self.tested.metadata_version_oid = '2'
        doc = obj_to_doc(self.tested)
        self.assertEqual(doc.attrib["MetaDataVersionOID"],self.tested.metadata_version_oid)


    def test_only_accepts_subjectdata(self):
        """Test that only SubjectData can be inserted"""
        tested = ClinicalData("STUDY1", "DEV")
        def do():
            tested << object()
        self.assertRaises(ValueError,do)

    def test_only_accepts_one_subject(self):
        """Test that only one SubjectData can be inserted"""
        def do():
            self.tested << SubjectData("SITE2", "SUBJECT2")
        self.assertRaises(ValueError,do)

    def test_builder(self):
        """XML produced"""
        doc = obj_to_doc(self.tested)
        self.assertEqual(doc.tag,"ClinicalData")


class TestODM(unittest.TestCase):
    """Test ODM wrapper class"""

    def setUp(self):
        self.tested = ODM("MY TEST SYSTEM", description="My test message")(
            ClinicalData("STUDY1","DEV")(
                SubjectData("SITE1","SUBJECT1")(
                    StudyEventData('VISIT_1')(
                        FormData("TESTFORM_A")(
                            ItemGroupData()(
                                ItemData("Field1", "ValueA"),
                                ItemData("Field2", "ValueB")
                            ),
                            ItemGroupData(item_group_repeat_key=2)(
                                ItemData("Field3", "ValueC"),
                            ),
                        )
                    )
                )
            )
        )

    def test_basic(self):
        """Basic tests"""
        # If no fileoid is given, a unique id is generated
        self.assertEqual(True,self.tested.fileoid is not None)
        self.assertEqual("My test message", self.tested.description)

    def test_assign_fileoid(self):
        """Test if you assign a fileoid it keeps it"""
        tested = ODM("MY TEST SYSTEM", fileoid="F1")
        self.assertEqual("F1", tested.fileoid)

    def test_only_accepts_valid_children(self):
        """Test that only ClinicalData or Study can be inserted"""
        def do():
            self.tested << ItemData("Field1", "ValueC")
        self.assertRaises(ValueError,do)

    def test_accepts_clinicaldata_and_study(self):
        """Test that accepts clinicaldata"""
        tested = ODM("MY TEST SYSTEM", fileoid="F1")
        cd = ClinicalData("Project1","DEV")
        study = Study("PROJ1",project_type=Study.PROJECT)
        tested << cd
        tested << study
        self.assertEqual(study,tested.study)
        self.assertEqual(cd, tested.clinical_data)

    def test_getroot(self):
        """XML produced"""
        doc = self.tested.getroot()
        self.assertEqual(doc.tag,"ODM")
        self.assertEqual(doc.attrib["Originator"], "MY TEST SYSTEM")
        self.assertEqual(doc.attrib["Description"], self.tested.description)
        self.assertEqual("ClinicalData", doc.getchildren()[0].tag)

    def test_getroot_study(self):
        """XML produced with a study child"""
        tested = ODM("MY TEST SYSTEM", fileoid="F1")
        study = Study("PROJ1",project_type=Study.PROJECT)
        tested << study
        doc = tested.getroot()
        self.assertEqual(doc.tag,"ODM")
        self.assertEqual("Study", doc.getchildren()[0].tag)

    def test_str_well_formed(self):
        """Make an XML string from the object, parse it to ensure it's well formed"""
        doc = ET.fromstring(str(self.tested))
        NS_ODM = '{http://www.cdisc.org/ns/odm/v1.3}'
        self.assertEqual(doc.tag,NS_ODM + "ODM")
        self.assertEqual(doc.attrib["Originator"], "MY TEST SYSTEM")
        self.assertEqual(doc.attrib["Description"], self.tested.description)


if __name__ == '__main__':
    unittest.main()
