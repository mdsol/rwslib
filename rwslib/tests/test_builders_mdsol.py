# -*- coding: utf-8 -*-
import unittest

from rwslib.builder_constants import QueryStatusType, ProtocolDeviationStatus
from rwslib.builders import MdsolQuery, ODM, ClinicalData, SubjectData, StudyEventData, FormData, ItemGroupData, \
    ItemData, MdsolProtocolDeviation
from rwslib.tests.common import obj_to_doc

__author__ = 'glow'


class TestMdsolQuery(unittest.TestCase):
    """Test extension MdsolQuery"""

    def get_tested(self):
        return MdsolQuery(status=QueryStatusType.Open, value="Data missing", query_repeat_key=123,
                          recipient="Site from System", requires_response=True)

    def test_basic(self):
        tested = self.get_tested()
        self.assertEqual("Data missing", tested.value)
        self.assertEqual(123, tested.query_repeat_key)
        self.assertEqual(QueryStatusType.Open, tested.status)
        self.assertEqual("Site from System", tested.recipient)
        self.assertEqual(True, tested.requires_response)

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


class TestProtocolDeviation(unittest.TestCase):
    """Test extension MdsolProtocolDeviation"""

    def setUp(self):
        self.tested = ODM("MY TEST SYSTEM", description="My test message")(
            ClinicalData("STUDY1", "DEV")(
                SubjectData("SITE1", "SUBJECT1")(
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

    def test_define_protocol_deviation(self):
        """Create a simple protocol deviation"""
        pd = MdsolProtocolDeviation(value="Deviated from Protocol",
                                    status=ProtocolDeviationStatus.Open,
                                    repeat_key=1)
        tested = obj_to_doc(pd)
        self.assertEqual("mdsol:ProtocolDeviation", tested.tag, "Unexpected Tag")
        self.assertEqual("Open", tested.attrib['Status'], "Status Key is missing")
        self.assertEqual("Deviated from Protocol", tested.get('Value'), "Value is missing")
        self.assertEqual(1, tested.get('ProtocolDeviationRepeatKey'), "ProtocolDeviationRepeatKey is missing")

    def test_define_protocol_deviation_with_class(self):
        """Create a simple protocol deviation with class and code"""
        pd = MdsolProtocolDeviation(value="Deviated from Protocol",
                                    status=ProtocolDeviationStatus.Open,
                                    repeat_key=1, code="E01", klass="Blargle")
        tested = obj_to_doc(pd)
        self.assertEqual("mdsol:ProtocolDeviation", tested.tag, "Unexpected Tag")
        self.assertEqual("Open", tested.attrib['Status'], "Status Key is missing")
        self.assertEqual("Deviated from Protocol", tested.get('Value'), "Value is missing")
        self.assertEqual("E01", tested.get('Code'), "Code is missing")
        self.assertEqual("Blargle", tested.get('Class'), "Class is missing")
        self.assertEqual(1, tested.get('ProtocolDeviationRepeatKey'), "ProtocolDeviationRepeatKey is missing")

    def test_define_protocol_deviation_with_transaction_type(self):
        """Create a simple protocol deviation with class and code and Transaction Type"""
        pd = MdsolProtocolDeviation(value="Deviated from Protocol",
                                    status=ProtocolDeviationStatus.Open,
                                    repeat_key=1, code="E01", klass="Blargle",
                                    transaction_type="Insert")
        tested = obj_to_doc(pd)
        self.assertEqual("mdsol:ProtocolDeviation", tested.tag, "Unexpected Tag")
        self.assertEqual("Open", tested.attrib['Status'], "Status Key is missing")
        self.assertEqual("Deviated from Protocol", tested.get('Value'), "Value is missing")
        self.assertEqual("E01", tested.get('Code'), "Code is missing")
        self.assertEqual("Blargle", tested.get('Class'), "Class is missing")
        self.assertEqual(1, tested.get('ProtocolDeviationRepeatKey'), "ProtocolDeviationRepeatKey is missing")
        self.assertEqual("Insert", tested.get('TransactionType'))

    def test_insert_pd_to_itemdata(self):
        """Create a simple protocol deviation with class and code and Transaction Type"""
        test = ItemData("FIXOID", "Fix me")(MdsolProtocolDeviation(value="Deviated from Protocol",
                                                                   status=ProtocolDeviationStatus.Open,
                                                                   repeat_key=1, code="E01", klass="Blargle",
                                                                   transaction_type="Insert"))
        tested = obj_to_doc(test)
        self.assertEqual(1, len(list(tested)))
        self.assertEqual('mdsol:ProtocolDeviation', list(tested)[0].tag)
        test << MdsolProtocolDeviation(value="Deviated from Protocol",
                                       status=ProtocolDeviationStatus.Open,
                                       repeat_key=2, code="E01", klass="Blargle",
                                       transaction_type="Insert")
        tested = obj_to_doc(test)
        self.assertEqual(2, len(list(tested)))
        self.assertEqual('mdsol:ProtocolDeviation', list(tested)[1].tag)
        self.assertEqual(2, list(tested)[1].get('ProtocolDeviationRepeatKey'))

    def test_define_protocol_deviation_with_errors(self):
        """Validate the entry"""
        with self.assertRaises(ValueError) as exc:
            pd = MdsolProtocolDeviation(value="Deviated from Protocol",
                                        status="Wigwam",
                                        repeat_key=1, code="E01", klass="Blargle")
        self.assertEqual("Status Wigwam is not a valid ProtocolDeviationStatus", str(exc.exception))
        with self.assertRaises(ValueError) as exc:
            pd = MdsolProtocolDeviation(value="Deviated from Protocol",
                                        status=ProtocolDeviationStatus.Open,
                                        repeat_key="no repeats", code="E01", klass="Blargle")
        self.assertEqual("RepeatKey no repeats is not a valid value", str(exc.exception))
        # tested = obj_to_doc(pd)
        # self.assertEqual("mdsol:ProtocolDeviation", tested.tag, "Unexpected Tag")
        # self.assertEqual("Open", tested.attrib['Status'], "Status Key is missing")
        # self.assertEqual("Deviated from Protocol", tested.get('Value'), "Value is missing")
        # self.assertEqual("E01", tested.get('Code'), "Code is missing")
        # self.assertEqual("Blargle", tested.get('Class'), "Class is missing")
        # self.assertEqual(1, tested.get('ProtocolDeviationRepeatKey'), "ProtocolDeviationRepeatKey is missing")
