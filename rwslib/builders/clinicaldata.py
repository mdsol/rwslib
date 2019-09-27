# -*- coding: utf-8 -*-

from rwslib.builders.common import (
    ODMElement,
    TransactionalElement,
    bool_to_yes_no,
    dt_to_iso8601,
    VALID_ID_CHARS,
)
from rwslib.builders.modm import LastUpdateMixin, MilestoneMixin
from rwslib.builders.metadata import MeasurementUnitRef
from rwslib.builders.constants import ProtocolDeviationStatus, QueryStatusType

from collections import OrderedDict
from datetime import datetime
import re


class ClinicalData(ODMElement, LastUpdateMixin):
    """Models the ODM ClinicalData object"""

    def __init__(
        self, projectname, environment, metadata_version_oid="1", annotations=None
    ):
        """
        :param projectname: Name of Project in Medidata Rave
        :param environment: Rave Study Enviroment
        :param metadata_version_oid: MetadataVersion OID
        """
        super(ClinicalData, self).__init__()
        self.projectname = projectname
        self.environment = environment
        self.metadata_version_oid = metadata_version_oid
        #: collection of :class:`SubjectData` for the ClinicalData Element
        self.subject_data = []
        self.annotations = annotations

    def build(self, builder):
        """Build XML by appending to builder"""
        params = dict(
            MetaDataVersionOID=str(self.metadata_version_oid),
            StudyOID="%s (%s)" % (self.projectname, self.environment),
        )

        # mixins
        self.mixin_params(params)

        builder.start("ClinicalData", params)
        # Ask children
        if self.subject_data:
            for subject in self.subject_data:
                subject.build(builder)
        # Add the Annotations
        if self.annotations is not None:
            self.annotations.build(builder)
        builder.end("ClinicalData")

    def __lshift__(self, other):
        """Override << operator"""
        if not isinstance(other, (SubjectData, Annotations)):
            raise ValueError(
                "ClinicalData object can only receive SubjectData or Annotations object"
            )
        self.set_list_attribute(other, SubjectData, "subject_data")
        self.set_single_attribute(other, Annotations, "annotations")
        return other


class SubjectData(TransactionalElement, LastUpdateMixin, MilestoneMixin):
    """Models the ODM SubjectData and ODM SiteRef objects"""

    ALLOWED_TRANSACTION_TYPES = ["Insert", "Update", "Upsert", "Context", "Remove"]

    def __init__(
        self,
        site_location_oid,
        subject_key,
        subject_key_type="SubjectName",
        transaction_type="Update",
    ):
        """
        :param str site_location_oid: :class:`SiteLocation` OID
        :param str subject_key: Value for SubjectKey
        :param str subject_key_type: Specifier as to the type of SubjectKey (either **SubjectName** or **SubjectUUID**)
        :param str transaction_type: Transaction Type for Data (one of **Insert**, **Update**, **Upsert**, **Context**, **Remove**)
        """
        super(self.__class__, self).__init__(transaction_type)
        self.sitelocationoid = site_location_oid
        self.subject_key = subject_key
        self.subject_key_type = subject_key_type
        #: collection of :class:`StudyEventData`
        self.study_events = []
        #: collection of :class:`Annotation`
        self.annotations = []
        #: :class:`AuditRecord` for SubjectData - *Not Supported By Rave*
        self.audit_record = None
        #: :class:`Signature` for SubjectData
        self.signature = None
        #: :class:`SiteRef`
        self.siteref = None

    def build(self, builder):
        """Build XML by appending to builder"""
        params = dict(SubjectKey=self.subject_key)
        params["mdsol:SubjectKeyType"] = self.subject_key_type

        if self.transaction_type is not None:
            params["TransactionType"] = self.transaction_type

        # mixins
        self.mixin()
        self.mixin_params(params)

        builder.start("SubjectData", params)

        # Ask children
        if self.audit_record is not None:
            self.audit_record.build(builder)

        if self.siteref:
            self.siteref.build(builder)
        else:
            builder.start("SiteRef", {"LocationOID": self.sitelocationoid})
            builder.end("SiteRef")

        for event in self.study_events:
            event.build(builder)

        if self.signature is not None:
            self.signature.build(builder)

        for annotation in self.annotations:
            annotation.build(builder)

        builder.end("SubjectData")

    def __lshift__(self, other):
        """Override << operator"""
        if not isinstance(
            other, (StudyEventData, AuditRecord, Annotation, Signature, SiteRef)
        ):
            raise ValueError(
                "SubjectData object can only receive StudyEventData, AuditRecord, "
                "Annotation or Signature object"
            )

        self.set_list_attribute(other, Annotation, "annotations")
        self.set_list_attribute(other, StudyEventData, "study_events")
        self.set_single_attribute(other, AuditRecord, "audit_record")
        self.set_single_attribute(other, Signature, "signature")
        self.set_single_attribute(other, SiteRef, "siteref")

        return other


class StudyEventData(TransactionalElement, LastUpdateMixin, MilestoneMixin):
    """Models the ODM StudyEventData object"""

    ALLOWED_TRANSACTION_TYPES = ["Insert", "Update", "Upsert", "Context", "Remove"]

    def __init__(
        self, study_event_oid, transaction_type="Update", study_event_repeat_key=None
    ):
        """
        :param str study_event_oid: :class:`StudyEvent` OID
        :param str transaction_type: Transaction Type for Data (one of **Insert**, **Update**, **Upsert**, **Context**, **Remove**)
        :param int study_event_repeat_key: :attr:`StudyEventRepeatKey` for StudyEventData
        """
        super(self.__class__, self).__init__(transaction_type)
        self.study_event_oid = study_event_oid
        self.study_event_repeat_key = study_event_repeat_key
        #: :class:`FormData` part of Study Event Data
        self.forms = []
        #: :class:`Annotation` for Study Event Data  - *Not Supported by Rave*
        self.annotations = []
        #: :class:`Signature` for Study Event Data
        self.signature = None

    def build(self, builder):
        """Build XML by appending to builder
        :Example:
        <StudyEventData StudyEventOID="SCREENING" StudyEventRepeatKey="1" TransactionType="Update">

        """
        params = dict(StudyEventOID=self.study_event_oid)

        if self.transaction_type is not None:
            params["TransactionType"] = self.transaction_type

        if self.study_event_repeat_key is not None:
            params["StudyEventRepeatKey"] = str(self.study_event_repeat_key)

        # mixins
        self.mixin()
        self.mixin_params(params)

        builder.start("StudyEventData", params)

        # Ask children
        for form in self.forms:
            form.build(builder)

        if self.signature is not None:
            self.signature.build(builder)

        for annotation in self.annotations:
            annotation.build(builder)

        builder.end("StudyEventData")

    def __lshift__(self, other):
        """Override << operator"""
        if not isinstance(other, (FormData, Annotation, Signature)):
            raise ValueError(
                "StudyEventData object can only receive FormData, Signature or Annotation objects"
            )
        self.set_list_attribute(other, FormData, "forms")
        self.set_single_attribute(other, Signature, "signature")
        self.set_list_attribute(other, Annotation, "annotations")
        return other


class FormData(TransactionalElement, LastUpdateMixin, MilestoneMixin):
    """Models the ODM FormData object"""

    ALLOWED_TRANSACTION_TYPES = ["Insert", "Update", "Upsert", "Context", "Remove"]

    def __init__(self, formoid, transaction_type=None, form_repeat_key=None):
        """
        :param str formoid: :class:`FormDef` OID
        :param str transaction_type: Transaction Type for Data (one of **Insert**, **Update**, **Upsert**, **Context**, **Remove**)
        :param str form_repeat_key: Repeat Key for FormData
        """
        super(FormData, self).__init__(transaction_type)
        self.formoid = formoid
        self.form_repeat_key = form_repeat_key
        self.itemgroups = []
        #: :class:`Signature` for FormData
        self.signature = None  # type: Signature
        #: Collection of :class:`Annotation` for FormData - *Not supported by Rave*
        self.annotations = []  # type: list(Annotation)

    def build(self, builder):
        """Build XML by appending to builder
        :Example:
        <FormData FormOID="MH" TransactionType="Update">

        """
        params = dict(FormOID=self.formoid)

        if self.transaction_type is not None:
            params["TransactionType"] = self.transaction_type

        if self.form_repeat_key is not None:
            params["FormRepeatKey"] = str(self.form_repeat_key)

        # mixins
        self.mixin()
        self.mixin_params(params)

        builder.start("FormData", params)

        # Ask children
        for itemgroup in self.itemgroups:
            itemgroup.build(builder, self.formoid)

        if self.signature is not None:
            self.signature.build(builder)

        for annotation in self.annotations:
            annotation.build(builder)

        builder.end("FormData")

    def __lshift__(self, other):
        """Override << operator"""
        if not isinstance(other, (Signature, ItemGroupData, Annotation)):
            raise ValueError(
                "FormData object can only receive ItemGroupData, Signature or Annotation objects (not '{}')".format(
                    other
                )
            )
        self.set_list_attribute(other, ItemGroupData, "itemgroups")
        self.set_list_attribute(other, Annotation, "annotations")
        self.set_single_attribute(other, Signature, "signature")
        return other


class ItemGroupData(TransactionalElement, LastUpdateMixin, MilestoneMixin):
    """
    Models the ODM ItemGroupData object.

    .. note:: No name for the ItemGroupData element is required. This is built automatically by the form.
    """

    ALLOWED_TRANSACTION_TYPES = ["Insert", "Update", "Upsert", "Context", "Remove"]

    def __init__(
        self,
        itemgroupoid=None,
        transaction_type=None,
        item_group_repeat_key=None,
        whole_item_group=False,
        annotations=None,
    ):
        """
        :param str transaction_type: Transaction Type for Data (one of **Insert**, **Update**, **Upsert**, **Context**, **Remove**)
        :param int item_group_repeat_key: RepeatKey for the ItemGroupData
        :param bool whole_item_group: Is this the entire ItemGroupData, or just parts? - *Rave specific attribute*
        :param annotations: Annotation for the ItemGroup - *Not supported by Rave*
        :type annotations: list(Annotation) or Annotation
        """
        super(self.__class__, self).__init__(transaction_type)
        self.item_group_repeat_key = item_group_repeat_key
        self.whole_item_group = whole_item_group
        self.items = OrderedDict()
        self.annotations = []
        if annotations:
            # Add the annotations
            if isinstance(annotations, Annotation):
                self << annotations
            elif isinstance(annotations, list):
                for annotation in annotations:
                    self << annotation
        #: :class:`Signature` for ItemGroupData
        self.signature = None
        self.itemgroupoid = itemgroupoid

    def build(self, builder, formname=None):
        """Build XML by appending to builder"""

        params = dict(ItemGroupOID=formname if formname else self.itemgroupoid)

        if self.transaction_type is not None:
            params["TransactionType"] = self.transaction_type

        if self.item_group_repeat_key is not None:
            params["ItemGroupRepeatKey"] = str(
                self.item_group_repeat_key
            )  # may be @context for transaction type upsert or context

        params["mdsol:Submission"] = (
            "WholeItemGroup" if self.whole_item_group else "SpecifiedItemsOnly"
        )

        # mixins
        self.mixin()
        self.mixin_params(params)

        builder.start("ItemGroupData", params)

        # Ask children
        for item in self.items.values():
            item.build(builder)

        # Add annotations
        for annotation in self.annotations:
            annotation.build(builder)

        # Add the signature if it exists
        if self.signature is not None:
            self.signature.build(builder)
        builder.end("ItemGroupData")

    def __lshift__(self, other):
        """Override << operator"""
        if not isinstance(other, (ItemData, Annotation, Signature)):
            raise ValueError(
                "ItemGroupData object can only receive ItemData, Signature or Annotation objects"
            )

        self.set_list_attribute(other, Annotation, "annotations")
        self.set_single_attribute(other, Signature, "signature")
        if isinstance(other, ItemData):
            if other.itemoid in self.items:
                raise ValueError(
                    "ItemGroupData object with that itemoid is already in the ItemGroupData object"
                )
            self.items[other.itemoid] = other
        return other


class ItemData(TransactionalElement, LastUpdateMixin, MilestoneMixin):
    """Models the ODM ItemData object"""

    ALLOWED_TRANSACTION_TYPES = ["Insert", "Update", "Upsert", "Context", "Remove"]

    def __init__(
        self,
        itemoid,
        value,
        specify_value=None,
        transaction_type=None,
        lock=None,
        freeze=None,
        verify=None,
    ):
        """
        :param str itemoid: OID for the matching :class:`ItemDef`
        :param str value: Value for the the ItemData
        :param str specify_value: 'If other, specify' value - *Rave specific attribute*
        :param str transaction_type: Transaction Type for Data (one of **Insert**, **Update**, **Upsert**, **Context**, **Remove**)
        :param bool lock: Lock the DataPoint? - *Rave specific attribute*
        :param bool freeze: Freeze the DataPoint? - *Rave specific attribute*
        :param bool verify: Verify the DataPoint? - *Rave specific attribute*
        """
        super(self.__class__, self).__init__(transaction_type)
        self.itemoid = itemoid
        self.value = value

        self.specify_value = specify_value
        self.lock = lock
        self.freeze = freeze
        self.verify = verify
        #: the corresponding :class:`AuditRecord` for the DataPoint
        self.audit_record = None
        #: the list of :class:`MdsolQuery` on the DataPoint  - *Rave Specific Attribute*
        self.queries = []
        #: the list of :class:`Annotation` on the DataPoint - *Not supported by Rave*
        self.annotations = []
        #: the corresponding :class:`MeasurementUnitRef` for the DataPoint
        self.measurement_unit_ref = None
        #: the list of :class:`MdsolProtocolDeviation` references on the DataPoint - *Rave Specific Attribute*
        self.deviations = []

    def build(self, builder):
        """
        Build XML by appending to builder
        """
        params = dict(ItemOID=self.itemoid)

        if self.transaction_type is not None:
            params["TransactionType"] = self.transaction_type

        if self.value in [None, ""]:
            params["IsNull"] = "Yes"
        else:
            params["Value"] = str(self.value)

        if self.specify_value is not None:
            params["mdsol:SpecifyValue"] = self.specify_value

        if self.lock is not None:
            params["mdsol:Lock"] = bool_to_yes_no(self.lock)

        if self.freeze is not None:
            params["mdsol:Freeze"] = bool_to_yes_no(self.freeze)

        if self.verify is not None:
            params["mdsol:Verify"] = bool_to_yes_no(self.verify)

        # mixins
        self.mixin()
        self.mixin_params(params)

        builder.start("ItemData", params)

        if self.audit_record is not None:
            self.audit_record.build(builder)

        # Measurement unit ref must be after audit record or RWS complains
        if self.measurement_unit_ref is not None:
            self.measurement_unit_ref.build(builder)

        for query in self.queries:  # type: MdsolQuery
            query.build(builder)

        for deviation in self.deviations:  # type: MdsolProtocolDeviation
            deviation.build(builder)

        for annotation in self.annotations:  # type: Annotation
            annotation.build(builder)

        builder.end("ItemData")

    def __lshift__(self, other):
        if not isinstance(
            other,
            (
                MeasurementUnitRef,
                AuditRecord,
                MdsolQuery,
                Annotation,
                MdsolProtocolDeviation,
            ),
        ):
            raise ValueError(
                "ItemData object can only receive MeasurementUnitRef, AuditRecord, Annotation,"
                "MdsolProtocolDeviation or MdsolQuery objects"
            )
        self.set_single_attribute(other, MeasurementUnitRef, "measurement_unit_ref")
        self.set_single_attribute(other, AuditRecord, "audit_record")
        self.set_list_attribute(other, MdsolQuery, "queries")
        self.set_list_attribute(other, MdsolProtocolDeviation, "deviations")
        self.set_list_attribute(other, Annotation, "annotations")
        return other


class Signature(ODMElement):
    """
    An electronic signature applies to a collection of clinical data.
    This indicates that some user accepts legal responsibility for that data.
    See 21 CFR Part 11.
    The signature identifies the person signing, the location of signing,
    the signature meaning (via the referenced SignatureDef),
    the date and time of signing,
    and (in the case of a digital signature) an encrypted hash of the included data.
    """

    def __init__(
        self,
        signature_id=None,
        user_ref=None,
        location_ref=None,
        signature_ref=None,
        date_time_stamp=None,
    ):
        #: Unique ID for Signature
        """
        :param UserRef user_ref: :class:`UserRef` for :class:`User` signing Data
        :param LocationRef location_ref: :class:`LocationRef` for :class:`Location` of signing
        :param SignatureRef signature_ref: :class:`SignatureRef` for :class:`SignatureDef` providing signature meaning
        :param date_time_stamp: :class:`DateTimeStamp` for the time of Signature
        """
        self._id = None
        if signature_id:
            self.signature_id = signature_id
        self.user_ref = user_ref
        self.location_ref = location_ref
        self.signature_ref = signature_ref
        self.date_time_stamp = date_time_stamp

    @property
    def signature_id(self):
        """
        The ID for the Signature

        .. note:: If a Signature element is contained within a Signatures element, the ID attribute is required.
        """
        return self._id

    @signature_id.setter
    def signature_id(self, id):
        """Set the ID for the Signature"""
        self._id = id

    def build(self, builder):
        """
        Build XML by appending to builder
        """

        params = {}
        if self.signature_id is not None:
            # If a Signature element is contained within a Signatures element, the ID attribute is required.
            params["ID"] = self.signature_id

        builder.start("Signature", params)

        if self.user_ref is None:
            raise ValueError("User Reference not set.")
        self.user_ref.build(builder)

        if self.location_ref is None:
            raise ValueError("Location Reference not set.")
        self.location_ref.build(builder)

        if self.signature_ref is None:
            raise ValueError("Signature Reference not set.")
        self.signature_ref.build(builder)

        if self.date_time_stamp is None:
            raise ValueError("DateTime not set.")
        self.date_time_stamp.build(builder)

        builder.end("Signature")

    def __lshift__(self, other):
        if not isinstance(other, (UserRef, LocationRef, SignatureRef, DateTimeStamp)):
            raise ValueError(
                "Signature cannot accept a child element of type %s"
                % other.__class__.__name__
            )

        # Order is important, apparently
        self.set_single_attribute(other, UserRef, "user_ref")
        self.set_single_attribute(other, LocationRef, "location_ref")
        self.set_single_attribute(other, SignatureRef, "signature_ref")
        self.set_single_attribute(other, DateTimeStamp, "date_time_stamp")
        return other


class Annotation(TransactionalElement):
    """
    A general note about clinical data.
    If an annotation has both a comment and flags, the flags should be related to the comment.

    .. note:: Annotation is not supported by Medidata Rave
    """

    ALLOWED_TRANSACTION_TYPES = ["Insert", "Update", "Remove", "Upsert", "Context"]

    def __init__(
        self,
        annotation_id=None,
        seqnum=1,
        flags=None,
        comment=None,
        transaction_type=None,
    ):
        """
        :param id: ID for this Annotation (required if contained within an Annotations element)
        :type id: str or None
        :param int seqnum: :attr:`SeqNum` for Annotation
        :param flags: one or more :class:`Flag` for the Annotation
        :type flags: Flag or list(Flag)
        :param comment: one or more :class:`Comment` for the Annotation
        :type comment: Comment
        :param transaction_type: :attr:`TransactionType` for Annotation (one of **Insert**, **Update**, *Remove*, **Upsert**, **Context**)
        """
        super(Annotation, self).__init__(transaction_type=transaction_type)
        # initialise the flags collection
        self.flags = []
        if flags:
            if isinstance(flags, (list, tuple)):
                for flag in flags:
                    self << flag
            elif isinstance(flags, Flag):
                self << flags
            else:
                raise AttributeError("Flags attribute should be an iterable or Flag")
        self._id = None
        if annotation_id is not None:
            self.annotation_id = annotation_id
        self._seqnum = None
        if seqnum is not None:
            # validate the input
            self.seqnum = seqnum
        self.comment = comment

    @property
    def annotation_id(self):
        """
        ID for annotation

        .. note:: If an Annotation is contained with an Annotations element, the ID attribute is required.
        """
        return self._id

    @annotation_id.setter
    def annotation_id(self, value):
        """Set ID for Annotation"""
        if value in [None, ""] or str(value).strip() == "":
            raise AttributeError("Invalid ID value supplied")
        self._id = value

    @property
    def seqnum(self):
        """
        SeqNum attribute (a small positive integer) uniquely identifies the annotation within its parent entity.
        """
        return self._seqnum

    @seqnum.setter
    def seqnum(self, value):
        """
        Set SeqNum for Annotation
        :param value: SeqNum value
        :type value: int
        """
        if not re.match(r"\d+", str(value)) or value < 0:
            raise AttributeError("Invalid SeqNum value supplied")
        self._seqnum = value

    def build(self, builder):
        """
        Build XML by appending to builder
        """
        params = {}

        # Add in the transaction type
        if self.transaction_type is not None:
            params["TransactionType"] = self.transaction_type

        if self.seqnum is None:
            # SeqNum is not optional (and defaulted)
            raise ValueError("SeqNum is not set.")  # pragma: no cover
        params["SeqNum"] = str(self.seqnum)

        if self.annotation_id is not None:
            # If an Annotation is contained with an Annotations element,
            # the ID attribute is required.
            params["ID"] = self.annotation_id

        builder.start("Annotation", params)

        if self.flags in (None, []):
            raise ValueError("Flag is not set.")

        # populate the flags
        for flag in self.flags:
            flag.build(builder)

        # add the Comment, if it exists
        if self.comment is not None:
            self.comment.build(builder)

        builder.end("Annotation")

    def __lshift__(self, other):
        if not isinstance(other, (Flag, Comment)):
            raise ValueError(
                "Annotation cannot accept a child element of type %s"
                % other.__class__.__name__
            )

        self.set_single_attribute(other, Comment, "comment")
        self.set_list_attribute(other, Flag, "flags")
        return other


class Annotations(ODMElement):
    """
    Groups Annotation elements referenced by ItemData[TYPE] elements.
    """

    def __init__(self, annotations=[]):
        self.annotations = []
        for annotation in annotations:
            self << annotation

    def build(self, builder):
        """
        Build XML by appending to builder
        """
        builder.start("Annotations")

        # populate the flags
        for annotation in self.annotations:
            annotation.build(builder)

        builder.end("Annotations")

    def __lshift__(self, other):
        if not isinstance(other, (Annotation,)):
            raise ValueError(
                "Annotations cannot accept a child element of type %s"
                % other.__class__.__name__
            )

        self.set_list_attribute(other, Annotation, "annotations")
        return other


class Comment(ODMElement):
    """
    A free-text (uninterpreted) comment about clinical data.
    The comment may have come from the Sponsor or the clinical Site.

    .. note:: Comment is not supported by Medidata Rave
    """

    VALID_SPONSOR_OR_SITE_RESPONSES = ["Sponsor", "Site"]

    def __init__(self, text=None, sponsor_or_site=None):
        """
        :param str text: Text for Comment
        :param str sponsor_or_site: Originator flag for Comment (either _Sponsor_ or _Site_)
        """
        self._text = text
        self._sponsor_or_site = sponsor_or_site

    @property
    def text(self):
        """Text content of Comment"""
        return self._text

    @text.setter
    def text(self, value):
        """Set Text content for Comment (validation of input)"""
        if value in (None, "") or value.strip() == "":
            raise AttributeError("Empty text value is invalid.")
        self._text = value

    @property
    def sponsor_or_site(self):
        """Originator of comment (either Sponsor or Site)"""
        return self._sponsor_or_site

    @sponsor_or_site.setter
    def sponsor_or_site(self, value):
        """Set Originator with validation of input"""
        if value not in Comment.VALID_SPONSOR_OR_SITE_RESPONSES:
            raise AttributeError(
                "%s sponsor_or_site value of %s is not valid"
                % (self.__class__.__name__, value)
            )
        self._sponsor_or_site = value

    def build(self, builder):
        """
        Build XML by appending to builder
        """
        if self.text is None:
            raise ValueError("Text is not set.")
        params = {}
        if self.sponsor_or_site is not None:
            params["SponsorOrSite"] = self.sponsor_or_site

        builder.start("Comment", params)
        builder.data(self.text)
        builder.end("Comment")


class Flag(ODMElement):
    """
    A machine-processable annotation on clinical data.

    .. note:: Flag is not supported by Rave
    """

    def __init__(self, flag_type=None, flag_value=None):
        """
        :param FlagType flag_type: Type for Flag
        :param FlagValue flag_value: Value for Flag
        """
        self.flag_type = None
        self.flag_value = None
        if flag_type is not None:
            self << flag_type
        if flag_value is not None:
            self << flag_value

    def build(self, builder):
        """
        Build XML by appending to builder
        """
        builder.start("Flag", {})

        if self.flag_type is not None:
            self.flag_type.build(builder)

        if self.flag_value is None:
            raise ValueError("FlagValue is not set.")
        self.flag_value.build(builder)

        builder.end("Flag")

    def __lshift__(self, other):
        if not isinstance(other, (FlagType, FlagValue)):
            raise ValueError(
                "Flag cannot accept a child element of type %s"
                % other.__class__.__name__
            )

        # Order is important, apparently
        self.set_single_attribute(other, FlagType, "flag_type")
        self.set_single_attribute(other, FlagValue, "flag_value")
        return other


class FlagType(ODMElement):
    """
    The type of flag. This determines the purpose and semantics of the flag.
    Different applications are expected to be interested in different types of flags.
    The actual value must be a member of the referenced CodeList.

    .. note:: FlagType is not supported by Rave
    """

    def __init__(self, flag_type, codelist_oid=None):
        """
        :param flag_type: Type for :class:`Flag`
        """
        self.flag_type = flag_type
        self._codelist_oid = None
        if codelist_oid is not None:
            self.codelist_oid = codelist_oid

    @property
    def codelist_oid(self):
        """Reference to the :class:`CodeList` for the FlagType"""
        return self._codelist_oid

    @codelist_oid.setter
    def codelist_oid(self, value):
        if value in (None, "") or value.strip() == "":
            raise AttributeError("Empty CodeListOID value is invalid.")
        self._codelist_oid = value

    def build(self, builder):
        """
        Build XML by appending to builder
        """
        if self.codelist_oid is None:
            raise ValueError("CodeListOID not set.")
        builder.start("FlagType", dict(CodeListOID=self.codelist_oid))
        builder.data(self.flag_type)
        builder.end("FlagType")


class FlagValue(ODMElement):
    """
    The value of the flag. The meaning of this value is typically dependent on the associated FlagType.
    The actual value must be a member of the referenced CodeList.

    .. note::  FlagValue is not supported by Rave
    """

    def __init__(self, flag_value, codelist_oid=None):
        """
        :param flag_value: Value for :class:`Flag`
        """
        self.flag_value = flag_value
        self._codelist_oid = None
        if codelist_oid is not None:
            self.codelist_oid = codelist_oid

    @property
    def codelist_oid(self):
        """Reference to the :class:`CodeList` for the FlagType"""
        return self._codelist_oid

    @codelist_oid.setter
    def codelist_oid(self, value):
        if value in (None, "") or value.strip() == "":
            raise AttributeError("Empty CodeListOID value is invalid.")
        self._codelist_oid = value

    def build(self, builder):
        """
        Build XML by appending to builder
        """
        if self.codelist_oid is None:
            raise ValueError("CodeListOID not set.")
        builder.start("FlagValue", dict(CodeListOID=self.codelist_oid))
        builder.data(self.flag_value)
        builder.end("FlagValue")


class UserRef(ODMElement):
    """
    Reference to a :class:`User`
    """

    def __init__(self, oid):
        """
        :param str oid: OID for referenced :class:`User`
        """
        self.oid = oid

    def build(self, builder):
        """
        Build XML by appending to builder
        """
        builder.start("UserRef", dict(UserOID=self.oid))
        builder.end("UserRef")


class LocationRef(ODMElement):
    """
    Reference to a :class:`Location`
    """

    def __init__(self, oid):
        """
        :param str oid: OID for referenced :class:`Location`
        """
        self.oid = oid

    def build(self, builder):
        """
        Build XML by appending to builder
        """
        builder.start("LocationRef", dict(LocationOID=str(self.oid)))
        builder.end("LocationRef")


class SiteRef(ODMElement, LastUpdateMixin):
    """
    Reference to a :class:`Location`
    The default value is `SiteName`, and the value `SiteUUID` implies that the `LocationOID`
    .. note:: The `mdsol:LocationOIDType` attribute should be used to indicate the type of `LocationOID`
    """

    def __init__(self, oid):
        """
        :param str oid: OID for referenced :class:`Location`
        """
        self.oid = oid

    def build(self, builder):
        """
        Build XML by appending to builder
        """
        params = dict(LocationOID=self.oid)
        # mixins
        self.mixin()
        self.mixin_params(params)

        builder.start("SiteRef", params)
        builder.end("SiteRef")


class SignatureRef(ODMElement):
    """
    Reference to a Signature
    """

    def __init__(self, oid):
        """
        :param str oid: OID for referenced :class:`Signature`
        """
        self.oid = oid

    def build(self, builder):
        """
        Build XML by appending to builder
        """
        builder.start("SignatureRef", dict(SignatureOID=self.oid))
        builder.end("SignatureRef")


class ReasonForChange(ODMElement):
    """
    A user-supplied reason for a data change.
    """

    def __init__(self, reason):
        """
        :param str reason: Supplied Reason for change
        """
        self.reason = reason

    def build(self, builder):
        """
        Build XML by appending to builder
        """
        builder.start("ReasonForChange", {})
        builder.data(self.reason)
        builder.end("ReasonForChange")


class DateTimeStamp(ODMElement):
    """
    The date/time that the data entry, modification, or signature was performed.
    This applies to the initial occurrence of the action, not to subsequent transfers between computer systems.
    """

    def __init__(self, date_time):
        #: specified DateTime for event
        self.date_time = date_time

    def build(self, builder):
        """
        Build XML by appending to builder
        """
        builder.start("DateTimeStamp", {})
        if isinstance(self.date_time, datetime):
            builder.data(dt_to_iso8601(self.date_time))
        else:
            builder.data(self.date_time)
        builder.end("DateTimeStamp")


class SourceID(ODMElement):
    """
    Information that identifies the source of the data within an originating system. 
      It is only meaningful within the context of that system.
    """

    def __init__(self, source_id):
        #: specified DateTime for event
        self.source_id = source_id

    def build(self, builder):
        """
        Build XML by appending to builder
        """
        builder.start("SourceID", {})
        builder.data(self.source_id)
        builder.end("SourceID")


class AuditRecord(ODMElement):
    """
    An AuditRecord carries information pertaining to the creation, deletion, or modification of clinical data.
    This information includes who performed that action, and where, when, and why that action was performed.

    .. note:: AuditRecord is supported only by :class:`ItemData` in Rave
    """

    EDIT_MONITORING = "Monitoring"
    EDIT_DATA_MANAGEMENT = "DataManagement"
    EDIT_DB_AUDIT = "DBAudit"
    EDIT_POINTS = [EDIT_MONITORING, EDIT_DATA_MANAGEMENT, EDIT_DB_AUDIT]

    def __init__(
        self,
        edit_point=None,
        used_imputation_method=None,
        identifier=None,
        include_file_oid=None,
    ):
        """
        :param str identifier: Audit identifier
        :param str edit_point: EditPoint attribute identifies the phase of data processing in which action occurred
            (*Monitoring*, *DataManagement*, *DBAudit*)
        :param bool used_imputation_method: Indicates whether the action involved the use of a Method
        :param bool include_file_oid: Include the FileOID in the AuditRecord
        """
        self._edit_point = None
        self.edit_point = edit_point
        self.used_imputation_method = used_imputation_method
        self._id = None
        if identifier:
            self.audit_id = identifier
        self.include_file_oid = include_file_oid
        #: :class:`UserRef` for the AuditRecord
        self.user_ref = None
        #: :class:`LocationRef` for the AuditRecord
        self.location_ref = None
        #: :class:`ReasonForChange` for the AuditRecord
        self.reason_for_change = None
        #: :class:`DateTimeStamp` for the AuditRecord
        self.date_time_stamp = None
        #: :class:`SourceID` for the AuditRecord
        self.source_id = None

    @property
    def audit_id(self):
        """
        AuditRecord ID

        .. note:: If an AuditRecord is contained within an AuditRecords element, the ID attribute must be provided.
        """
        return self._id

    @audit_id.setter
    def audit_id(self, value):
        if value not in [None, ""] and str(value).strip() != "":
            val = str(value).strip()[0]
            if val not in VALID_ID_CHARS:
                raise AttributeError(
                    '%s id cannot start with "%s" character'
                    % (self.__class__.__name__, val)
                )
        self._id = value

    @property
    def edit_point(self):
        """
        EditPoint attribute identifies the phase of data processing in which action occurred
            (*Monitoring*, *DataManagement*, *DBAudit*)
        """
        return self._edit_point

    @edit_point.setter
    def edit_point(self, value):
        if value is not None:
            if value not in self.EDIT_POINTS:
                raise AttributeError(
                    "%s edit_point must be one of %s not %s"
                    % (self.__class__.__name__, ",".join(self.EDIT_POINTS), value)
                )
        self._edit_point = value

    def build(self, builder):
        """Build XML by appending to builder"""
        params = {}

        if self.edit_point is not None:
            params["EditPoint"] = self.edit_point

        if self.used_imputation_method is not None:
            params["UsedImputationMethod"] = bool_to_yes_no(self.used_imputation_method)

        if self.audit_id is not None:
            params["ID"] = str(self.audit_id)

        if self.include_file_oid is not None:
            params["mdsol:IncludeFileOID"] = bool_to_yes_no(self.include_file_oid)

        builder.start("AuditRecord", params)
        if self.user_ref is None:
            raise ValueError("User Reference not set.")
        self.user_ref.build(builder)

        if self.location_ref is None:
            raise ValueError("Location Reference not set.")
        self.location_ref.build(builder)

        if self.date_time_stamp is None:
            raise ValueError("DateTime not set.")

        self.date_time_stamp.build(builder)

        # Optional
        if self.source_id:
            self.source_id.build(builder)
        # Optional
        if self.reason_for_change is not None:
            self.reason_for_change.build(builder)

        builder.end("AuditRecord")

    def __lshift__(self, other):
        if not isinstance(
            other, (UserRef, LocationRef, DateTimeStamp, ReasonForChange, SourceID)
        ):
            raise ValueError(
                "AuditRecord cannot accept a child element of type %s"
                % other.__class__.__name__
            )

        # Order is important, apparently
        self.set_single_attribute(other, UserRef, "user_ref")
        self.set_single_attribute(other, LocationRef, "location_ref")
        self.set_single_attribute(other, DateTimeStamp, "date_time_stamp")
        self.set_single_attribute(other, ReasonForChange, "reason_for_change")
        self.set_single_attribute(other, SourceID, "source_id")
        return other


class MdsolProtocolDeviation(TransactionalElement):
    """
    Extension for Protocol Deviations in Rave

    .. note::
        * This is a Medidata Rave Specific Extension
        * This primarily exists as a mechanism for use by the Clinical Audit Record Service, but it is useful to define for the builders

    """

    ALLOWED_TRANSACTION_TYPES = ["Insert"]

    def __init__(
        self, value, status, repeat_key=1, code=None, klass=None, transaction_type=None
    ):
        """
        :param str value: Value for the Protocol Deviation 
        :param rwslib.builder_constants.ProtocolDeviationStatus status: 
        :param int repeat_key: RepeatKey for the Protocol Deviation
        :param basestring code: Protocol Deviation Code
        :param basestring klass: Protocol Deviation Class 
        :param transaction_type: Transaction Type for the Protocol Deviation
        """
        super(MdsolProtocolDeviation, self).__init__(transaction_type=transaction_type)
        self._status = None
        self._repeat_key = None
        self.status = status
        self.value = value
        self.repeat_key = repeat_key
        self.code = code
        self.pdclass = klass

    @property
    def repeat_key(self):
        return self._repeat_key

    @repeat_key.setter
    def repeat_key(self, value):
        if isinstance(value, int):
            self._repeat_key = value
        else:
            raise ValueError("RepeatKey should be an integer, not {}".format(value))

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        if isinstance(value, ProtocolDeviationStatus):
            self._status = value
        else:
            raise ValueError(
                "Status {} is not a valid ProtocolDeviationStatus".format(value)
            )

    def build(self, builder):
        """Build XML by appending to builder"""
        params = dict(
            Value=self.value,
            Status=self.status.value,
            ProtocolDeviationRepeatKey=self.repeat_key,
        )

        if self.code:
            params["Code"] = self.code
        if self.pdclass:
            params["Class"] = self.pdclass
        if self.transaction_type:
            params["TransactionType"] = self.transaction_type
        builder.start("mdsol:ProtocolDeviation", params)
        builder.end("mdsol:ProtocolDeviation")


class MdsolQuery(ODMElement):
    """
    MdsolQuery extension element for Queries at item level only

    .. note:: This is a Medidata Rave specific extension
    """

    def __init__(
        self,
        value=None,
        query_repeat_key=None,
        recipient=None,
        status=None,
        requires_response=None,
        response=None,
    ):
        """
        :param str value: Query Value
        :param int query_repeat_key: Repeat key for Query
        :param str recipient: Recipient for Query
        :param QueryStatusType status: Query status
        :param bool requires_response: Does this Query need a response?
        :param response: Query response (if any)
        :type response: str or None
        """
        self.value = value
        self.query_repeat_key = query_repeat_key
        self.recipient = recipient
        self._status = None
        self.status = status
        self.requires_response = requires_response
        self.response = response

    @property
    def status(self):
        """Query Status"""
        return self._status

    @status.setter
    def status(self, value):
        """Set Query Status"""
        if value is not None:
            if not isinstance(value, QueryStatusType):
                raise AttributeError(
                    "%s action type is invalid in mdsol:Query." % (value,)
                )
        self._status = value

    def build(self, builder):
        """
        Build XML by appending to builder
        """
        params = {}

        if self.value is not None:
            params["Value"] = str(self.value)

        if self.query_repeat_key is not None:
            params["QueryRepeatKey"] = str(self.query_repeat_key)

        if self.recipient is not None:
            params["Recipient"] = str(self.recipient)

        if self.status is not None:
            params["Status"] = self.status.value

        if self.requires_response is not None:
            params["RequiresResponse"] = bool_to_yes_no(self.requires_response)

        # When closing a query
        if self.response is not None:
            params["Response"] = str(self.response)

        builder.start("mdsol:Query", params)
        builder.end("mdsol:Query")
