# -*- coding: utf-8 -*-
__author__ = 'isparks'

import unittest
from rwslib.builders import *
from xml.etree import cElementTree as ET
from test_builders import obj_to_doc, bool_to_yes_no


# Metadata object tests


class TestTranslatedText(unittest.TestCase):
    def test_builder(self):
        """XML produced"""
        tested = TranslatedText('A test', lang='en')
        doc = obj_to_doc(tested)
        self.assertEquals(doc.tag, "TranslatedText")
        self.assertEquals("en", doc.attrib['xml:lang'])
        self.assertEquals("A test", doc.text)

    def test_builder_no_lang(self):
        """XML produced when no lang is provided"""
        tested = TranslatedText('A test')
        doc = obj_to_doc(tested)
        self.assertEquals(doc.tag, "TranslatedText")
        self.assertEquals("", doc.get('xml:lang', ''))
        self.assertEquals("A test", doc.text)

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
        self.assertEquals(doc.attrib['mdsol:StandardUnit'], "Yes")

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
            StudyEventRef("OID", 2, False) << object()


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
        self.assertEquals(doc.tag, "Protocol")
        self.assertEquals(doc.getchildren()[0].tag, "StudyEventRef")


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
        self.assertEquals(doc.tag, "StudyEventDef")
        self.assertEquals("OID", doc.attrib['OID'])
        self.assertEquals("Name", doc.attrib['Name'])
        self.assertEquals("Scheduled", doc.attrib['Type'])
        self.assertEquals("Test Cat", doc.attrib['Category'])
        self.assertEquals("1", doc.attrib['mdsol:AccessDays'])
        self.assertEquals("2", doc.attrib['mdsol:StartWinDays'])
        self.assertEquals("3", doc.attrib['mdsol:TargetDays'])
        self.assertEquals("4", doc.attrib['mdsol:EndWinDays'])
        self.assertEquals("5", doc.attrib['mdsol:OverDueDays'])
        self.assertEquals("6", doc.attrib['mdsol:CloseDays'])
        self.assertEquals("FormRef", doc.getchildren()[0].tag)


class TestItemGroupRef(unittest.TestCase):
    def test_accepts_no_children(self):
        with self.assertRaises(ValueError):
            ItemGroupRef("ItemGroup1", 1) << object()

    def test_builder(self):
        tested = ItemGroupRef("ItemGroup1", 1, mandatory=True)
        doc = obj_to_doc(tested)
        self.assertEquals(doc.tag, "ItemGroupRef")
        self.assertEquals("ItemGroup1", doc.attrib['ItemGroupOID'])
        self.assertEquals("1", doc.attrib['OrderNumber'])
        self.assertEquals("Yes", doc.attrib['Mandatory'])


class TestMdsolHelpTexts(unittest.TestCase):
    def test_build(self):
        tested = MdsolHelpText("en", "This is a help text")
        doc = obj_to_doc(tested)
        self.assertEquals(doc.tag, "mdsol:HelpText")
        self.assertEquals("en", doc.attrib['xml:lang'])
        self.assertEquals("This is a help text", doc.text)

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
        self.assertEquals(doc.tag, "mdsol:ViewRestriction")
        self.assertEquals("DM", doc.text)


class TestMdsolEntryRestriction(unittest.TestCase):
    def test_accepts_no_children(self):
        with self.assertRaises(ValueError):
            MdsolEntryRestriction("CRA") << object()

    def test_build(self):
        tested = MdsolEntryRestriction("DM")
        doc = obj_to_doc(tested)
        self.assertEquals(doc.tag, "mdsol:EntryRestriction")
        self.assertEquals("DM", doc.text)


class TestMdsolLabelRef(unittest.TestCase):
    def test_accepts_no_children(self):
        with self.assertRaises(ValueError):
            MdsolLabelRef("LABEL1", 1) << object()

    def test_build(self):
        tested = MdsolLabelRef("OID1", 1)

        doc = obj_to_doc(tested)
        self.assertEquals(doc.tag, "mdsol:LabelRef")
        self.assertEquals("OID1", doc.attrib['LabelOID'])
        self.assertEquals("1", doc.attrib['OrderNumber'])


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
        self.assertEquals(doc.tag, "ItemRef")
        self.assertEquals("OID1", doc.attrib['ItemOID'])
        self.assertEquals("1", doc.attrib['OrderNumber'])
        self.assertEquals("3", doc.attrib['KeySequence'])
        self.assertEquals("IMPUTE1", doc.attrib['ImputationMethodOID'])
        self.assertEquals("AROLE", doc.attrib['Role'])
        self.assertEquals("ROLEX", doc.attrib['RoleCodeListOID'])
        self.assertEquals("mdsol:Attribute", doc.getchildren()[0].tag)
        self.assertEquals("mdsol:Attribute", doc.getchildren()[1].tag)


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
        self.assertEquals(doc.tag, "Question")
        self.assertEquals("TranslatedText", doc.getchildren()[0].tag)


class TestMeasurementUnitRef(unittest.TestCase):
    def test_cannot_accept_child(self):
        with self.assertRaises(ValueError):
            MeasurementUnitRef("KG") << object()

    def test_build(self):
        tested = MeasurementUnitRef("KG", order_number=1)
        doc = obj_to_doc(tested)
        self.assertEquals(doc.tag, "MeasurementUnitRef")
        self.assertEquals("KG", doc.attrib['MeasurementUnitOID'])
        self.assertEquals("1", doc.attrib['mdsol:OrderNumber'])


class TestCodeListRef(unittest.TestCase):
    def test_cannot_accept_child(self):
        with self.assertRaises(ValueError):
            CodeListRef("SEV") << object()

    def test_build(self):
        tested = CodeListRef("SEVERITY")
        doc = obj_to_doc(tested)
        self.assertEquals(doc.tag, "CodeListRef")
        self.assertEquals("SEVERITY", doc.attrib['CodeListOID'])


class TestMdsolReviewGroup(unittest.TestCase):
    def test_accepts_no_children(self):
        with self.assertRaises(ValueError):
            MdsolReviewGroup("DM") << object()


def test_build(self):
    doc = obj_to_doc(MdsolReviewGroup("CRA"))
    self.assertEquals(doc.tag, "mdsol:ReviewGroup")
    self.assertEquals("CRA", doc.text)


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
        self.assertEquals(doc.tag, "mdsol:LabelDef")
        self.assertEquals("L_AGE", doc.attrib['OID'])
        self.assertEquals("Age Label", doc.attrib['Name'])
        self.assertEquals("4", doc.attrib['FieldNumber'])
        self.assertEquals("TranslatedText", doc.getchildren()[0].tag)
        self.assertEquals("mdsol:ViewRestriction", doc.getchildren()[1].tag)


class TestCheckValue(unittest.TestCase):

    def test_accepts_no_children(self):
        with self.assertRaises(ValueError):
            CheckValue("Test") << object()


    def test_build(self):
        doc = obj_to_doc(CheckValue(99))
        self.assertEquals(doc.tag, "CheckValue")
        self.assertEquals("99", doc.text)


class TestRangeCheck(unittest.TestCase):

    def test_accepts_no_strange_children(self):
        with self.assertRaises(ValueError):
            RangeCheck(comparator=RangeCheck.GREATER_THAN_EQUAL_TO, soft_hard=RangeCheck.SOFT) << object()

    def test_accepts_no_strange_soft_hard(self):
        with self.assertRaises(AttributeError):
            RangeCheck(comparator=RangeCheck.GREATER_THAN_EQUAL_TO, soft_hard="Blash")

    def test_accepts_no_strange_comparator(self):
        with self.assertRaises(AttributeError):
            RangeCheck(comparator="EQ",soft_hard="Blash")

    def test_accepts_checkvalue(self):
        tested = RangeCheck(comparator=RangeCheck.LESS_THAN_EQUAL_TO,soft_hard=RangeCheck.SOFT)
        cv = CheckValue(0)
        tested << cv
        self.assertEqual(cv, tested.check_value)


    def test_accepts_measurement_unit_ref(self):
        tested = RangeCheck(comparator=RangeCheck.GREATER_THAN_EQUAL_TO,soft_hard=RangeCheck.SOFT)
        mr =  MeasurementUnitRef('kg')
        tested << mr
        self.assertEqual(mr, tested.measurement_unit_ref)

    def test_build(self):
        self.tested = RangeCheck(comparator=RangeCheck.GREATER_THAN_EQUAL_TO, soft_hard=RangeCheck.SOFT)
        self.tested << CheckValue(0)
        self.tested << MeasurementUnitRef('kg')

        doc = obj_to_doc(self.tested)
        self.assertEquals(doc.tag, "RangeCheck")
        self.assertEquals("Soft", doc.attrib['SoftHard'])
        self.assertEquals("GE", doc.attrib['Comparator'])
        self.assertEquals("CheckValue", doc.getchildren()[0].tag)
        self.assertEquals("MeasurementUnitRef", doc.getchildren()[1].tag)


class TestItemDef(unittest.TestCase):
    def setUp(self):
        self.tested = ItemDef("I_AGE", "Age", DATATYPE_INTEGER, 3,
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
                              control_type=ItemDef.CONTROLTYPE_TEXT,
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
        with self.assertRaises(KeyError):
            ItemDef("TEST", "My Test", "TOTALLY_WRONG_DATATYPE", 10)

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
        self.tested << RangeCheck(RangeCheck.LESS_THAN_EQUAL_TO, RangeCheck.SOFT)
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
        self.tested << RangeCheck(RangeCheck.LESS_THAN_EQUAL_TO, RangeCheck.SOFT)

        doc = obj_to_doc(self.tested)
        self.assertEquals(doc.tag, "ItemDef")
        self.assertEquals("I_AGE", doc.attrib['OID'])
        self.assertEquals("Age", doc.attrib['Name'])
        self.assertEquals("Yes", doc.attrib['mdsol:Active'])
        self.assertEquals("integer", doc.attrib['DataType'])
        self.assertEquals("3", doc.attrib['Length'])
        self.assertEquals("Text", doc.attrib['mdsol:ControlType'])
        self.assertEquals("3", doc.attrib['SignificantDigits'])
        self.assertEquals("SAGE", doc.attrib['SASFieldName'])
        self.assertEquals("SVARNAME", doc.attrib['SDSVarName'])
        self.assertEquals("AGE_YRS", doc.attrib['mdsol:SASLabel'])
        self.assertEquals("3.0", doc.attrib['mdsol:SASFormat'])
        self.assertEquals("A comment", doc.attrib['Comment'])
        self.assertEquals("An origin", doc.attrib['Origin'])
        self.assertEquals("No", doc.attrib['mdsol:QueryFutureDate'])
        self.assertEquals("Yes", doc.attrib['mdsol:Visible'])
        self.assertEquals("Yes", doc.attrib['mdsol:TranslationRequired'])
        self.assertEquals("Yes", doc.attrib['mdsol:SourceDocument'])
        self.assertEquals("No", doc.attrib['mdsol:OtherVisits'])
        self.assertEquals("Yes", doc.attrib['mdsol:SourceDocument'])
        self.assertEquals("Yes", doc.attrib['mdsol:QueryNonConformance'])
        self.assertEquals("No", doc.attrib['mdsol:CanSetItemGroupDate'])
        self.assertEquals("No", doc.attrib['mdsol:CanSetFormDate'])
        self.assertEquals("No", doc.attrib['mdsol:CanSetStudyEventDate'])
        self.assertEquals("No", doc.attrib['mdsol:CanSetSubjectDate'])
        self.assertEquals("Yes", doc.attrib['mdsol:VisualVerify'])
        self.assertEquals("Yes", doc.attrib['mdsol:DoesNotBreakSignature'])
        self.assertEquals("SOMETHING_DIFFERENT", doc.attrib['mdsol:VariableOID'])
        self.assertEquals("jpg", doc.attrib['mdsol:AcceptableFileExtensions'])
        self.assertEquals("99", doc.attrib['mdsol:DefaultValue'])
        self.assertEquals("mmm yy dd", doc.attrib['mdsol:DateTimeFormat'])
        self.assertEquals("10", doc.attrib['mdsol:FieldNumber'])

        self.assertEquals("Question", doc.getchildren()[0].tag)
        self.assertEquals("CodeListRef", doc.getchildren()[1].tag)
        self.assertEquals("MeasurementUnitRef", doc.getchildren()[2].tag)
        self.assertEquals("RangeCheck", doc.getchildren()[3].tag)
        self.assertEquals("mdsol:HeaderText", doc.getchildren()[4].tag)
        self.assertEquals("mdsol:ViewRestriction", doc.getchildren()[5].tag)
        self.assertEquals("mdsol:EntryRestriction", doc.getchildren()[6].tag)
        self.assertEquals("mdsol:HelpText", doc.getchildren()[7].tag)
        self.assertEquals("mdsol:ReviewGroup", doc.getchildren()[8].tag)


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
        self.assertEquals(doc.tag, "ItemGroupDef")
        self.assertEquals("DM", doc.attrib['OID'])
        self.assertEquals("Yes", doc.attrib['Repeating'])
        self.assertEquals("Yes", doc.attrib['IsReferenceData'])
        self.assertEquals("Demography", doc.attrib['Name'])
        self.assertEquals("DMSAS", doc.attrib['SASDatasetName'])
        self.assertEquals("TESTDOMAIN", doc.attrib['Domain'])
        self.assertEquals("TESTORIGIN", doc.attrib['Origin'])
        self.assertEquals("TESTROLE", doc.attrib['Role'])
        self.assertEquals("TESTPURPOSE", doc.attrib['Purpose'])
        self.assertEquals("A comment", doc.attrib['Comment'])
        self.assertEquals("ItemRef", doc.getchildren()[0].tag)
        self.assertEquals("mdsol:LabelRef", doc.getchildren()[1].tag)


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
        self.assertEquals(doc.tag, "FormDef")
        self.assertEquals("DM", doc.attrib['OID'])
        self.assertEquals("Demog", doc.attrib['Name'])
        self.assertEquals("Yes", doc.attrib['Repeating'])
        self.assertEquals("2", doc.attrib['mdsol:OrderNumber'])
        # Would not see LinkFormOID and LinkStudyEventOID together, they are mutually exclusive. Just for coverage.
        self.assertEquals("FRM1", doc.attrib['mdsol:LinkFormOID'])
        self.assertEquals("EVT1", doc.attrib['mdsol:LinkStudyEventOID'])
        self.assertEquals("ItemGroupRef", doc.getchildren()[0].tag)
        self.assertEquals("mdsol:HelpText", doc.getchildren()[1].tag)
        self.assertEquals("mdsol:ViewRestriction", doc.getchildren()[2].tag)
        self.assertEquals("mdsol:EntryRestriction", doc.getchildren()[3].tag)


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
        self.assertEquals("Decode", doc.tag)
        self.assertEquals("TranslatedText", doc.getchildren()[0].tag)


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
        self.assertEquals("CodeListItem", doc.tag)
        self.assertEquals("", doc.get('mdsol:Specify', ''))
        self.assertEquals("", doc.get('mdsol:OrderNumber', ''))
        self.assertEquals("Y", doc.attrib['CodedValue'])
        self.assertEquals("Decode", doc.getchildren()[0].tag)

    def test_builder_order_specify(self):
        """XML produced with optional params set"""
        tested = CodeListItem("Y", order_number=1, specify=True)
        tested << Decode()
        doc = obj_to_doc(tested)
        self.assertEquals("CodeListItem", doc.tag)
        self.assertEquals("Yes", doc.attrib['mdsol:Specify'])
        self.assertEquals("1", doc.attrib['mdsol:OrderNumber'])
        self.assertEquals("Y", doc.attrib['CodedValue'])
        self.assertEquals("Decode", doc.getchildren()[0].tag)


class TestCodeList(unittest.TestCase):
    """Codelists contain codelistitems"""

    def test_cannot_accept_non_codelistitem(self):
        with self.assertRaises(ValueError):
            CodeList("CL1", "Codelist1", DATATYPE_INTEGER) << object()

    def test_invalid_datatype(self):
        with self.assertRaises(ValueError):
            CodeList("CL1","Codelist1", "IncorrectDataType")

    def test_accepts_codelistitem(self):
        tested = CodeList("CL1", "Codelist1", DATATYPE_INTEGER)
        cl1 = CodeListItem("1")
        tested.add(cl1)
        self.assertEqual(cl1, tested.codelist_items[0])

    def test_builder(self):
        """XML produced"""
        tested = CodeList("CL_YN", "YesNo", DATATYPE_STRING, sas_format_name="YESNO_CL")
        tested << CodeListItem("Y")
        doc = obj_to_doc(tested)
        self.assertEquals("CodeList", doc.tag)
        self.assertEquals(DATATYPE_STRING, doc.attrib['DataType'])
        self.assertEquals("YESNO_CL", doc.attrib['SASFormatName'])
        self.assertEquals("CodeListItem", doc.getchildren()[0].tag)


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
        tested << ItemDef("ID_AGE", "Demography", DATATYPE_INTEGER, 3)
        tested << CodeList("C_YESNO", "Yes No", DATATYPE_STRING)
        tested << MdsolLabelDef("LABEL1", "first label")

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
        self.assertEquals("StudyEventDef", doc.getchildren()[1].tag)
        self.assertEquals("FormDef", doc.getchildren()[2].tag)
        self.assertEquals("ItemGroupDef", doc.getchildren()[3].tag)
        self.assertEquals("ItemDef", doc.getchildren()[4].tag)
        self.assertEquals("CodeList", doc.getchildren()[5].tag)
        self.assertEquals("mdsol:LabelDef", doc.getchildren()[6].tag)


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
        self.assertEquals(doc.tag, "Study")
        self.assertEquals(doc.attrib['mdsol:ProjectType'], "GlobalLibrary Volume")
        self.assertEquals(doc.getchildren()[0].tag, "GlobalVariables")
        self.assertEquals(doc.getchildren()[1].tag, "BasicDefinitions")
        self.assertEquals(doc.getchildren()[2].tag, "MetaDataVersion")


if __name__ == '__main__':
    unittest.main()
