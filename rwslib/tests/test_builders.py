__author__ = 'isparks'

import unittest
from rwslib.builders import *
from xml.etree import cElementTree as ET


def obj_to_doc(obj, *args, **kwargs):
    """Convert an object to am XML document object"""
    builder = ET.TreeBuilder()
    obj.build(builder, *args, **kwargs)
    return builder.close()


class TestBoolToTrueFalse(unittest.TestCase):
    def test_true_to_TRUE(self):
        """TRUE returned from true"""
        self.assertEqual('TRUE', bool_to_true_false(True))

    def test_false_to_FALSE(self):
        """FALSE returned from false"""
        self.assertEqual('FALSE', bool_to_true_false(False))


class TestInheritance(unittest.TestCase):
    """The things we do for 100% coverage."""

    def test_inheritance_warning(self):
        class NewObj(ODMElement):
            """We do not override the __lshift__ method"""
            pass

        with self.assertRaises(ValueError):
            # Exercise __lshift__
            NewObj() << object()


class TestString(unittest.TestCase):
    def test_to_string(self):
        self.assertEqual('<UserRef UserOID="test" />', str(UserRef("test")))


class TestAttributeSetters(unittest.TestCase):
    class TestElem(ODMElement):
        """Test class with a bad __lshift__ implementation"""

        def __init__(self):
            self.user = None
            self.locations = []

        def __lshift__(self, other):
            self.set_single_attribute(other, UserRef, "xxxuser")  # Incorrect spelling of user attribute
            self.set_list_attribute(other, LocationRef, "xxxlocations")  # Incorrect spelling of location attribute

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

        self.assertEqual(doc.attrib['UserOID'], "Fred")
        self.assertEqual(doc.tag, "UserRef")


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
                                  used_imputation_method=False,
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
        self.assertEqual('_Hello', ar.audit_id)

        # Letter OK
        ar = AuditRecord(identifier='Hello')
        self.assertEqual('Hello', ar.audit_id)

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


class TestSignatureRef(unittest.TestCase):
    def test_creates_expected_element(self):
        """We get the Signature Ref element"""
        t = SignatureRef("ASIGNATURE")
        doc = obj_to_doc(t)
        self.assertEqual("SignatureRef", doc.tag)
        self.assertEqual("ASIGNATURE", doc.attrib['SignatureOID'])


class TestSignature(unittest.TestCase):
    def test_creates_expected_element(self):
        """We create a Signature element"""
        t = Signature(signature_id="Some ID",
                      user_ref=UserRef(oid="AUser"),
                      location_ref=LocationRef(oid="ALocation"),
                      signature_ref=SignatureRef(oid="ASignature"),
                      date_time_stamp=DateTimeStamp(date_time=datetime(year=2016,
                                                                       month=12,
                                                                       day=25,
                                                                       hour=12,
                                                                       minute=0,
                                                                       second=0)))
        doc = obj_to_doc(t)
        self.assertEqual('Signature', doc.tag)
        self.assertEqual('Some ID', doc.attrib['ID'])
        # all four elements are present
        self.assertTrue(len(doc.getchildren()) == 4)

    def test_creates_expected_element_no_id(self):
        """We create a Signature element without an ID"""
        t = Signature(user_ref=UserRef(oid="AUser"),
                      location_ref=LocationRef(oid="ALocation"),
                      signature_ref=SignatureRef(oid="ASignature"),
                      date_time_stamp=DateTimeStamp(date_time=datetime(year=2016,
                                                                       month=12,
                                                                       day=25,
                                                                       hour=12,
                                                                       minute=0,
                                                                       second=0)))
        doc = obj_to_doc(t)
        self.assertEqual('Signature', doc.tag)
        self.assertTrue('ID' not in doc.attrib)
        # all four elements are present
        self.assertTrue(len(doc.getchildren()) == 4)

    def test_all_elements_are_required(self):
        """All the sub-elements are required"""
        all = dict(user_ref=UserRef(oid="AUser"),
                   location_ref=LocationRef(oid="ALocation"),
                   signature_ref=SignatureRef(oid="ASignature"),
                   date_time_stamp=DateTimeStamp(date_time=datetime(year=2016,
                                                                    month=12,
                                                                    day=25,
                                                                    hour=12,
                                                                    minute=0,
                                                                    second=0)))
        t0 = Signature()
        with self.assertRaises(ValueError) as exc:
            doc = obj_to_doc(t0)
        self.assertEqual("User Reference not set.", str(exc.exception))
        t1 = Signature(user_ref=all.get('user_ref'))
        with self.assertRaises(ValueError) as exc:
            doc = obj_to_doc(t1)
        self.assertEqual("Location Reference not set.", str(exc.exception))
        t2 = Signature(user_ref=all.get('user_ref'), location_ref=all.get('location_ref'))
        with self.assertRaises(ValueError) as exc:
            doc = obj_to_doc(t2)
        self.assertEqual("Signature Reference not set.", str(exc.exception))
        t3 = Signature(user_ref=all.get('user_ref'),
                       location_ref=all.get('location_ref'),
                       signature_ref=all.get('signature_ref'))
        with self.assertRaises(ValueError) as exc:
            doc = obj_to_doc(t3)
        self.assertEqual("DateTime not set.", str(exc.exception))

    def test_signature_builder(self):
        """"""
        tested = Signature(signature_id="Some ID")
        all = dict(user_ref=UserRef(oid="AUser"),
                   location_ref=LocationRef(oid="ALocation"),
                   signature_ref=SignatureRef(oid="ASignature"),
                   date_time_stamp=DateTimeStamp(date_time=datetime(year=2016,
                                                                    month=12,
                                                                    day=25,
                                                                    hour=12,
                                                                    minute=0,
                                                                    second=0)))
        for child in all.values():
            tested << child
        doc = obj_to_doc(tested)
        self.assertEqual('Signature', doc.tag)
        self.assertEqual('Some ID', doc.attrib['ID'])
        # all four elements are present
        self.assertTrue(len(doc.getchildren()) == 4)

    def test_signature_builder_with_invalid_input(self):
        """"""
        tested = Signature(signature_id="Some ID")
        with self.assertRaises(ValueError) as exc:
            tested << ItemData(itemoid="GENDER", value="MALE")
        self.assertEqual("Signature cannot accept a child element of type ItemData",
                         str(exc.exception))


class TestAnnotation(unittest.TestCase):
    """ Test Annotation classes """

    def test_happy_path(self):
        """ Simple Annotation with a single flag and comment"""
        tested = Annotation(annotation_id="APPLE",
                            seqnum=1)
        f = Flag(flag_value=FlagValue("Some value", codelist_oid="ANOID"),
                 flag_type=FlagType("Some type", codelist_oid="ANOTHEROID"))
        c = Comment("Some Comment")
        tested << f
        tested << c
        t = obj_to_doc(tested)
        self.assertEqual('Annotation', t.tag)
        self.assertEqual(1, t.attrib['SeqNum'])
        self.assertEqual("APPLE", t.attrib['ID'])
        self.assertTrue(len(t.getchildren()) == 2)

    def test_happy_path_id_optional(self):
        """ Simple Annotation with a single flag and comment, no ID"""
        tested = Annotation(seqnum=1)
        f = Flag(flag_value=FlagValue("Some value", codelist_oid="ANOID"),
                 flag_type=FlagType("Some type", codelist_oid="ANOTHEROID"))
        c = Comment("Some Comment")
        tested << f
        tested << c
        t = obj_to_doc(tested)
        self.assertEqual('Annotation', t.tag)
        self.assertEqual(1, t.attrib['SeqNum'])
        self.assertNotIn("ID", t.attrib)
        self.assertTrue(len(t.getchildren()) == 2)

    def test_happy_path_seqnum_defaulted(self):
        """ Simple Annotation with a single flag and comment, SeqNum missing"""
        tested = Annotation()
        f = Flag(flag_value=FlagValue("Some value", codelist_oid="ANOID"),
                 flag_type=FlagType("Some type", codelist_oid="ANOTHEROID"))
        c = Comment("Some Comment")
        tested << f
        tested << c
        t = obj_to_doc(tested)
        self.assertEqual('Annotation', t.tag)
        self.assertEqual(1, t.attrib['SeqNum'])
        self.assertTrue(len(t.getchildren()) == 2)

    def test_happy_path_multiple_flags(self):
        """ Simple Annotation with a multiple flags and comment"""
        tested = Annotation()
        c = Comment("Some Comment")
        # Add some flags
        for i in range(0, 3):
            tested << Flag(flag_value=FlagValue("Some value %s" % i, codelist_oid="ANOID%s" % i),
                           flag_type=FlagType("Some type %s" % i, codelist_oid="ANOTHEROID%s" % i))
        tested << c
        t = obj_to_doc(tested)
        self.assertEqual('Annotation', t.tag)
        self.assertTrue(len(t.getchildren()) == 4)

    def test_happy_path_multiple_flags_on_init(self):
        """ Simple Annotation with a multiple flags and comment created at init"""
        flags = [Flag(flag_value=FlagValue("Some value %s" % i, codelist_oid="ANOID%s" % i),
                      flag_type=FlagType("Some type %s" % i, codelist_oid="ANOTHEROID%s" % i)) for i in range(0, 3)]
        tested = Annotation(comment=Comment("Some Comment"), flags=flags)
        t = obj_to_doc(tested)
        self.assertEqual('Annotation', t.tag)
        self.assertTrue(len(t.getchildren()) == 4)

    def test_happy_path_flag_on_init(self):
        """ Simple Annotation with a single flag and comment created at init"""
        flags = [Flag(flag_value=FlagValue("Some value %s" % i, codelist_oid="ANOID%s" % i),
                      flag_type=FlagType("Some type %s" % i, codelist_oid="ANOTHEROID%s" % i)) for i in range(0, 3)]
        tested = Annotation(comment=Comment("Some Comment"), flags=flags[0])
        t = obj_to_doc(tested)
        self.assertEqual('Annotation', t.tag)
        self.assertTrue(len(t.getchildren()) == 2)

    def test_not_flag_on_init(self):
        """ Simple Annotation with not a flag raises an exception and comment created at init"""
        notflags = ItemData(itemoid="GENDER", value="MALE")
        with self.assertRaises(AttributeError) as exc:
            tested = Annotation(comment=Comment("Some Comment"), flags=notflags)
        self.assertEqual("Flags attribute should be an iterable or Flag",
                         str(exc.exception))

    def test_only_accept_valid_children(self):
        """ Annotation can only take one or more Flags and one Comment"""
        tested = Annotation(annotation_id='An Annotation')
        with self.assertRaises(ValueError) as exc:
            tested << ItemData(itemoid="GENDER", value="MALE")
        self.assertEqual("Annotation cannot accept a child element of type ItemData",
                         str(exc.exception))
        tested << Comment("A comment")
        with self.assertRaises(ValueError) as exc:
            tested << Comment("Another Comment")
        self.assertEqual("Annotation already has a Comment element set.",
                         str(exc.exception))

    def test_only_valid_id_accepted(self):
        """ Annotation ID must be a non empty string"""
        for nonsense in ('', '     '):
            with self.assertRaises(AttributeError) as exc:
                tested = Annotation(annotation_id=nonsense)
            self.assertEqual("Invalid ID value supplied",
                             str(exc.exception),
                             "Value should raise with '%s'" % nonsense)

    def test_only_valid_seqnum_accepted(self):
        """ Annotation ID must be a non empty string"""
        for nonsense in ('apple', '     ', -1):
            with self.assertRaises(AttributeError) as exc:
                tested = Annotation(seqnum=nonsense)
            self.assertEqual("Invalid SeqNum value supplied",
                             str(exc.exception),
                             "Value should raise with '%s'" % nonsense)

    def test_need_flags(self):
        """ Annotation needs a Flag """
        tested = Annotation(comment=Comment("A comment"))
        with self.assertRaises(ValueError) as exc:
            t = obj_to_doc(tested)
        self.assertEqual("Flag is not set.", str(exc.exception))

    def test_transaction_type(self):
        """ Annotation can take a transaction type """
        tested = Annotation(flags=Flag(flag_value=FlagValue("Some value", codelist_oid="ANOID"),
                                       flag_type=FlagType("Some type", codelist_oid="ANOTHEROID")),
                            comment=Comment("A comment"), transaction_type='Update')
        t = obj_to_doc(tested)
        self.assertEqual("Annotation", t.tag)
        self.assertEqual("Update", t.attrib['TransactionType'])


class TestFlag(unittest.TestCase):
    """ Test Flag classes """

    def test_happy_path(self):
        """Create a Flag object"""
        tested = Flag()
        tested << FlagValue("Some value", codelist_oid="ANOID")
        tested << FlagType("Some type", codelist_oid="ANOTHEROID")
        t = obj_to_doc(tested)
        self.assertEqual('Flag', t.tag)
        self.assertTrue(len(t.getchildren()) == 2)

    def test_no_value(self):
        """No FlagValue is an exception"""
        tested = Flag()
        tested << FlagType("Some type", codelist_oid="ANOTHEROID")
        with self.assertRaises(ValueError) as exc:
            t = obj_to_doc(tested)
        self.assertEqual("FlagValue is not set.", str(exc.exception))

    def test_only_expected_types(self):
        """We can only add Flag-type elements"""
        tested = Flag()
        with self.assertRaises(ValueError) as exc:
            tested << ItemData(itemoid="GENDER", value="MALE")
        self.assertEqual("Flag cannot accept a child element of type ItemData",
                         str(exc.exception))

    def test_only_expected_types_instance_vars(self):
        """We can only add Flag-type elements"""
        with self.assertRaises(ValueError) as exc:
            tested = Flag(flag_type=ItemData(itemoid="GENDER", value="MALE"))
        self.assertEqual("Flag cannot accept a child element of type ItemData",
                         str(exc.exception))
        with self.assertRaises(ValueError) as exc:
            tested = Flag(flag_value=ItemData(itemoid="GENDER", value="MALE"))
        self.assertEqual("Flag cannot accept a child element of type ItemData",
                         str(exc.exception))


class TestFlagType(unittest.TestCase):
    """ Test FlagType classes """

    def test_happy_path(self):
        """Create a FlagType object"""
        tested = FlagType("A Type")
        tested.codelist_oid = "ANOID"
        t = obj_to_doc(tested)
        self.assertEqual('FlagType', t.tag)
        self.assertEqual('ANOID', t.attrib['CodeListOID'])
        self.assertEqual('A Type', t.text)

    def test_no_oid_exception(self):
        """Create a FlagType object without a CodeListOID is an exception"""
        tested = FlagType("A Type")
        with self.assertRaises(ValueError) as exc:
            t = obj_to_doc(tested)
        self.assertEqual("CodeListOID not set.", str(exc.exception))

    def test_invalid_oid_exception(self):
        """Assigning a nonsensical value is an error"""
        tested = FlagType("A Type")
        for nonsense in (None, '', '   '):
            with self.assertRaises(AttributeError) as exc:
                tested.codelist_oid = nonsense
            self.assertEqual("Empty CodeListOID value is invalid.", str(exc.exception))

    def test_invalid_oid_exception_at_creation(self):
        """Assigning a nonsensical value is an error"""
        with self.assertRaises(AttributeError) as exc:
            tested = FlagType("A Type", codelist_oid='')
        self.assertEqual("Empty CodeListOID value is invalid.", str(exc.exception))


class TestFlagValue(unittest.TestCase):
    """ Test FlagValue classes """

    def test_happy_path(self):
        """Create a FlagValue object"""
        tested = FlagValue("A Value")
        tested.codelist_oid = "ANOID"
        t = obj_to_doc(tested)
        self.assertEqual('FlagValue', t.tag)
        self.assertEqual('ANOID', t.attrib['CodeListOID'])
        self.assertEqual('A Value', t.text)

    def test_no_oid_exception(self):
        """Create a FlagType object without a CodeListOID is an exception"""
        tested = FlagValue("A Type")
        with self.assertRaises(ValueError) as exc:
            t = obj_to_doc(tested)
        self.assertEqual("CodeListOID not set.", str(exc.exception))

    def test_invalid_oid_exception(self):
        """Assigning a nonsensical value is an error"""
        tested = FlagValue("A Type")
        for nonsense in (None, '', '   '):
            with self.assertRaises(AttributeError) as exc:
                tested.codelist_oid = nonsense
            self.assertEqual("Empty CodeListOID value is invalid.", str(exc.exception))

    def test_invalid_oid_exception_at_creation(self):
        """Assigning a nonsensical value is an error"""
        with self.assertRaises(AttributeError) as exc:
            tested = FlagValue("A Value", codelist_oid='')
        self.assertEqual("Empty CodeListOID value is invalid.", str(exc.exception))


class TestComment(unittest.TestCase):
    """ Test Comment classes """

    def test_happy_path(self):
        """Creating a valid Comment, no problems"""
        tested = Comment()
        tested.text = 'Some comment'
        tested.sponsor_or_site = 'Site'
        t = obj_to_doc(tested)
        self.assertEqual('Comment', t.tag)
        self.assertEqual('Site', t.attrib['SponsorOrSite'])
        self.assertEqual('Some comment', t.text)

    def test_happy_path_no_commenter(self):
        """Creating a valid Comment without a commenter, no problems"""
        tested = Comment()
        tested.text = 'Some comment'
        t = obj_to_doc(tested)
        self.assertEqual('Comment', t.tag)
        self.assertNotIn('SponsorOrSite', t.attrib)
        self.assertEqual('Some comment', t.text)

    def test_invalid_commenter(self):
        """Creating a valid Comment with an invalid commenter, get an exception"""
        tested = Comment()
        tested.text = 'Some comment'
        with self.assertRaises(AttributeError) as exc:
            tested.sponsor_or_site = 'Some guy off the street'
        self.assertEqual("Comment sponsor_or_site value of Some guy off the street is not valid",
                         str(exc.exception))

    def test_invalid_no_comment(self):
        """Creating a invalid Comment, get an exception"""
        tested = Comment()
        with self.assertRaises(ValueError) as exc:
            t = obj_to_doc(tested)
        self.assertEqual("Text is not set.",
                         str(exc.exception))

    def test_invalid_text_comment(self):
        """Creating a Comment with invalid text, get an exception"""
        tested = Comment()
        for nonsense in (None, '', '    '):
            with self.assertRaises(AttributeError) as exc:
                tested.text = nonsense
            self.assertEqual("Empty text value is invalid.",
                             str(exc.exception))


class TestItemData(unittest.TestCase):
    """Test ItemData classes"""

    def setUp(self):
        self.tested = ItemData('FIELDA', "TEST")

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
            self.tested << {"Field1": "ValueC"}

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

        self.assertRaises(KeyError, do)

    def test_specify(self):
        """Test specify"""
        specify_value = 'A Specify'
        self.tested.specify_value = specify_value
        doc = obj_to_doc(self.tested)
        self.assertEqual(doc.attrib['mdsol:SpecifyValue'], specify_value)

    def test_freeze_lock_verify(self):
        tested = ItemData('FIELDA', "TEST", lock=True, verify=True, freeze=False)
        self.assertEqual(tested.lock, True)
        self.assertEqual(tested.freeze, False)
        self.assertEqual(tested.verify, True)

    def test_builder(self):
        """Test building XML"""
        tested = ItemData('FIELDA', "TEST", lock=True, verify=True, freeze=False)

        tested << AuditRecord(edit_point=AuditRecord.EDIT_DATA_MANAGEMENT,
                              used_imputation_method=False,
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

        self.assertEqual(doc.attrib['ItemOID'], "FIELDA")
        self.assertEqual(doc.attrib['Value'], "TEST")
        self.assertEqual(doc.attrib['mdsol:Verify'], "Yes")
        self.assertEqual(doc.attrib['mdsol:Lock'], "Yes")
        self.assertEqual(doc.attrib['mdsol:Freeze'], "No")
        self.assertEqual(doc.tag, "ItemData")
        self.assertEqual("AuditRecord", doc.getchildren()[0].tag)
        self.assertEqual("MeasurementUnitRef", doc.getchildren()[1].tag)
        self.assertEqual("mdsol:Query", doc.getchildren()[2].tag)

    def test_transaction_type(self):
        tested = self.tested
        tested.transaction_type = 'Update'
        doc = obj_to_doc(tested)
        self.assertEqual(doc.attrib['TransactionType'], "Update")

    def test_null_value(self):
        """Null or empty string values are treated specially with IsNull property and no value"""
        tested = self.tested
        tested.value = ''
        doc = obj_to_doc(tested)
        self.assertEqual(doc.attrib['IsNull'], "Yes")

        # Check Value attribute is also missing
        def do():
            doc.attrib["Value"]

        self.assertRaises(KeyError, do)

    def test_invalid_transaction_type(self):
        def do():
            ItemData("A", "val", transaction_type='invalid')

        self.assertRaises(AttributeError, do)

    def test_add_annotations(self):
        """Test we can add one or more annotations"""
        flags = [Flag(flag_value=FlagValue("Some value %s" % i, codelist_oid="ANOID%s" % i),
                      flag_type=FlagType("Some type %s" % i, codelist_oid="ANOTHEROID%s" % i)) for i in range(0, 3)]
        for i in range(0, 4):
            self.tested << Annotation(comment=Comment("Some Comment %s" % i), flags=flags)
        t = obj_to_doc(self.tested)
        self.assertEqual(self.__class__.__name__[4:], t.tag)
        self.assertTrue(len(t.getchildren()) == 4)  # one formdata + 4 annotations


class TestItemGroupData(unittest.TestCase):
    """Test ItemGroupData classes"""

    def setUp(self):
        self.tested = ItemGroupData()(
            ItemData("Field1", "ValueA"),
            ItemData("Field2", "ValueB")
        )

    def test_children(self):
        """Test there are 2 children"""
        self.assertEqual(2, len(self.tested.items))

    def test_two_same_invalid(self):
        """Test adding a duplicate field causes error"""

        def do():
            self.tested << ItemData("Field1", "ValueC")

        self.assertRaises(ValueError, do)

    def test_only_accepts_itemdata(self):
        """Test that an ItemGroupData will only accept an ItemData element"""

        def do():
            self.tested << {"Field1": "ValueC"}

        self.assertRaises(ValueError, do)

    def test_invalid_transaction_type(self):
        def do():
            ItemGroupData(transaction_type='invalid')

        self.assertRaises(AttributeError, do)

    def test_builders_basic(self):
        doc = obj_to_doc(self.tested, "TESTFORM")
        self.assertEqual(doc.attrib["ItemGroupOID"], "TESTFORM")
        self.assertEqual(len(doc), 2)
        self.assertEqual(doc.tag, "ItemGroupData")

    def test_transaction_type(self):
        """Test transaction type inserted if set"""
        self.tested.transaction_type = 'Context'
        doc = obj_to_doc(self.tested, "TESTFORM")
        self.assertEqual(doc.attrib["TransactionType"], "Context")

    def test_whole_item_group(self):
        """mdsol:Submission should be wholeitemgroup or SpecifiedItemsOnly"""
        doc = obj_to_doc(self.tested, "TESTFORM")
        self.assertEqual(doc.attrib["mdsol:Submission"], "SpecifiedItemsOnly")

        self.tested.whole_item_group = True
        doc = obj_to_doc(self.tested, "TESTFORM")
        self.assertEqual(doc.attrib["mdsol:Submission"], "WholeItemGroup")

    def test_add_annotations(self):
        """Test we can add one or more annotations"""
        flags = [Flag(flag_value=FlagValue("Some value %s" % i, codelist_oid="ANOID%s" % i),
                      flag_type=FlagType("Some type %s" % i, codelist_oid="ANOTHEROID%s" % i)) for i in range(0, 3)]
        for i in range(0, 4):
            self.tested << Annotation(comment=Comment("Some Comment %s" % i), flags=flags)
        t = obj_to_doc(self.tested, "TESTFORM")
        self.assertEqual(self.__class__.__name__[4:], t.tag)
        self.assertTrue(len(t.getchildren()) == 6)  # two itemdata + 4 annotations

    def test_add_annotations_on_create_multiple(self):
        """Test we can add one or more annotations at initialisation"""
        flags = [Flag(flag_value=FlagValue("Some value %s" % i, codelist_oid="ANOID%s" % i),
                      flag_type=FlagType("Some type %s" % i, codelist_oid="ANOTHEROID%s" % i)) for i in range(0, 3)]
        annotations = [Annotation(comment=Comment("Some Comment %s" % i), flags=flags) for i in range(0, 4)]
        # add a list of annotations
        igd = ItemGroupData(annotations=annotations)(
            ItemData("Field1", "ValueA"),
            ItemData("Field2", "ValueB")
        )
        t = obj_to_doc(igd, "TESTFORM")
        self.assertEqual(self.__class__.__name__[4:], t.tag)
        self.assertTrue(len(t.getchildren()) == 6)  # two itemdata + 4 annotations

    def test_add_annotations_on_create_single(self):
        """Test we can add one or more annotations at initialisation with one"""
        flags = [Flag(flag_value=FlagValue("Some value %s" % i, codelist_oid="ANOID%s" % i),
                      flag_type=FlagType("Some type %s" % i, codelist_oid="ANOTHEROID%s" % i)) for i in range(0, 3)]
        annotations = [Annotation(comment=Comment("Some Comment %s" % i), flags=flags) for i in range(0, 4)]
        # add a list of annotations
        igd = ItemGroupData(annotations=annotations[0])(
            ItemData("Field1", "ValueA"),
            ItemData("Field2", "ValueB")
        )
        t = obj_to_doc(igd, "TESTFORM")
        self.assertEqual(self.__class__.__name__[4:], t.tag)
        self.assertTrue(len(t.getchildren()) == 3)  # two itemdata + 4 annotations

    def test_add_signature(self):
        """Test we can add one signature"""
        self.tested << Signature(signature_id="Some ID",
                                 user_ref=UserRef(oid="AUser"),
                                 location_ref=LocationRef(oid="ALocation"),
                                 signature_ref=SignatureRef(oid="ASignature"),
                                 date_time_stamp=DateTimeStamp(date_time=datetime(year=2016,
                                                                                  month=12,
                                                                                  day=25,
                                                                                  hour=12,
                                                                                  minute=0,
                                                                                  second=0)))
        t = obj_to_doc(self.tested, "TESTFORM")
        self.assertEqual(self.__class__.__name__[4:], t.tag)
        self.assertTrue(len(t.getchildren()) == 3)  # two itemdata + 1 signature


class TestFormData(unittest.TestCase):
    """Test FormData classes"""

    def setUp(self):
        self.tested = FormData("TESTFORM_A")(
            ItemGroupData()(
                ItemData("Field1", "ValueA"),
                ItemData("Field2", "ValueB")
            ),
            ItemGroupData()(
                ItemData("Field3", "ValueC"),
            ),
            ItemGroupData()(
                ItemData("Field4", "ValueD"),
            ),
        )

    def test_children(self):
        """Test there are 3 children"""
        self.assertEqual(3, len(self.tested.itemgroups))

    def test_invalid_transaction_type(self):
        """Can only be insert, update, upsert not context"""

        def do():
            FormData("MYFORM", transaction_type='context')

        self.assertRaises(AttributeError, do)

    def test_only_accepts_itemgroupdata(self):
        """Test that only ItemGroupData can be inserted"""

        def do():
            # Bzzzt. Should be ItemGroupData
            self.tested << ItemData("Field1", "ValueC")

        self.assertRaises(ValueError, do)

    def test_only_add_itemgroup_once(self):
        """Test that an ItemGroupData can only be added once"""
        igd = ItemGroupData()
        self.tested << igd

        def do():
            self.tested << igd

        self.assertRaises(ValueError, do)

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

        self.assertRaises(AttributeError, do)

    def test_form_repeat_key(self):
        """Test transaction type inserted if set"""
        tested = FormData("TESTFORM_A", form_repeat_key=9)(
            ItemGroupData()(
                ItemData("Field1", "ValueA"),
                ItemData("Field2", "ValueB")
            )
        )
        doc = obj_to_doc(tested)
        self.assertEqual(doc.attrib["FormRepeatKey"], "9")

    def test_add_annotations(self):
        """Test we can add one or more annotations"""
        flags = [Flag(flag_value=FlagValue("Some value %s" % i, codelist_oid="ANOID%s" % i),
                      flag_type=FlagType("Some type %s" % i, codelist_oid="ANOTHEROID%s" % i)) for i in range(0, 3)]
        for i in range(0, 4):
            self.tested << Annotation(comment=Comment("Some Comment %s" % i), flags=flags)
        t = obj_to_doc(self.tested)
        self.assertEqual(self.__class__.__name__[4:], t.tag)
        self.assertTrue(len(t.getchildren()) == 7)  # three igdata + 4 annotations

    def test_add_signature(self):
        """Test we can add one signature"""
        self.tested << Signature(signature_id="Some ID",
                                 user_ref=UserRef(oid="AUser"),
                                 location_ref=LocationRef(oid="ALocation"),
                                 signature_ref=SignatureRef(oid="ASignature"),
                                 date_time_stamp=DateTimeStamp(date_time=datetime(year=2016,
                                                                                  month=12,
                                                                                  day=25,
                                                                                  hour=12,
                                                                                  minute=0,
                                                                                  second=0)))
        t = obj_to_doc(self.tested)
        self.assertEqual(self.__class__.__name__[4:], t.tag)
        self.assertTrue(len(t.getchildren()) == 4)  # three igdata + 1 signature


class TestStudyEventData(unittest.TestCase):
    """Test StudyEventData classes"""

    def setUp(self):
        self.tested = StudyEventData('VISIT_1')(
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

    def test_transaction_type(self):
        """Test transaction type inserted if set"""
        self.tested.transaction_type = 'Update'
        doc = obj_to_doc(self.tested)
        self.assertEqual(doc.attrib["TransactionType"], self.tested.transaction_type)

    def test_builders_basic(self):
        doc = obj_to_doc(self.tested)
        self.assertEqual(doc.attrib["StudyEventOID"], "VISIT_1")
        self.assertIsNone(doc.attrib.get("StudyEventRepeatKey"))
        self.assertEqual(len(doc), 1)
        self.assertEqual(doc.tag, "StudyEventData")

    def test_study_event_repeat_key(self):
        """ If supplied we export the study event repeat key"""
        tested = StudyEventData('VISIT_1', study_event_repeat_key="1")(
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
        t = obj_to_doc(tested)
        self.assertEqual("StudyEventData", t.tag)
        self.assertEqual("1", t.attrib['StudyEventRepeatKey'])

    def test_only_add_formdata_once(self):
        """Test that an FormData object can only be added once"""
        fd = FormData("FORM1")
        self.tested << fd

        def do():
            self.tested << fd

        self.assertRaises(ValueError, do)

    def test_add_annotations(self):
        """Test we can add one or more annotations"""
        flags = [Flag(flag_value=FlagValue("Some value %s" % i, codelist_oid="ANOID%s" % i),
                      flag_type=FlagType("Some type %s" % i, codelist_oid="ANOTHEROID%s" % i)) for i in range(0, 3)]
        for i in range(0, 4):
            self.tested << Annotation(comment=Comment("Some Comment %s" % i), flags=flags)
        t = obj_to_doc(self.tested)
        self.assertEqual(self.__class__.__name__[4:], t.tag)
        self.assertTrue(len(t.getchildren()) == 5)  # one formdata + 4 annotations

    def test_add_signature(self):
        """Test we can add one signature"""
        self.tested << Signature(signature_id="Some ID",
                                 user_ref=UserRef(oid="AUser"),
                                 location_ref=LocationRef(oid="ALocation"),
                                 signature_ref=SignatureRef(oid="ASignature"),
                                 date_time_stamp=DateTimeStamp(date_time=datetime(year=2016,
                                                                                  month=12,
                                                                                  day=25,
                                                                                  hour=12,
                                                                                  minute=0,
                                                                                  second=0)))
        t = obj_to_doc(self.tested)
        self.assertEqual(self.__class__.__name__[4:], t.tag)
        self.assertTrue(len(t.getchildren()) == 2)  # 1 formdata + 1 signature

    def test_invalid_transaction_type_direct_assign(self):
        """Test transaction type will not allow you to set to invalid choice"""

        def do():
            self.tested.transaction_type = 'upsert'

        self.assertRaises(AttributeError, do)

    def test_invalid_transaction_type(self):
        """According to docs does not permit upserts"""

        def do():
            StudyEventData("V2", transaction_type='upsert')

        self.assertRaises(AttributeError, do)

    def test_only_accepts_formdata(self):
        """Test that only FormData can be inserted"""

        def do():
            # Bzzzt. Should be ItemGroupData
            self.tested << ItemData("Field1", "ValueC")

        self.assertRaises(ValueError, do)


class TestSubjectData(unittest.TestCase):
    """Test SubjectData classes"""

    def setUp(self):
        self.tested = SubjectData("SITE1", "SUBJECT1")(
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

        self.assertRaises(AttributeError, do)

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

        self.assertRaises(ValueError, do)

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
        t = obj_to_doc(self.tested)
        self.assertEqual(self.__class__.__name__[4:], t.tag)
        self.assertTrue(len(t.getchildren()) == 3)  # 1 StudyEventData + 1 SiteRef + 1 AuditRecord

    def test_add_annotations(self):
        """Test we can add one or more annotations"""
        flags = [Flag(flag_value=FlagValue("Some value %s" % i, codelist_oid="ANOID%s" % i),
                      flag_type=FlagType("Some type %s" % i, codelist_oid="ANOTHEROID%s" % i)) for i in range(0, 3)]
        for i in range(0, 4):
            self.tested << Annotation(comment=Comment("Some Comment %s" % i), flags=flags)
        t = obj_to_doc(self.tested)
        self.assertEqual(self.__class__.__name__[4:], t.tag)
        self.assertTrue(len(t.getchildren()) == 6)  # 1 StudyEventData + 1 SiteRef + 4 annotations

    def test_add_signature(self):
        """Test we can add one signature"""
        self.tested << Signature(signature_id="Some ID",
                                 user_ref=UserRef(oid="AUser"),
                                 location_ref=LocationRef(oid="ALocation"),
                                 signature_ref=SignatureRef(oid="ASignature"),
                                 date_time_stamp=DateTimeStamp(date_time=datetime(year=2016,
                                                                                  month=12,
                                                                                  day=25,
                                                                                  hour=12,
                                                                                  minute=0,
                                                                                  second=0)))
        t = obj_to_doc(self.tested)
        self.assertEqual(self.__class__.__name__[4:], t.tag)
        self.assertTrue(len(t.getchildren()) == 3)  # 1 studyeventdata + 1 SiteRef + 1 signature


class TestClinicalData(unittest.TestCase):
    """Test ClinicalData classes"""

    def setUp(self):
        self.tested = ClinicalData("STUDY1", "DEV")(
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

    def test_basic(self):
        """Test there are 3 children"""
        self.assertEqual("STUDY1", self.tested.projectname)
        self.assertEqual("DEV", self.tested.environment)
        # Test default MetadataVersionOID
        self.assertEqual("1", self.tested.metadata_version_oid)

    def test_metadata_version_oid(self):
        self.tested.metadata_version_oid = '2'
        doc = obj_to_doc(self.tested)
        self.assertEqual(doc.attrib["MetaDataVersionOID"], self.tested.metadata_version_oid)

    def test_only_accepts_subjectdata(self):
        """Test that only SubjectData can be inserted"""
        tested = ClinicalData("STUDY1", "DEV")

        def do():
            tested << object()

        self.assertRaises(ValueError, do)

    def test_only_accepts_one_subject(self):
        """Test that only one SubjectData can be inserted"""

        def do():
            self.tested << SubjectData("SITE2", "SUBJECT2")

        self.assertRaises(ValueError, do)

    def test_builder(self):
        """XML produced"""
        doc = obj_to_doc(self.tested)
        self.assertEqual(doc.tag, "ClinicalData")


class TestODM(unittest.TestCase):
    """Test ODM wrapper class"""

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

    def test_basic(self):
        """Basic tests"""
        # If no fileoid is given, a unique id is generated
        self.assertEqual(True, self.tested.fileoid is not None)
        self.assertEqual("My test message", self.tested.description)

    def test_assign_fileoid(self):
        """Test if you assign a fileoid it keeps it"""
        tested = ODM("MY TEST SYSTEM", fileoid="F1")
        self.assertEqual("F1", tested.fileoid)

    def test_only_accepts_valid_children(self):
        """Test that only ClinicalData or Study can be inserted"""

        def do():
            self.tested << ItemData("Field1", "ValueC")

        self.assertRaises(ValueError, do)

    def test_accepts_clinicaldata_and_study(self):
        """Test that accepts clinicaldata"""
        tested = ODM("MY TEST SYSTEM", fileoid="F1")
        cd = ClinicalData("Project1", "DEV")
        study = Study("PROJ1", project_type=Study.PROJECT)
        tested << cd
        tested << study
        self.assertEqual(study, tested.study)
        self.assertEqual(cd, tested.clinical_data)

    def test_getroot(self):
        """XML produced"""
        doc = self.tested.getroot()
        self.assertEqual(doc.tag, "ODM")
        self.assertEqual(doc.attrib["Originator"], "MY TEST SYSTEM")
        self.assertEqual(doc.attrib["Description"], self.tested.description)
        self.assertEqual("ClinicalData", doc.getchildren()[0].tag)

    def test_getroot_study(self):
        """XML produced with a study child"""
        tested = ODM("MY TEST SYSTEM", fileoid="F1")
        study = Study("PROJ1", project_type=Study.PROJECT)
        tested << study
        doc = tested.getroot()
        self.assertEqual(doc.tag, "ODM")
        self.assertEqual("Study", doc.getchildren()[0].tag)

    def test_str_well_formed(self):
        """Make an XML string from the object, parse it to ensure it's well formed"""
        doc = ET.fromstring(str(self.tested))
        NS_ODM = '{http://www.cdisc.org/ns/odm/v1.3}'
        self.assertEqual(doc.tag, NS_ODM + "ODM")
        self.assertEqual(doc.attrib["Originator"], "MY TEST SYSTEM")
        self.assertEqual(doc.attrib["Description"], self.tested.description)


if __name__ == '__main__':
    unittest.main()
