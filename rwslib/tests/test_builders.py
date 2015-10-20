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


if __name__ == '__main__':
    unittest.main()
