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

        def do():
            no = NewObj()
            #Exercise __lshift__
            no << object()
        self.assertRaises(NotImplementedError,do)


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

    def test_isnull_not_set(self):
        """Isnull should not be set where we have a value not in '', None"""
        doc = obj_to_doc(self.tested)
        #Check IsNull attribute is missing
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
        doc = obj_to_doc(tested)

        self.assertEqual(doc.attrib['ItemOID'],"FIELDA")
        self.assertEqual(doc.attrib['Value'],"TEST")
        self.assertEqual(doc.attrib['mdsol:Verify'],"Yes")
        self.assertEqual(doc.attrib['mdsol:Lock'],"Yes")
        self.assertEqual(doc.attrib['mdsol:Freeze'],"No")
        self.assertEquals(doc.tag,"ItemData")

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
        self.assertEquals(2, len(self.tested.items))

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
        self.assertEquals(doc.attrib["ItemGroupOID"],"TESTFORM")
        self.assertEquals(len(doc),2)
        self.assertEquals(doc.tag,"ItemGroupData")

    def test_transaction_type(self):
        """Test transaction type inserted if set"""
        self.tested.transaction_type = 'Context'
        doc = obj_to_doc(self.tested,"TESTFORM")
        self.assertEquals(doc.attrib["TransactionType"],"Context")

    def test_whole_item_group(self):
        """mdsol:Submission should be wholeitemgroup or SpecifiedItemsOnly"""
        doc = obj_to_doc(self.tested,"TESTFORM")
        self.assertEquals(doc.attrib["mdsol:Submission"],"SpecifiedItemsOnly")

        self.tested.whole_item_group = True
        doc = obj_to_doc(self.tested,"TESTFORM")
        self.assertEquals(doc.attrib["mdsol:Submission"],"WholeItemGroup")


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
        self.assertEquals(doc.attrib["FormOID"], "TESTFORM_A")
        self.assertEquals(len(doc), 3)
        self.assertEquals(doc.tag, "FormData")

    def test_transaction_type(self):
        """Test transaction type inserted if set"""
        self.tested.transaction_type = 'Update'
        doc = obj_to_doc(self.tested)
        self.assertEquals(doc.attrib["TransactionType"], self.tested.transaction_type)

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
        self.assertEquals(doc.attrib["FormRepeatKey"],"9")

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
        self.assertEquals(doc.attrib["TransactionType"],self.tested.transaction_type)

    def test_builders_basic(self):
        doc = obj_to_doc(self.tested)
        self.assertEquals(doc.attrib["StudyEventOID"],"VISIT_1")
        self.assertEquals(len(doc),1)
        self.assertEquals(doc.tag,"StudyEventData")

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
        self.assertEquals("SITE1", self.tested.sitelocationoid)
        self.assertEquals("SUBJECT1", self.tested.subject_key)
        #Default transaction type
        self.assertEquals("Update", self.tested.transaction_type)

    def test_invalid_transaction_type_direct_assign(self):
        """Test transaction type will not allow you to set to invalid choice"""
        def do():
            self.tested.transaction_type = 'UpDateSert'
        self.assertRaises(AttributeError, do)

    def test_children(self):
        """Test there are 3 children"""
        self.assertEquals(1, len(self.tested.study_events))

    def test_invalid_transaction_type(self):
        """According to docs does not permit upserts"""
        def do():
            SubjectData("SITEA", "SUB1", transaction_type='upsert')

        self.assertRaises(AttributeError, do )

    def test_builder(self):
        """XML produced"""
        doc = obj_to_doc(self.tested)
        #Test default transaction tyoe
        self.assertEquals(doc.attrib["TransactionType"], "Update")
        self.assertEquals(doc.tag, "SubjectData")

    def test_only_add_studyeventdata_once(self):
        """Test that a StudyEventData object can only be added once"""
        sed = StudyEventData("V1")
        self.tested << sed
        def do():
            self.tested << sed
        self.assertRaises(ValueError,do)

    def test_only_accepts_studyeventdata(self):
        """Test that only StudyEventData can be inserted"""
        def do():
            self.tested << ItemData("Field1", "ValueC")
        self.assertRaises(ValueError, do)

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
        self.assertEquals("STUDY1", self.tested.projectname)
        self.assertEquals("DEV", self.tested.environment)

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
        self.assertEquals(doc.tag,"ClinicalData")


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
        self.assertEquals(True,self.tested.fileoid is not None)
        self.assertEquals("My test message", self.tested.description)

    def test_assign_fileoid(self):
        """Test if you assign a fileoid it keeps it"""
        tested = ODM("MY TEST SYSTEM", fileoid="F1")
        self.assertEquals("F1", tested.fileoid)

    def test_only_accepts_clinicaldata(self):
        """Test that only ClinicalData can be inserted"""
        def do():
            self.tested << ItemData("Field1", "ValueC")
        self.assertRaises(ValueError,do)

    def test_getroot(self):
        """XML produced"""
        doc = self.tested.getroot()
        self.assertEquals(doc.tag,"ODM")
        self.assertEquals(doc.attrib["Originator"], "MY TEST SYSTEM")
        self.assertEquals(doc.attrib["Description"], self.tested.description)

    def test_str_well_formed(self):
        """Make an XML string from the object, parse it to ensure it's well formed"""
        doc = ET.fromstring(str(self.tested))
        NS_ODM = '{http://www.cdisc.org/ns/odm/v1.3}'
        self.assertEquals(doc.tag,NS_ODM + "ODM")
        self.assertEquals(doc.attrib["Originator"], "MY TEST SYSTEM")
        self.assertEquals(doc.attrib["Description"], self.tested.description)

#-----------------------------------------------------------------------------------------------------------------------
# Metadata object tests

class TestTranslatedText(unittest.TestCase):
    def test_builder(self):
        """XML produced"""
        tested = TranslatedText('en','A test')
        doc = obj_to_doc(tested)
        self.assertEquals(doc.tag, "TranslatedText")
        self.assertEquals("en", doc.attrib['xml:lang'])
        self.assertEquals("A test", doc.text)

    def test_accepts_no_children(self):
        with self.assertRaises(ValueError):
            TranslatedText('en','test') << object()

class TestSymbols(unittest.TestCase):
    def test_can_only_receive_translated_text(self):
        with self.assertRaises(ValueError):
            Symbol() << object()

    def test_translated_text_received(self):
        tested = Symbol()
        tested << TranslatedText('en','Test string')
        self.assertEqual(1, len(tested.translations))

    def test_builder(self):
        """XML produced"""
        tested = Symbol()(TranslatedText('en','Test string'))
        doc = obj_to_doc(tested)
        self.assertEquals(doc.tag, "Symbol")
        self.assertEquals(doc.getchildren()[0].tag, "TranslatedText")

class TestMeasurementUnits(unittest.TestCase):
    def test_basic(self):
        tested = MeasurementUnit('MU_OID', 'MU_NAME')
        self.assertEqual(1, tested.constant_a)
        self.assertEqual(1, tested.constant_b)
        self.assertEqual(0, tested.constant_c)
        self.assertEqual(0, tested.constant_k)
        self.assertEqual(0, len(tested.symbols))

    def test_kg(self):
        tested = MeasurementUnit("MSU00001", "KG", unit_dictionary_name='UN1', standard_unit=True)
        doc = obj_to_doc(tested)
        self.assertEquals(doc.attrib['mdsol:StandardUnit'],"Yes")

    def test_can_only_receive_symbol(self):
        with self.assertRaises(ValueError):
            MeasurementUnit('MU_OID','MU_NAME') << object()

    def test_symbol_received(self):
        tested = MeasurementUnit('MU_OID', 'MU_NAME')
        tested << Symbol()
        self.assertEqual(1, len(tested.symbols))

    def test_builder(self):
        """XML produced"""
        tested = MeasurementUnit('MU_OID', 'MU_NAME')(Symbol())
        doc = obj_to_doc(tested)
        self.assertEquals(doc.tag, "MeasurementUnit")
        self.assertEquals(doc.getchildren()[0].tag, "Symbol")


class TestBasicDefinitions(unittest.TestCase):
    def test_basic(self):
        tested = BasicDefinitions()
        self.assertEqual(0, len(tested.measurement_units))

    def test_mus_onlu(self):
        tested = BasicDefinitions()
        with self.assertRaises(ValueError):
            tested << object()

    def test_mus(self):
        tested = BasicDefinitions()
        tested << MeasurementUnit("MU_OID", "MUNAME")
        self.assertEqual(1, len(tested.measurement_units))

    def test_builder(self):
        """XML produced"""
        tested = BasicDefinitions()(MeasurementUnit("MU_OID", "MUNAME"))
        doc = obj_to_doc(tested)
        self.assertEquals(doc.tag, "BasicDefinitions")
        self.assertEquals(doc.getchildren()[0].tag, "MeasurementUnit")


class TestGlobalVariables(unittest.TestCase):
    """Test Global Variables class"""

    def test_basic(self):
        tested = GlobalVariables('project_name', 'name', 'description')
        self.assertEqual('project_name', tested.protocol_name)
        self.assertEqual('name', tested.name)
        self.assertEqual('description', tested.description)

    def test_defaults(self):
        tested = GlobalVariables('project_name')
        self.assertEqual('project_name', tested.protocol_name)
        self.assertEqual('project_name', tested.name) #Defaults to protocol_name
        self.assertEqual('', tested.description) #Defaults to empty string

    def test_no_children(self):
        """GlobalVariables accepts no children"""
        with self.assertRaises(ValueError):
            GlobalVariables('TEST') << object()

    def test_builder(self):
        """XML produced"""
        tested = GlobalVariables('project_name', description="A description")
        doc = obj_to_doc(tested)
        self.assertEquals(doc.tag, "GlobalVariables")
        self.assertEquals(doc.getchildren()[0].tag, "StudyName")
        self.assertEquals("project_name", doc.getchildren()[0].text)
        self.assertEquals(doc.getchildren()[1].tag, "StudyDescription")
        self.assertEquals("A description", doc.getchildren()[1].text)
        self.assertEquals(doc.getchildren()[2].tag, "ProtocolName")
        self.assertEquals("project_name", doc.getchildren()[2].text)


class TestStudyEventRef(unittest.TestCase):
    def test_cannot_accept_child(self):
        with self.assertRaises(ValueError):
            StudyEventRef("OID",2,False) << object()


class TestProtocol(unittest.TestCase):

    def test_can_accept_studyeventref_child(self):
        se = StudyEventRef('OID',2,True)
        tested = Protocol()(se)
        self.assertEqual(se, tested.study_event_refs[0])

    def test_cannot_accept_non_study_eventref_child(self):
        with self.assertRaises(ValueError):
            Protocol() << object()

    def test_builder(self):
        """XML produced"""
        doc = obj_to_doc(Protocol()(StudyEventRef("OID",1,True)))
        self.assertEquals(doc.tag, "Protocol")
        self.assertEquals(doc.getchildren()[0].tag, "StudyEventRef")


class TestMetaDataVersion(unittest.TestCase):
    """Contains Metadata for study design. Rave only allows one, the spec allows many in an ODM doc"""

    def test_cannot_accept_non_protocol_child(self):
        with self.assertRaises(ValueError):
            MetaDataVersion("OID","NAME") << object()

    def test_can_accept_protocol_child(self):
        prot = Protocol()
        tested = MetaDataVersion("OID","NAME")(prot)
        self.assertEqual(prot, tested.protocol)

    def test_builder(self):
        """XML produced"""
        tested =  MetaDataVersion("OID","NAME", description="A description",
                                  primary_formoid="DM",
                                  default_matrix_oid="DEFAULT",
                                  signature_prompt='I confirm.',
                                  delete_existing=True)

        tested << Protocol()

        doc = obj_to_doc(tested)
        self.assertEquals(doc.tag, "MetaDataVersion")
        self.assertEquals("OID", doc.attrib['OID'])
        self.assertEquals("NAME", doc.attrib['Name'])
        self.assertEquals("A description", doc.attrib['Description'])
        self.assertEquals("DEFAULT", doc.attrib['mdsol:DefaultMatrixOID'])
        self.assertEquals("I confirm.", doc.attrib['mdsol:SignaturePrompt'])
        self.assertEquals("DM", doc.attrib['mdsol:PrimaryFormOID'])
        self.assertEquals("Yes", doc.attrib['mdsol:DeleteExisting'])
        self.assertEquals("Protocol", doc.getchildren()[0].tag)


class TestStudy(unittest.TestCase):
    """Test Study Metadata class"""

    def test_oid(self):
        tested = Study('oid1')
        self.assertEqual('oid1', tested.oid)

    def test_default_project_type(self):
        tested = Study('oid1')
        self.assertEqual('Project', tested.project_type)

    def test_invalid_project_type(self):
        with self.assertRaises(ValueError):
            Study('oid1', project_type='Prijket')

    def test_provided_project_type(self):
        tested = Study('oid1', 'GlobalLibrary Volume')
        self.assertEqual('GlobalLibrary Volume', tested.project_type)

    def test_cannot_accept_itemdata(self):
        tested = Study('oid')
        with self.assertRaises(ValueError):
            tested << ItemData("Field1", "ValueC")

    def test_can_accept_globalvariables(self):
        tested = Study('oid')
        gv = GlobalVariables('MY_TEST_PROJECT')
        tested << gv
        self.assertEqual(gv, tested.global_variables)

    def test_cannot_accept_two_globalvariables(self):
        tested = Study('oid')(GlobalVariables('MY_TEST_PROJECT'))
        with self.assertRaises(ValueError):
            tested << GlobalVariables('Another_one')

    def test_can_accept_basic_definitions(self):
        tested = Study('oid')
        bd = BasicDefinitions()
        tested << bd
        self.assertEqual(bd, tested.basic_definitions)

    def test_cannot_accept_two_basic_definitions(self):
        tested = Study('oid')(BasicDefinitions())
        with self.assertRaises(ValueError):
            tested << BasicDefinitions()

    def test_can_accept_metadata_version(self):
        tested = Study('oid')
        mv = MetaDataVersion('OID','Name')
        tested << mv
        self.assertEqual(mv, tested.metadata_version)

    def test_cannot_accept_two_metadata_versions(self):
        tested = Study('oid')(MetaDataVersion('OID1','NAME1'))
        with self.assertRaises(ValueError):
            tested << MetaDataVersion('OID2','NAME2')

    def test_builder(self):
        """XML produced"""
        tested = Study('oid1', 'GlobalLibrary Volume')(
                                                       GlobalVariables('MY_TEST_PROJECT'),
                                                       BasicDefinitions(),
                                                       MetaDataVersion("OID","NAME")
                                                       )
        doc = obj_to_doc(tested)
        self.assertEquals(doc.tag, "Study")
        self.assertEquals(doc.attrib['mdsol:ProjectType'], "GlobalLibrary Volume")
        self.assertEquals(doc.getchildren()[0].tag, "GlobalVariables")
        self.assertEquals(doc.getchildren()[1].tag, "BasicDefinitions")
        self.assertEquals(doc.getchildren()[2].tag, "MetaDataVersion")

if __name__ == '__main__':
    unittest.main()
