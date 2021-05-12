# -*- coding: utf-8 -*-

__author__ = 'isparks'

import unittest

from rwslib.builders.metadata import *
from rwslib.builders.constants import DataType, LogicalRecordPositionType, StepType
from rwslib.builders.clinicaldata import ItemData

from rwslib.tests.test_builders import obj_to_doc

# Metadata object tests


class TestTranslatedText(unittest.TestCase):
    def test_builder(self):
        """XML produced"""
        tested = TranslatedText('A test', lang='en')
        doc = obj_to_doc(tested)
        self.assertEqual(doc.tag, "TranslatedText")
        self.assertEqual("en", doc.attrib['xml:lang'])
        self.assertEqual("A test", doc.text)

    def test_builder_no_lang(self):
        """XML produced when no lang is provided"""
        tested = TranslatedText('A test')
        doc = obj_to_doc(tested)
        self.assertEqual(doc.tag, "TranslatedText")
        self.assertEqual("", doc.get('xml:lang', ''))
        self.assertEqual("A test", doc.text)

    def test_accepts_no_children(self):
        with self.assertRaises(ValueError):
            TranslatedText('test') << object()


class TestSymbols(unittest.TestCase):
    def test_can_only_receive_translated_text(self):
        with self.assertRaises(ValueError):
            Symbol() << object()

    def test_translated_text_received(self):
        tested = Symbol()
        tested << TranslatedText('en', 'Test string')
        self.assertEqual(1, len(tested.translations))

    def test_builder(self):
        """XML produced"""
        tested = Symbol()(TranslatedText('en', 'Test string'))
        doc = obj_to_doc(tested)
        self.assertEqual(doc.tag, "Symbol")
        self.assertEqual(list(doc)[0].tag, "TranslatedText")


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
        self.assertEqual(doc.attrib['mdsol:StandardUnit'], "Yes")

    def test_can_only_receive_symbol(self):
        with self.assertRaises(ValueError):
            MeasurementUnit('MU_OID', 'MU_NAME') << object()

    def test_symbol_received(self):
        tested = MeasurementUnit('MU_OID', 'MU_NAME')
        tested << Symbol()
        self.assertEqual(1, len(tested.symbols))

    def test_builder(self):
        """XML produced"""
        tested = MeasurementUnit('MU_OID', 'MU_NAME')(Symbol())
        doc = obj_to_doc(tested)
        self.assertEqual(doc.tag, "MeasurementUnit")
        self.assertEqual(list(doc)[0].tag, "Symbol")


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
        self.assertEqual(doc.tag, "BasicDefinitions")
        self.assertEqual(list(doc)[0].tag, "MeasurementUnit")


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
        self.assertEqual('project_name', tested.name)  # Defaults to protocol_name
        self.assertEqual('', tested.description)  # Defaults to empty string

    def test_no_children(self):
        """GlobalVariables accepts no children"""
        with self.assertRaises(ValueError):
            GlobalVariables('TEST') << object()

    def test_builder(self):
        """XML produced"""
        tested = GlobalVariables('project_name', description="A description")
        doc = obj_to_doc(tested)
        self.assertEqual(doc.tag, "GlobalVariables")
        self.assertEqual(list(doc)[0].tag, "StudyName")
        self.assertEqual("project_name", list(doc)[0].text)
        self.assertEqual(list(doc)[1].tag, "StudyDescription")
        self.assertEqual("A description", list(doc)[1].text)
        self.assertEqual(list(doc)[2].tag, "ProtocolName")
        self.assertEqual("project_name", list(doc)[2].text)


class TestStudyEventRef(unittest.TestCase):
    def test_cannot_accept_child(self):
        with self.assertRaises(ValueError):
            StudyEventRef("OID", 2, False) << object()

    def test_optional_order_number(self):
        ser = StudyEventRef("OID")
        doc = obj_to_doc(ser)
        self.assertIsNone(doc.get('OrderNumber'))
        self.assertEqual("No", doc.get('Mandatory'))

    def test_zero_order_number(self):
        """Not that it's entirely sensible, but it's cleaner"""
        ser = StudyEventRef("OID", order_number=0)
        doc = obj_to_doc(ser)
        self.assertEqual("0", str(doc.get('OrderNumber')))

    def test_mandatory_study_event_ref(self):
        ser = StudyEventRef("OID", mandatory=True)
        doc = obj_to_doc(ser)
        self.assertIsNone(doc.get('OrderNumber'))
        self.assertEqual("Yes", doc.get('Mandatory'))


class TestProtocol(unittest.TestCase):
    def test_can_accept_studyeventref_child(self):
        se = StudyEventRef('OID', 2, True)
        tested = Protocol()(se)
        self.assertEqual(se, tested.study_event_refs[0])

    def test_cannot_accept_non_study_eventref_child(self):
        with self.assertRaises(ValueError):
            Protocol() << object()

    def test_builder(self):
        """XML produced"""
        doc = obj_to_doc(Protocol()(StudyEventRef("OID", 1, True)))
        self.assertEqual(doc.tag, "Protocol")
        self.assertEqual(list(doc)[0].tag, "StudyEventRef")


class TestFormRef(unittest.TestCase):
    def test_cannot_accept_any_child(self):
        with self.assertRaises(ValueError):
            FormRef('OID', 1, False) << object()


class TestStudyEventDef(unittest.TestCase):
    def test_cannot_accept_non_formref_child(self):
        with self.assertRaises(ValueError):
            StudyEventDef("OID", "Name", False, StudyEventDef.SCHEDULED) << object()

    def test_can_accept_formref_child(self):
        tested = StudyEventDef("OID", "Name", False, StudyEventDef.SCHEDULED)(FormRef("FORMOID", 1, False))
        self.assertEqual(1, len(tested.formrefs))

    def test_builder(self):
        tested = StudyEventDef("OID", "Name", False,
                               StudyEventDef.SCHEDULED,
                               category="Test Cat",
                               access_days=1,
                               start_win_days=2,
                               target_days=3,
                               end_win_days=4,
                               overdue_days=5,
                               close_days=6
                               )
        tested << FormRef("FORMOID", 1, False)

        doc = obj_to_doc(tested)
        self.assertEqual(doc.tag, "StudyEventDef")
        self.assertEqual("OID", doc.attrib['OID'])
        self.assertEqual("Name", doc.attrib['Name'])
        self.assertEqual("Scheduled", doc.attrib['Type'])
        self.assertEqual("Test Cat", doc.attrib['Category'])
        self.assertEqual("1", doc.attrib['mdsol:AccessDays'])
        self.assertEqual("2", doc.attrib['mdsol:StartWinDays'])
        self.assertEqual("3", doc.attrib['mdsol:TargetDays'])
        self.assertEqual("4", doc.attrib['mdsol:EndWinDays'])
        self.assertEqual("5", doc.attrib['mdsol:OverDueDays'])
        self.assertEqual("6", doc.attrib['mdsol:CloseDays'])
        self.assertEqual("FormRef", list(doc)[0].tag)


class TestItemGroupRef(unittest.TestCase):
    def test_accepts_no_children(self):
        with self.assertRaises(ValueError):
            ItemGroupRef("ItemGroup1", 1) << object()

    def test_optional_order_number(self):
        igr = ItemGroupRef("ItemGroup1")
        doc = obj_to_doc(igr)
        self.assertEqual("ItemGroup1", doc.attrib['ItemGroupOID'])
        self.assertNotIn('OrderNumber', doc.attrib)

    def test_builder(self):
        tested = ItemGroupRef("ItemGroup1", 1, mandatory=True)
        doc = obj_to_doc(tested)
        self.assertEqual(doc.tag, "ItemGroupRef")
        self.assertEqual("ItemGroup1", doc.attrib['ItemGroupOID'])
        self.assertEqual("1", doc.attrib['OrderNumber'])
        self.assertEqual("Yes", doc.attrib['Mandatory'])


class TestMdsolHelpTexts(unittest.TestCase):
    def test_build(self):
        tested = MdsolHelpText("en", "This is a help text")
        doc = obj_to_doc(tested)
        self.assertEqual(doc.tag, "mdsol:HelpText")
        self.assertEqual("en", doc.attrib['xml:lang'])
        self.assertEqual("This is a help text", doc.text)

    def test_accepts_no_children(self):
        with self.assertRaises(ValueError):
            MdsolHelpText("en", "Content") << object()


class TestMdsolViewRestriction(unittest.TestCase):
    def test_accepts_no_children(self):
        with self.assertRaises(ValueError):
            MdsolViewRestriction("CRA") << object()

    def test_build(self):
        tested = MdsolViewRestriction("DM")
        doc = obj_to_doc(tested)
        self.assertEqual(doc.tag, "mdsol:ViewRestriction")
        self.assertEqual("DM", doc.text)


class TestMdsolEntryRestriction(unittest.TestCase):
    def test_accepts_no_children(self):
        with self.assertRaises(ValueError):
            MdsolEntryRestriction("CRA") << object()

    def test_build(self):
        tested = MdsolEntryRestriction("DM")
        doc = obj_to_doc(tested)
        self.assertEqual(doc.tag, "mdsol:EntryRestriction")
        self.assertEqual("DM", doc.text)


class TestMdsolLabelRef(unittest.TestCase):
    def test_accepts_no_children(self):
        with self.assertRaises(ValueError):
            MdsolLabelRef("LABEL1", 1) << object()

    def test_build(self):
        tested = MdsolLabelRef("OID1", 1)

        doc = obj_to_doc(tested)
        self.assertEqual(doc.tag, "mdsol:LabelRef")
        self.assertEqual("OID1", doc.attrib['LabelOID'])
        self.assertEqual("1", doc.attrib['OrderNumber'])


class TestMdsolAttribute(unittest.TestCase):
    def test_accepts_no_children(self):
        with self.assertRaises(ValueError):
            MdsolAttribute("Namespace", "Name", "Value") << object()


class TestItemRef(unittest.TestCase):
    def test_accepts_no_children(self):
        with self.assertRaises(ValueError):
            ItemRef("OID", 1) << object()

    def test_build(self):
        tested = ItemRef("OID1", 1,
                         key_sequence=3,
                         imputation_method_oid='IMPUTE1',
                         role="AROLE",
                         role_codelist_oid='ROLEX')

        tested << MdsolAttribute("Namespace", "Name", "Value")
        tested << MdsolAttribute("Namespace2", "Name2", "Value2")

        doc = obj_to_doc(tested)
        self.assertEqual(doc.tag, "ItemRef")
        self.assertEqual("OID1", doc.attrib['ItemOID'])
        self.assertEqual("1", doc.attrib['OrderNumber'])
        self.assertEqual("3", doc.attrib['KeySequence'])
        self.assertEqual("IMPUTE1", doc.attrib['ImputationMethodOID'])
        self.assertEqual("AROLE", doc.attrib['Role'])
        self.assertEqual("ROLEX", doc.attrib['RoleCodeListOID'])
        self.assertEqual("mdsol:Attribute", list(doc)[0].tag)
        self.assertEqual("mdsol:Attribute", list(doc)[1].tag)


class TestQuestion(unittest.TestCase):
    def test_cannot_accept_non_translation_child(self):
        with self.assertRaises(ValueError):
            Question() << object()

    def test_can_accept_translation_child(self):
        tested = Question()(TranslatedText("How do you feel today?"))
        self.assertEqual(1, len(tested.translations))

    def test_build(self):
        tested = Question()(TranslatedText('How are you feeling?'))
        doc = obj_to_doc(tested)
        self.assertEqual(doc.tag, "Question")
        self.assertEqual("TranslatedText", list(doc)[0].tag)


class TestMeasurementUnitRef(unittest.TestCase):
    def test_cannot_accept_child(self):
        with self.assertRaises(ValueError):
            MeasurementUnitRef("KG") << object()

    def test_build(self):
        tested = MeasurementUnitRef("KG")
        doc = obj_to_doc(tested)
        self.assertEqual(doc.tag, "MeasurementUnitRef")
        self.assertEqual("KG", doc.attrib['MeasurementUnitOID'])


class TestCodeListRef(unittest.TestCase):
    def test_cannot_accept_child(self):
        with self.assertRaises(ValueError):
            CodeListRef("SEV") << object()

    def test_build(self):
        tested = CodeListRef("SEVERITY")
        doc = obj_to_doc(tested)
        self.assertEqual(doc.tag, "CodeListRef")
        self.assertEqual("SEVERITY", doc.attrib['CodeListOID'])


class TestMdsolReviewGroup(unittest.TestCase):
    def test_accepts_no_children(self):
        with self.assertRaises(ValueError):
            MdsolReviewGroup("DM") << object()


    def test_build(self):
        doc = obj_to_doc(MdsolReviewGroup("CRA"))
        self.assertEqual(doc.tag, "mdsol:ReviewGroup")
        self.assertEqual("CRA", doc.text)


class TestMdsolLabelDef(unittest.TestCase):
    def setUp(self):
        self.tested = MdsolLabelDef("L_AGE", "Age Label", field_number=4)

    def test_accepts_no_strange_children(self):
        with self.assertRaises(ValueError):
            self.tested << object()

    def test_accepts_view_restriction(self):
        self.tested << MdsolViewRestriction("DM")
        self.assertEqual(1, len(self.tested.view_restrictions))

    def test_accepts_translated_text(self):
        tt = TranslatedText("Hello")
        self.tested << tt
        self.assertEqual(tt, self.tested.translations[0])

    def test_build(self):
        self.tested << TranslatedText("Please answer all questions")
        self.tested << MdsolViewRestriction("DM")

        doc = obj_to_doc(self.tested)
        self.assertEqual(doc.tag, "mdsol:LabelDef")
        self.assertEqual("L_AGE", doc.attrib['OID'])
        self.assertEqual("Age Label", doc.attrib['Name'])
        self.assertEqual("4", doc.attrib['FieldNumber'])
        self.assertEqual("TranslatedText", list(doc)[0].tag)
        self.assertEqual("mdsol:ViewRestriction", list(doc)[1].tag)


class TestCheckValue(unittest.TestCase):
    def test_accepts_no_children(self):
        with self.assertRaises(ValueError):
            CheckValue("Test") << object()

    def test_build(self):
        doc = obj_to_doc(CheckValue(99))
        self.assertEqual(doc.tag, "CheckValue")
        self.assertEqual("99", doc.text)


class TestRangeCheck(unittest.TestCase):
    def test_accepts_no_strange_children(self):
        with self.assertRaises(ValueError):
            RangeCheck(comparator=RangeCheckComparatorType.GreaterThanEqualTo,
                       soft_hard=RangeCheckType.Soft) << object()

    def test_accepts_no_strange_soft_hard(self):
        with self.assertRaises(AttributeError):
            RangeCheck(comparator=RangeCheckComparatorType.GreaterThanEqualTo, soft_hard="Blash")

    def test_accepts_no_strange_comparator(self):
        with self.assertRaises(AttributeError):
            RangeCheck(comparator="EQ", soft_hard="Blash")

    def test_accepts_checkvalue(self):
        tested = RangeCheck(comparator=RangeCheckComparatorType.LessThanEqualTo, soft_hard=RangeCheckType.Soft)
        cv = CheckValue(0)
        tested << cv
        self.assertEqual(cv, tested.check_value)

    def test_accepts_measurement_unit_ref(self):
        tested = RangeCheck(comparator=RangeCheckComparatorType.GreaterThanEqualTo, soft_hard=RangeCheckType.Soft)
        mr = MeasurementUnitRef('kg')
        tested << mr
        self.assertEqual(mr, tested.measurement_unit_ref)

    def test_build(self):
        self.tested = RangeCheck(comparator=RangeCheckComparatorType.GreaterThanEqualTo, soft_hard=RangeCheckType.Soft)
        self.tested << CheckValue(0)
        self.tested << MeasurementUnitRef('kg')

        doc = obj_to_doc(self.tested)
        self.assertEqual("RangeCheck", doc.tag)
        self.assertEqual("Soft", doc.attrib['SoftHard'])
        self.assertEqual("GE", doc.attrib['Comparator'])
        self.assertEqual("CheckValue", list(doc)[0].tag)
        self.assertEqual("MeasurementUnitRef", list(doc)[1].tag)


class TestMdsolHeaderText(unittest.TestCase):
    def test_lang_default(self):
        tested = MdsolHeaderText("Content", "en")
        self.assertEqual("en", tested.lang)
        doc = obj_to_doc(tested)
        self.assertEqual("mdsol:HeaderText", doc.tag)
        self.assertEqual("Content", doc.text)
        self.assertEqual("en", doc.attrib['xml:lang'])


class TestItemDef(unittest.TestCase):
    def setUp(self):
        self.tested = ItemDef("I_AGE", "Age", DataType.Integer, 3,
                              significant_digits=3,
                              sas_field_name='SAGE',
                              sds_var_name='SVARNAME',
                              sas_format="3.0",
                              sas_label='AGE_YRS',
                              source_document_verify=True,
                              query_future_date=False,
                              visible=True,
                              translation_required=True,
                              query_non_conformance=True,
                              other_visits=False,
                              can_set_item_group_date=False,
                              can_set_form_date=False,
                              can_set_study_event_date=False,
                              can_set_subject_date=False,
                              visual_verify=True,
                              does_not_break_signature=True,
                              acceptable_file_extensions='jpg',
                              control_type=ControlType.Text,
                              variable_oid='SOMETHING_DIFFERENT',
                              default_value=99,
                              origin='An origin',
                              comment='A comment',
                              date_time_format='mmm yy dd',
                              field_number='10'
                              )

    def test_accepts_no_strange_children(self):
        with self.assertRaises(ValueError):
            self.tested << object()

    def test_invalid_datatype(self):
        with self.assertRaises(AttributeError):
            ItemDef("TEST", "My Test", "TOTALLY_WRONG_DATATYPE", 10)

    def test_invalid_controltype(self):
        with self.assertRaises(AttributeError):
            ItemDef("TEST", "My Test", DataType.Text, 10, control_type="TOTALLY_WRONG_CONTROLTYPE")

    def test_invalid_integer_missing_length(self):
        """Test that integer type raises error if no length set"""
        with self.assertRaises(AttributeError):
            ItemDef("TEST", "My Test", DataType.Integer)

    def test_invalid_text_missing_length(self):
        """Test that text type raises error if no length set"""
        with self.assertRaises(AttributeError):
            ItemDef("TEST", "My Test", DataType.Text)

    def test_valid_date_missing_length(self):
        """Test that dates are defaulted to length of their format"""
        id = ItemDef("TEST", "My Test", DataType.Date, date_time_format="mmm dd yy")
        self.assertEqual(9, id.length)

    def test_accepts_mdsolhelp(self):
        self.tested << MdsolHelpText("en", "Content of help")
        self.assertEqual(1, len(self.tested.help_texts))

    def test_accepts_view_restriction(self):
        self.tested << MdsolViewRestriction("DM")
        self.assertEqual(1, len(self.tested.view_restrictions))

    def test_accepts_header_text(self):
        ht = MdsolHeaderText("KILOs")
        self.tested << ht
        self.assertEqual(ht, self.tested.header_text)

    def test_does_not_accept_two_header_texts(self):
        h1 = MdsolHeaderText("One")
        h2 = MdsolHeaderText("Two")
        self.tested << h1
        with self.assertRaises(ValueError):
            self.tested << h2

    def test_accepts_measurement_unit_ref(self):
        mu = MeasurementUnitRef("KG")
        self.tested << mu
        self.assertEqual(1, len(self.tested.measurement_unit_refs))

    def test_accepts_question(self):
        q = Question()
        self.tested << q
        self.assertEqual(q, self.tested.question)

    def test_does_not_accept_two_questions(self):
        q1 = Question()
        q2 = Question()
        self.tested << q1
        with self.assertRaises(ValueError):
            self.tested << q2

    def test_accepts_codelistref(self):
        cl = CodeListRef("SEVERITY")
        self.tested << cl
        self.assertEqual(cl, self.tested.codelistref)

    def test_does_not_accept_two_codelists(self):
        cl1 = CodeListRef("SEVERITY")
        cl2 = CodeListRef("STATUS")
        self.tested << cl1
        with self.assertRaises(ValueError):
            self.tested << cl2

    def test_accepts_entry_restriction(self):
        self.tested << MdsolEntryRestriction("CRA")
        self.assertEqual(1, len(self.tested.entry_restrictions))

    def test_accepts_review_group(self):
        self.tested << MdsolReviewGroup("CRA")
        self.assertEqual(1, len(self.tested.review_groups))

    def test_accepts_range_check(self):
        self.tested << RangeCheck(RangeCheckComparatorType.LessThanEqualTo, RangeCheckType.Soft)
        self.assertEqual(1, len(self.tested.range_checks))

    def test_build(self):
        self.tested << Question()(TranslatedText("How do you feel today?"))
        self.tested << CodeListRef("SCALE_1")
        self.tested << MeasurementUnitRef("Years")
        self.tested << MdsolHelpText("en", "Content of help")
        self.tested << MdsolViewRestriction("DM")
        self.tested << MdsolEntryRestriction("CRA")
        self.tested << MdsolHeaderText("YRS")
        self.tested << MdsolReviewGroup("CRA")
        self.tested << RangeCheck(RangeCheckComparatorType.LessThanEqualTo, RangeCheckType.Soft)

        doc = obj_to_doc(self.tested)
        self.assertEqual(doc.tag, "ItemDef")
        self.assertEqual("I_AGE", doc.attrib['OID'])
        self.assertEqual("Age", doc.attrib['Name'])
        self.assertEqual("Yes", doc.attrib['mdsol:Active'])
        self.assertEqual("integer", doc.attrib['DataType'])
        self.assertEqual("3", doc.attrib['Length'])
        self.assertEqual("Text", doc.attrib['mdsol:ControlType'])
        self.assertEqual("3", doc.attrib['SignificantDigits'])
        self.assertEqual("SAGE", doc.attrib['SASFieldName'])
        self.assertEqual("SVARNAME", doc.attrib['SDSVarName'])
        self.assertEqual("AGE_YRS", doc.attrib['mdsol:SASLabel'])
        self.assertEqual("3.0", doc.attrib['mdsol:SASFormat'])
        self.assertEqual("A comment", doc.attrib['Comment'])
        self.assertEqual("An origin", doc.attrib['Origin'])
        self.assertEqual("No", doc.attrib['mdsol:QueryFutureDate'])
        self.assertEqual("Yes", doc.attrib['mdsol:Visible'])
        self.assertEqual("Yes", doc.attrib['mdsol:TranslationRequired'])
        self.assertEqual("Yes", doc.attrib['mdsol:SourceDocument'])
        self.assertEqual("No", doc.attrib['mdsol:OtherVisits'])
        self.assertEqual("Yes", doc.attrib['mdsol:SourceDocument'])
        self.assertEqual("Yes", doc.attrib['mdsol:QueryNonConformance'])
        self.assertEqual("No", doc.attrib['mdsol:CanSetItemGroupDate'])
        self.assertEqual("No", doc.attrib['mdsol:CanSetFormDate'])
        self.assertEqual("No", doc.attrib['mdsol:CanSetStudyEventDate'])
        self.assertEqual("No", doc.attrib['mdsol:CanSetSubjectDate'])
        self.assertEqual("Yes", doc.attrib['mdsol:VisualVerify'])
        self.assertEqual("Yes", doc.attrib['mdsol:DoesNotBreakSignature'])
        self.assertEqual("SOMETHING_DIFFERENT", doc.attrib['mdsol:VariableOID'])
        self.assertEqual("jpg", doc.attrib['mdsol:AcceptableFileExtensions'])
        self.assertEqual("99", doc.attrib['mdsol:DefaultValue'])
        self.assertEqual("mmm yy dd", doc.attrib['mdsol:DateTimeFormat'])
        self.assertEqual("10", doc.attrib['mdsol:FieldNumber'])

        self.assertEqual("Question", list(doc)[0].tag)
        self.assertEqual("CodeListRef", list(doc)[1].tag)
        self.assertEqual("MeasurementUnitRef", list(doc)[2].tag)
        self.assertEqual("RangeCheck", list(doc)[3].tag)
        self.assertEqual("mdsol:HeaderText", list(doc)[4].tag)
        self.assertEqual("mdsol:ViewRestriction", list(doc)[5].tag)
        self.assertEqual("mdsol:EntryRestriction", list(doc)[6].tag)
        self.assertEqual("mdsol:HelpText", list(doc)[7].tag)
        self.assertEqual("mdsol:ReviewGroup", list(doc)[8].tag)


class TestItemGroupDef(unittest.TestCase):
    def test_does_notaccept_non_itemref_child(self):
        with self.assertRaises(ValueError):
            ItemGroupDef("DM", "Demog") << object()

    def test_accepts_itemref_child(self):
        tested = ItemGroupDef("DM", "Demog")
        tested << ItemRef("OID1", "1")
        tested << MdsolLabelRef("LABEL1", 2)

        self.assertEqual(1, len(tested.item_refs))
        self.assertEqual(1, len(tested.label_refs))

    def test_build(self):
        tested = ItemGroupDef("DM", "Demography",
                              repeating=True,
                              is_reference_data=True,
                              sas_dataset_name='DMSAS',
                              domain='TESTDOMAIN',
                              origin='TESTORIGIN',
                              role='TESTROLE',
                              purpose='TESTPURPOSE',
                              comment='A comment')

        tested << ItemRef("OID1", 1)
        tested << MdsolLabelRef("LABEL1", 2)

        doc = obj_to_doc(tested)
        self.assertEqual(doc.tag, "ItemGroupDef")
        self.assertEqual("DM", doc.attrib['OID'])
        self.assertEqual("Yes", doc.attrib['Repeating'])
        self.assertEqual("Yes", doc.attrib['IsReferenceData'])
        self.assertEqual("Demography", doc.attrib['Name'])
        self.assertEqual("DMSAS", doc.attrib['SASDatasetName'])
        self.assertEqual("TESTDOMAIN", doc.attrib['Domain'])
        self.assertEqual("TESTORIGIN", doc.attrib['Origin'])
        self.assertEqual("TESTROLE", doc.attrib['Role'])
        self.assertEqual("TESTPURPOSE", doc.attrib['Purpose'])
        self.assertEqual("A comment", doc.attrib['Comment'])
        self.assertEqual("ItemRef", list(doc)[0].tag)
        self.assertEqual("mdsol:LabelRef", list(doc)[1].tag)


class TestFormDef(unittest.TestCase):
    def test_only_accept_itemgroup_ref(self):
        with self.assertRaises(ValueError):
            FormDef("VS", "Vital Signs") << object()

    def test_accept_itemgroup_ref(self):
        tested = FormDef("DM", "Demog", order_number=1)(ItemGroupRef("ItemGroup1", 1))
        self.assertEqual(1, len(tested.itemgroup_refs))

    def test_builder(self):
        tested = FormDef("DM", "Demog", repeating=True,
                         order_number=2,
                         link_form_oid='FRM1',
                         link_study_event_oid='EVT1')

        tested << ItemGroupRef("ItemGroup1", 1)
        tested << MdsolHelpText("en", "This is a help text")
        tested << MdsolViewRestriction("DM")
        tested << MdsolEntryRestriction("CRA")

        doc = obj_to_doc(tested)
        self.assertEqual(doc.tag, "FormDef")
        self.assertEqual("DM", doc.attrib['OID'])
        self.assertEqual("Demog", doc.attrib['Name'])
        self.assertEqual("Yes", doc.attrib['Repeating'])
        self.assertEqual("2", doc.attrib['mdsol:OrderNumber'])
        # Would not see LinkFormOID and LinkStudyEventOID together, they are mutually exclusive. Just for coverage.
        self.assertEqual("FRM1", doc.attrib['mdsol:LinkFormOID'])
        self.assertEqual("EVT1", doc.attrib['mdsol:LinkStudyEventOID'])
        self.assertEqual("ItemGroupRef", list(doc)[0].tag)
        self.assertEqual("mdsol:HelpText", list(doc)[1].tag)
        self.assertEqual("mdsol:ViewRestriction", list(doc)[2].tag)
        self.assertEqual("mdsol:EntryRestriction", list(doc)[3].tag)


class TestDecode(unittest.TestCase):
    def test_cannot_accept_non_translated_text(self):
        with self.assertRaises(ValueError):
            Decode() << object()

    def test_accepts_decode(self):
        tested = Decode()
        tt = TranslatedText("Yes")
        tested.add(tt)
        self.assertEqual(tt, tested.translations[0])

    def test_builder(self):
        """XML produced"""
        tested = Decode()
        tested << TranslatedText("Yes")
        doc = obj_to_doc(tested)
        self.assertEqual("Decode", doc.tag)
        self.assertEqual("TranslatedText", list(doc)[0].tag)


class TestCodeListItem(unittest.TestCase):
    def test_cannot_accept_non_decode(self):
        with self.assertRaises(ValueError):
            CodeListItem("M") << object()

    def test_accepts_decode(self):
        tested = CodeListItem("N")
        decode = Decode()
        tested.add(decode)
        self.assertEqual(decode, tested.decode)

    def test_builder_basic(self):
        """XML produced"""
        tested = CodeListItem("Y")
        tested << Decode()
        doc = obj_to_doc(tested)
        self.assertEqual("CodeListItem", doc.tag)
        self.assertEqual("", doc.get('mdsol:Specify', ''))
        self.assertEqual("", doc.get('mdsol:OrderNumber', ''))
        self.assertEqual("Y", doc.attrib['CodedValue'])
        self.assertEqual("Decode", list(doc)[0].tag)

    def test_builder_order_specify(self):
        """XML produced with optional params set"""
        tested = CodeListItem("Y", order_number=1, specify=True)
        tested << Decode()
        doc = obj_to_doc(tested)
        self.assertEqual("CodeListItem", doc.tag)
        self.assertEqual("Yes", doc.attrib['mdsol:Specify'])
        self.assertEqual("1", doc.attrib['mdsol:OrderNumber'])
        self.assertEqual("Y", doc.attrib['CodedValue'])
        self.assertEqual("Decode", list(doc)[0].tag)


class TestCodeList(unittest.TestCase):
    """Codelists contain codelistitems"""

    def test_cannot_accept_non_codelistitem(self):
        with self.assertRaises(ValueError):
            CodeList("CL1", "Codelist1", DataType.Integer) << object()

    def test_invalid_datatype(self):
        with self.assertRaises(ValueError):
            CodeList("CL1", "Codelist1", "IncorrectDataType")

    def test_accepts_codelistitem(self):
        tested = CodeList("CL1", "Codelist1", DataType.Integer)
        cl1 = CodeListItem("1")
        tested.add(cl1)
        self.assertEqual(cl1, tested.codelist_items[0])

    def test_builder(self):
        """XML produced"""
        tested = CodeList("CL_YN", "YesNo", DataType.String, sas_format_name="YESNO_CL")
        tested << CodeListItem("Y")
        doc = obj_to_doc(tested)
        self.assertEqual("CodeList", doc.tag)
        self.assertEqual(DataType.String.value, doc.attrib['DataType'])
        self.assertEqual("YESNO_CL", doc.attrib['SASFormatName'])
        self.assertEqual("CodeListItem", list(doc)[0].tag)


class TestConfirmationMessage(unittest.TestCase):
    def test_build(self):
        cm = MdsolConfirmationMessage("Form saved.")
        doc = obj_to_doc(cm)
        self.assertEqual("mdsol:ConfirmationMessage", doc.tag)
        self.assertEqual("Form saved.", doc.text)

    def test_lang_set(self):
        cm = MdsolConfirmationMessage("Form saved.", lang="en")
        doc = obj_to_doc(cm)
        self.assertEqual("en", doc.attrib['xml:lang'])


class TestMdsolCheckAction(unittest.TestCase):
    """Test extensions to ODM for Edit Checks Steps in Rave"""

    def test_build(self):
        tested = MdsolCheckAction(
            field_oid="Field",
            variable_oid="TheVAR",
            form_oid="The Form",
            form_repeat_number=1,
            folder_oid="The Folder",
            folder_repeat_number=2,
            record_position=3,
            check_action_type=ActionType.SetDataPoint,
            check_string="CString",  # Knowing which of these to use for each action type is
            check_script="CScript",  # the trick. Best to look in an Architect Loader Spreadsheet
            check_options="COptions")  # to get an idea
        doc = obj_to_doc(tested)
        self.assertEqual("mdsol:CheckAction", doc.tag)
        self.assertEqual("The Folder", doc.attrib['FolderOID'])
        self.assertEqual("The Form", doc.attrib['FormOID'])
        self.assertEqual("Field", doc.attrib['FieldOID'])
        self.assertEqual("TheVAR", doc.attrib['VariableOID'])
        self.assertEqual("1", doc.attrib['FormRepeatNumber'])
        self.assertEqual("2", doc.attrib['FolderRepeatNumber'])
        self.assertEqual("3", doc.attrib['RecordPosition'])
        self.assertEqual("CString", doc.attrib['String'])
        self.assertEqual("CScript", doc.attrib['Script'])
        self.assertEqual("COptions", doc.attrib['Options'])
        self.assertEqual(ActionType.SetDataPoint.value, doc.attrib['Type'])

    def test_invalid_action(self):
        with self.assertRaises(AttributeError):
            MdsolCheckAction(check_action_type='bad_name')


class TestMdsolCheckStep(unittest.TestCase):
    """Test extensions to ODM for Edit Checks Steps in Rave"""

    def test_build(self):
        tested = MdsolCheckStep(data_format="$1", static_value="1")
        doc = obj_to_doc(tested)
        self.assertEqual("mdsol:CheckStep", doc.tag)
        self.assertEqual("$1", doc.attrib['DataFormat'])
        self.assertEqual("1", doc.attrib['StaticValue'])
        # No function param
        self.assertEqual("", doc.attrib.get('Function', ''))

    def test_build_function(self):
        tested = MdsolCheckStep(function=StepType.Add)
        doc = obj_to_doc(tested)
        self.assertEqual("mdsol:CheckStep", doc.tag)
        self.assertEqual(StepType.Add.value, doc.attrib['Function'])
        # No data format param
        self.assertEqual("", doc.attrib.get('DataFormat', ''))

    def test_build_datastep(self):
        tested = MdsolCheckStep(variable_oid="VAROID", field_oid="FIELDOID",
                                form_oid="MyForm",
                                folder_oid="MyFolder",
                                record_position=0, form_repeat_number=2, folder_repeat_number=3,
                                logical_record_position=LogicalRecordPositionType.MaxBySubject)
        doc = obj_to_doc(tested)
        self.assertEqual("mdsol:CheckStep", doc.tag)
        self.assertEqual("VAROID", doc.attrib['VariableOID'])
        self.assertEqual("FIELDOID", doc.attrib['FieldOID'])
        self.assertEqual("MyForm", doc.attrib['FormOID'])
        self.assertEqual("MyFolder", doc.attrib['FolderOID'])
        self.assertEqual("0", doc.attrib['RecordPosition'])
        self.assertEqual("2", doc.attrib['FormRepeatNumber'])
        self.assertEqual("3", doc.attrib['FolderRepeatNumber'])
        self.assertEqual("MaxBySubject", doc.attrib['LogicalRecordPosition'])
        # No data format param
        self.assertEqual("", doc.attrib.get('DataFormat', ''))
        # No function param
        self.assertEqual("", doc.attrib.get('Function', ''))

    def test_build_custom_function(self):
        tested = MdsolCheckStep(custom_function="AlwaysTrue*")
        doc = obj_to_doc(tested)
        self.assertEqual("mdsol:CheckStep", doc.tag)
        self.assertEqual("AlwaysTrue*", doc.attrib['CustomFunction'])
        # No data format param
        self.assertEqual("", doc.attrib.get('DataFormat', ''))
        # No function param
        self.assertEqual("", doc.attrib.get('Function', ''))

    def test_invalid_function(self):
        with self.assertRaises(AttributeError):
            MdsolCheckStep(function='bad_name')

    def test_create_with_valid_lrp(self):
        """We create a function with a valid LRP value"""
        tested = MdsolCheckStep(custom_function="AlwaysTrue*",
                                logical_record_position=LogicalRecordPositionType.Last)
        doc = obj_to_doc(tested)
        self.assertEqual("mdsol:CheckStep", doc.tag)
        self.assertEqual("AlwaysTrue*", doc.attrib['CustomFunction'])
        self.assertEqual("Last", doc.attrib['LogicalRecordPosition'])

    def test_create_with_invalid_lrp(self):
        """We create a function with an invalid LRP value"""
        with self.assertRaises(AttributeError) as exc:
            tested = MdsolCheckStep(custom_function="AlwaysTrue*",
                                    logical_record_position='Wibble')
        self.assertEqual("Invalid Check Step Logical Record Position Wibble",
                         str(exc.exception))


class TestMdsolEditCheckDef(unittest.TestCase):
    """Test extensions to ODM for Edit Checks in Rave"""

    def test_build(self):
        tested = MdsolEditCheckDef("CHECK1")

        tested << MdsolCheckStep(data_format="$1", static_value="1")
        tested << MdsolCheckAction()

        doc = obj_to_doc(tested)
        self.assertEqual("mdsol:EditCheckDef", doc.tag)
        self.assertEqual("TRUE", doc.attrib['Active'])
        self.assertEqual("CHECK1", doc.attrib['OID'])
        self.assertEqual("FALSE", doc.attrib['NeedsRetesting'])
        self.assertEqual("FALSE", doc.attrib['BypassDuringMigration'])
        self.assertEqual("mdsol:CheckStep", list(doc)[0].tag)
        self.assertEqual("mdsol:CheckAction", list(doc)[1].tag)

    def test_cannot_accept_non_check_or_action_child(self):
        with self.assertRaises(ValueError):
            MdsolEditCheckDef("OID") << object()

    def test_accepts_check_step(self):
        tested = MdsolEditCheckDef("CHECK1")
        cs = MdsolCheckStep(data_format="$1", static_value="1")
        tested << cs
        self.assertEqual(cs, tested.check_steps[0])

    def test_accepts_check_action(self):
        tested = MdsolEditCheckDef("CHECK1")
        ca = MdsolCheckAction()
        tested << ca
        self.assertEqual(ca, tested.check_actions[0])


class TestMdsolDerivationStep(unittest.TestCase):
    """Test extensions to ODM for Derivation Steps in Rave"""

    def test_build(self):
        """
        We build a Derivation Value Step
        """
        tested = MdsolDerivationStep(data_format="$1", value="1")
        doc = obj_to_doc(tested)
        self.assertEqual("mdsol:DerivationStep", doc.tag)
        self.assertEqual("$1", doc.attrib['DataFormat'])
        self.assertEqual("1", doc.attrib['Value'])
        # No function param
        self.assertEqual("", doc.attrib.get('Function', ''))

    def test_build_function(self):
        """We build a Derivation Function Step"""
        tested = MdsolDerivationStep(function=StepType.Add)
        doc = obj_to_doc(tested)
        self.assertEqual("mdsol:DerivationStep", doc.tag)
        self.assertEqual(StepType.Add.value, doc.attrib['Function'])
        # No data format param
        self.assertEqual("", doc.attrib.get('DataFormat', ''))

    def test_build_datastep(self):
        """We build a Derivation Data Step"""
        tested = MdsolDerivationStep(variable_oid="VAROID", field_oid="FIELDOID",
                                     form_oid="VFORM",
                                     folder_oid="MyFolder",
                                     record_position=0, form_repeat_number=2, folder_repeat_number=3,
                                     logical_record_position=LogicalRecordPositionType.MaxBySubject)
        doc = obj_to_doc(tested)
        self.assertEqual("mdsol:DerivationStep", doc.tag)
        self.assertEqual("VAROID", doc.attrib['VariableOID'])
        self.assertEqual("FIELDOID", doc.attrib['FieldOID'])
        self.assertEqual("VFORM", doc.attrib['FormOID'])
        self.assertEqual("MyFolder", doc.attrib['FolderOID'])
        self.assertEqual("0", doc.attrib['RecordPosition'])
        self.assertEqual("2", doc.attrib['FormRepeatNumber'])
        self.assertEqual("3", doc.attrib['FolderRepeatNumber'])
        self.assertEqual("MaxBySubject", doc.attrib['LogicalRecordPosition'])
        # No data format param
        self.assertEqual("", doc.attrib.get('DataFormat', ''))
        # No function param
        self.assertEqual("", doc.attrib.get('Function', ''))

    def test_build_custom_function(self):
        """We build a Custom Function Step"""
        tested = MdsolDerivationStep(custom_function="AlwaysTrue*")
        doc = obj_to_doc(tested)
        self.assertEqual("mdsol:DerivationStep", doc.tag)
        self.assertEqual("AlwaysTrue*", doc.attrib['CustomFunction'])
        # No data format param
        self.assertEqual("", doc.attrib.get('DataFormat', ''))
        # No function param
        self.assertEqual("", doc.attrib.get('Function', ''))

    def test_invalid_function(self):
        """Trying to create a Derivation with an invalid step raises an exception"""
        with self.assertRaises(AttributeError):
            # StepType.IsPresent not valid for DerivationStep
            MdsolDerivationStep(function=StepType.IsPresent)

    def test_create_with_valid_lrp(self):
        """We create a function with a valid LRP value"""
        tested = MdsolDerivationStep(custom_function="AlwaysTrue*",
                                     logical_record_position=LogicalRecordPositionType.Last)
        doc = obj_to_doc(tested)
        self.assertEqual("mdsol:DerivationStep", doc.tag)
        self.assertEqual("AlwaysTrue*", doc.attrib['CustomFunction'])
        self.assertEqual("Last", doc.attrib['LogicalRecordPosition'])

    def test_create_with_invalid_lrp(self):
        """We create a function with an invalid LRP value"""
        with self.assertRaises(AttributeError) as exc:
            tested = MdsolDerivationStep(custom_function="AlwaysTrue*",
                                         logical_record_position='Wibble')
        self.assertEqual("Invalid Derivation Logical Record Position Wibble",
                         str(exc.exception))


class TestMdsolDerivationDef(unittest.TestCase):
    """Test extensions to ODM for Derivations in Rave"""

    def test_build(self):
        tested = MdsolDerivationDef("AGE",
                                    variable_oid="VAROID", field_oid="FIELDOID",
                                    form_oid="MyForm",
                                    folder_oid="MyFolder",
                                    record_position=0, form_repeat_number=2, folder_repeat_number=3,
                                    logical_record_position=LogicalRecordPositionType.MaxBySubject,
                                    all_variables_in_fields=True,
                                    all_variables_in_folders=True)
        doc = obj_to_doc(tested)
        tested << MdsolDerivationStep(function=StepType.Age)

        doc = obj_to_doc(tested)
        self.assertEqual("mdsol:DerivationDef", doc.tag)
        self.assertEqual("TRUE", doc.attrib['Active'])
        self.assertEqual("AGE", doc.attrib['OID'])
        self.assertEqual("FALSE", doc.attrib['NeedsRetesting'])
        self.assertEqual("FALSE", doc.attrib['BypassDuringMigration'])
        self.assertEqual("TRUE", doc.attrib['AllVariablesInFolders'])
        self.assertEqual("TRUE", doc.attrib['AllVariablesInFields'])
        self.assertEqual("VAROID", doc.attrib['VariableOID'])
        self.assertEqual("FIELDOID", doc.attrib['FieldOID'])
        self.assertEqual("MyForm", doc.attrib['FormOID'])
        self.assertEqual("MyFolder", doc.attrib['FolderOID'])
        self.assertEqual("0", doc.attrib['RecordPosition'])
        self.assertEqual("2", doc.attrib['FormRepeatNumber'])
        self.assertEqual("3", doc.attrib['FolderRepeatNumber'])
        self.assertEqual("MaxBySubject", doc.attrib['LogicalRecordPosition'])

        self.assertEqual("mdsol:DerivationStep", list(doc)[0].tag)

    def test_cannot_accept_any_child(self):
        with self.assertRaises(ValueError):
            MdsolDerivationDef("OID") << object()

    def test_accepts_derivation_step(self):
        tested = MdsolDerivationDef("AGE")
        ds = MdsolDerivationStep(function=StepType.Age)
        tested << ds
        self.assertEqual(ds, tested.derivation_steps[0])

    def test_create_with_valid_lrp(self):
        """We create a function with a valid LRP value"""
        tested = MdsolDerivationDef('TANK',
                                    logical_record_position=LogicalRecordPositionType.Last)
        doc = obj_to_doc(tested)
        self.assertEqual("mdsol:DerivationDef", doc.tag)
        self.assertEqual("Last", doc.attrib['LogicalRecordPosition'])

    def test_create_with_invalid_lrp(self):
        """We create a function with an invalid LRP value"""
        with self.assertRaises(AttributeError) as exc:
            tested = MdsolDerivationDef('TANK',
                                        logical_record_position='Wibble')
        self.assertEqual("Invalid Derivation Def Logical Record Position Wibble",
                         str(exc.exception))


class TestMetaDataVersion(unittest.TestCase):
    """Contains Metadata for study design. Rave only allows one, the spec allows many in an ODM doc"""

    def test_cannot_accept_non_protocol_child(self):
        with self.assertRaises(ValueError):
            MetaDataVersion("OID", "NAME") << object()

    def test_can_accept_protocol_child(self):
        prot = Protocol()
        tested = MetaDataVersion("OID", "NAME")(prot)
        self.assertEqual(prot, tested.protocol)

    def test_can_accept_study_eventdef_child(self):
        sed = StudyEventDef("OID", "Name", False, StudyEventDef.SCHEDULED)
        tested = MetaDataVersion("OID", "NAME")(sed)
        self.assertEqual(sed, tested.study_event_defs[0])

    def test_can_accept_confirmation_message(self):
        cm = MdsolConfirmationMessage("Form saved", lang="eng")
        tested = MetaDataVersion("OID", "NAME")(cm)
        self.assertEqual(cm, tested.confirmation_message)

    def test_can_accept_edit_check_def(self):
        ec = MdsolEditCheckDef("CHECK1")
        tested = MetaDataVersion("OID", "NAME")(ec)
        self.assertEqual(ec, tested.edit_checks[0])

    def test_can_accept_derivation_def(self):
        dd = MdsolDerivationDef("DEV1")
        tested = MetaDataVersion("OID", "NAME")(dd)
        self.assertEqual(dd, tested.derivations[0])

    def test_can_accept_custom_function_def(self):
        cf = MdsolCustomFunctionDef("DEV1", "return true;", language=MdsolCustomFunctionDef.C_SHARP)
        tested = MetaDataVersion("OID", "NAME")(cf)
        self.assertEqual(cf, tested.custom_functions[0])

    def test_builder(self):
        """XML produced"""
        tested = MetaDataVersion("OID", "NAME", description="A description",
                                 primary_formoid="DM",
                                 default_matrix_oid="DEFAULT",
                                 signature_prompt='I confirm.',
                                 delete_existing=True)

        tested << Protocol()
        tested << StudyEventDef("OID", "Name", False, StudyEventDef.SCHEDULED)
        tested << FormDef("FORM_OID", "FORM_Name")
        tested << ItemGroupDef("IG_DEMO", "Demography")
        tested << ItemDef("ID_AGE", "Demography", DataType.Integer, 3)
        tested << CodeList("C_YESNO", "Yes No", DataType.String)
        tested << MdsolLabelDef("LABEL1", "first label")
        tested << MdsolConfirmationMessage("Form has been submitted!")
        tested << MdsolCustomFunctionDef("AlwaysTrue*", "return true;")
        tested << MdsolEditCheckDef("DM01")
        tested << MdsolDerivationDef("AGE")

        doc = obj_to_doc(tested)
        self.assertEqual(doc.tag, "MetaDataVersion")
        self.assertEqual("OID", doc.attrib['OID'])
        self.assertEqual("NAME", doc.attrib['Name'])
        self.assertEqual("A description", doc.attrib['Description'])
        self.assertEqual("DEFAULT", doc.attrib['mdsol:DefaultMatrixOID'])
        self.assertEqual("I confirm.", doc.attrib['mdsol:SignaturePrompt'])
        self.assertEqual("DM", doc.attrib['mdsol:PrimaryFormOID'])
        self.assertEqual("Yes", doc.attrib['mdsol:DeleteExisting'])
        self.assertEqual("Protocol", list(doc)[0].tag)
        self.assertEqual("StudyEventDef", list(doc)[1].tag)
        self.assertEqual("FormDef", list(doc)[2].tag)
        self.assertEqual("ItemGroupDef", list(doc)[3].tag)
        self.assertEqual("ItemDef", list(doc)[4].tag)
        self.assertEqual("CodeList", list(doc)[5].tag)
        self.assertEqual("mdsol:ConfirmationMessage", list(doc)[6].tag)
        self.assertEqual("mdsol:LabelDef", list(doc)[7].tag)
        self.assertEqual("mdsol:EditCheckDef", list(doc)[8].tag)
        self.assertEqual("mdsol:DerivationDef", list(doc)[9].tag)
        self.assertEqual("mdsol:CustomFunctionDef", list(doc)[10].tag)


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
        mv = MetaDataVersion('OID', 'Name')
        tested << mv
        self.assertEqual(mv, tested.metadata_version)

    def test_cannot_accept_two_metadata_versions(self):
        tested = Study('oid')(MetaDataVersion('OID1', 'NAME1'))
        with self.assertRaises(ValueError):
            tested << MetaDataVersion('OID2', 'NAME2')

    def test_builder(self):
        """XML produced"""
        tested = Study('oid1', 'GlobalLibrary Volume')(
            GlobalVariables('MY_TEST_PROJECT'),
            BasicDefinitions(),
            MetaDataVersion("OID", "NAME")
        )
        doc = obj_to_doc(tested)
        self.assertEqual(doc.tag, "Study")
        self.assertEqual(doc.attrib['mdsol:ProjectType'], "GlobalLibrary Volume")
        self.assertEqual(list(doc)[0].tag, "GlobalVariables")
        self.assertEqual(list(doc)[1].tag, "BasicDefinitions")
        self.assertEqual(list(doc)[2].tag, "MetaDataVersion")


class TestAlias(unittest.TestCase):

    def test_alias(self):
        """Create an Alias"""
        obj = Alias(context="SDTM", name="DM.BRTHDTC")
        doc = obj_to_doc(obj)
        self.assertEqual('Alias', doc.tag)
        self.assertEqual('SDTM', doc.get('Context'))
        self.assertEqual('DM.BRTHDTC', doc.get('Name'))

    def test_add_alias_to_item(self):
        """Add an Alias to an ItemDef"""
        obj = ItemDef(oid="DM.BRTHDAT", name="Date of Birth", datatype=DataType.Date,
                      date_time_format="dd MMM yyyy")
        obj << Alias(context="SDTM", name="DM.BRTHDTC")
        doc = obj_to_doc(obj)
        self.assertEqual('ItemDef', doc.tag)
        self.assertEqual('Alias', list(doc)[0].tag)

    def test_add_alias_to_protocol(self):
        """Add an Alias to an Protocol"""
        obj = Protocol()
        obj << Alias(context="SDTM", name="DM.BRTHDTC")
        doc = obj_to_doc(obj)
        self.assertEqual('Protocol', doc.tag)
        self.assertEqual('Alias', list(doc)[0].tag)

    def test_add_alias_to_studyevent(self):
        """Add an Alias to an StudyEventDef"""
        obj = StudyEventDef(oid="DM", name="Screening", repeating=False, event_type=StudyEventDef.SCHEDULED)
        obj << Alias(context="MAPPING", name="Screening")
        doc = obj_to_doc(obj)
        self.assertEqual('StudyEventDef', doc.tag)
        self.assertEqual('Alias', list(doc)[0].tag)

    def test_add_alias_to_form(self):
        """Add an Alias to an FormDef"""
        obj = FormDef(oid="DM", name="Demographics", repeating=False)
        obj << Alias(context="MAPPING", name="DEMOG")
        doc = obj_to_doc(obj)
        self.assertEqual('FormDef', doc.tag)
        self.assertEqual('Alias', list(doc)[0].tag)

    def test_add_alias_to_itemgroup(self):
        """Add an Alias to an ItemGroupDef"""
        obj = ItemGroupDef(oid="VS", name="Vitals", repeating=False)
        obj << Alias(context="MAPPING", name="VITALS")
        doc = obj_to_doc(obj)
        self.assertEqual('ItemGroupDef', doc.tag)
        self.assertEqual('Alias', list(doc)[0].tag)

    def test_add_alias_to_codelist(self):
        """Add an Alias to an CodeList"""
        obj = CodeList(oid="VSTEST", name="Vitals Tests", datatype=DataType.String)
        obj << Alias(context="MAPPING", name="VITALS")
        doc = obj_to_doc(obj)
        self.assertEqual('CodeList', doc.tag)
        self.assertEqual('Alias', list(doc)[0].tag)

    def test_add_alias_to_codelistitem(self):
        """Add an Alias to an CodeListItem"""
        obj = CodeListItem(coded_value="SYSBP")
        obj << Alias(context="MAPPING", name="Systolic Blood Pressure")
        doc = obj_to_doc(obj)
        self.assertEqual('CodeListItem', doc.tag)
        self.assertEqual('Alias', list(doc)[0].tag)

