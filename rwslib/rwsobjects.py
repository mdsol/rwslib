__author__ = "isparks"

from lxml import etree

MEDI_NS = "{http://www.mdsol.com/ns/odm/metadata}"
ODM_NS = "{http://www.cdisc.org/ns/odm/v1.3}"
XLINK_NS = "{http://www.w3.org/1999/xlink}"


def getEnvironmentFromNameAndProtocol(studyname, protocolname):
    """
    Extract environment name using studyname and protocolname to guide
    :param str studyname: Name of the study (including Env)
    :param str protocolname: Name of the study
    """
    # StudyName =    "TEST (1) (DEV)"
    # ProtocolName = "TEST (1)"
    # Raw Env      =           "(DEV)"

    raw_env = studyname[len(protocolname) :].strip()

    if "(" in raw_env:
        l_brace_pos = raw_env.rfind("(")
        r_brace_pos = raw_env.rfind(")")
        return raw_env[l_brace_pos + 1 : r_brace_pos]
    else:
        return raw_env


def parseXMLString(xml):
    """
    Parse XML string, return root
    :param str: Passed in XML
    """

    # Remove BOM if it exists (different requests seem to have different BOMs)
    unichr_captured = ""

    if not xml.strip():
        return u""

    while xml[0] != u"<":
        unichr_captured += xml[0]
        xml = xml[1:]
    parser = etree.XMLParser(ns_clean=True, collect_ids=False, huge_tree=True)
    try:
        return etree.fromstring(xml.encode("utf-8"), parser=parser)
    except etree.XMLSyntaxError:
        raise Exception(xml)


class RWSException(Exception):
    """RWS Exception. Usual to attach the error response object"""

    def __init__(self, msg, rws_error):
        """
        :param str msg: Error message (base)
        :param str rws_error: RWS error message
        """
        Exception.__init__(self, msg)
        self.rws_error = rws_error


class XMLRepr(object):
    """Classes that represent objects passed back from RWS as XML"""

    def __init__(self, xml):
        """
        :param str xml: XML returned from RWS
        """
        self.root = parseXMLString(xml)

    def __unicode__(self):
        """String representation of same"""
        return etree.tostring(self.root, encoding="utf-8")

    def __str__(self):
        """String representation of same"""
        return etree.tostring(self.root, encoding="utf-8").decode("utf-8")


class ODMDoc(XMLRepr):
    """A base ODM document"""

    def __init__(self, xml):
        """
        Abstract Doc Class
        :param bytes xml: Input content
        """
        # Call base class
        XMLRepr.__init__(self, xml)
        r_get = self.root.get

        self.filetype = r_get("FileType")
        self.creationdatetime = r_get("CreationDateTime")
        self.fileoid = r_get("FileOID")
        self.ODMVersion = r_get("ODMVersion")
        self.granularity = r_get("Granularity", None)


class RWSError(ODMDoc):
    """
    Extends ODMDoc, inheriting attributes like filetype, creationdatetime etc.

    Parses XML of the form:

    .. code-block:: xml

        <?xml version="1.0" encoding="utf-8"?>
        <ODM xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata"
             FileType="Snapshot"
             CreationDateTime="2013-04-08T10:28:49.578-00:00"
             FileOID="4d13722a-ceb6-4419-a917-b6ad5d0bc30e"
             ODMVersion="1.3"
             mdsol:ErrorDescription="Incorrect login and password combination. [RWS00008]"
             xmlns="http://www.cdisc.org/ns/odm/v1.3" />
    """

    def __init__(self, xml):
        ODMDoc.__init__(self, xml)
        r_get = self.root.get
        self.errordescription = r_get(MEDI_NS + "ErrorDescription")


class RWSErrorResponse(XMLRepr):
    """
    Parses messages of the form:

    .. code-block:: xml

        <Response
            ReferenceNumber="0b47fe86-542f-4070-9e7d-16396a5ef08a"
            InboundODMFileOID="Not Supplied"
            IsTransactionSuccessful="0"
            ReasonCode="RWS00092"
            ErrorClientResponseMessage="CRF version not found">
        </Response>
    """

    def __init__(self, xml):
        # Call base class
        XMLRepr.__init__(self, xml)
        r_get = self.root.get

        self.referencenumber = r_get("ReferenceNumber")
        self.inboundodmfileoid = r_get("InboundODMFileOID")
        self.istransactionsuccessful = r_get("IsTransactionSuccessful") == "1"
        self.reasoncode = r_get("ReasonCode")
        self.errordescription = r_get("ErrorClientResponseMessage")


class RWSResponse(XMLRepr):
    """
    Parses messages of the form:

    .. code-block:: xml

        <Response ReferenceNumber="82e942b0-48e8-4cf4-b299-51e2b6a89a1b"
            InboundODMFileOID=""
            IsTransactionSuccessful="1"
            SuccessStatistics="Rave objects touched: Subjects=0; Folders=0; Forms=0; Fields=0; LogLines=0" NewRecords="">
        </Response>
    """

    def __init__(self, xml):
        # Call base class
        XMLRepr.__init__(self, xml)
        r_get = self.root.get

        self.referencenumber = r_get("ReferenceNumber")
        self.inboundodmfileoid = r_get("InboundODMFileOID")
        self.istransactionsuccessful = r_get("IsTransactionSuccessful") == "1"

        self.subjects_touched = 0
        self.folders_touched = 0
        self.forms_touched = 0
        self.fields_touched = 0
        self.loglines_touched = 0

        success_stats = r_get("SuccessStatistics", "")

        # Clinical data post
        if success_stats.startswith("Rave objects touched:"):
            success_stats = success_stats[
                len("Rave objects touched:") + 1 :
            ]  # Subjects=0; Folders=0; Forms=0; Fields=0; LogLines=0
            parts = success_stats.split(
                ";"
            )  # [Subjects=0, Folders=0, Forms=0, Fields=0, LogLines=0]
            for part in parts:
                name, value = part.strip().split("=")
                # if value[-1] == ';':
                #     value = value[:-1]
                if name == "Subjects":
                    self.subjects_touched = int(value)
                elif name == "Folders":
                    self.folders_touched = int(value)
                elif name == "Forms":
                    self.forms_touched = int(value)
                elif name == "Fields":
                    self.fields_touched = int(value)
                elif name == "LogLines":
                    self.loglines_touched = int(value)
                else:
                    raise KeyError(
                        "Unknown Rave Object %s in response %s" % (name, success_stats)
                    )

        # Note: Metadata post has success_stats == 'N/A'
        self.new_records = r_get("NewRecords")


class RWSPostResponse(RWSResponse):
    """
    Parses responses from PostODMClinicalData messages with the format:

    .. code-block:: xml

        <Response ReferenceNumber="82e942b0-48e8-4cf4-b299-51e2b6a89a1b"
                  InboundODMFileOID=""
                  IsTransactionSuccessful="1"
                  SuccessStatistics="Rave objects touched: Subjects=0; Folders=0; Forms=0; Fields=0; LogLines=0" NewRecords=""
                  SubjectNumberInStudy="1103" SubjectNumberInStudySite="55">
        </Response>
    """

    def __init__(self, xml):
        # Call base class
        RWSResponse.__init__(self, xml)
        r_get = self.root.get
        # These counts may only come as a result of a Clinical data POST
        snis = r_get("SubjectNumberInStudy")
        self.subjects_in_study = int(snis) if snis is not None else None

        sniss = r_get("SubjectNumberInStudySite")
        self.subjects_in_study_site = int(sniss) if sniss is not None else None

        # DraftImported only comes from a MetaData Post
        # In which case successStatistics will be SuccessStatistics="N/A"
        self.draft_imported = r_get("DraftImported")


class RWSPostErrorResponse(RWSResponse):
    """
    Responses to Clinical data post messages have additional Attributes to normal RWS Response messages:

    .. code-block:: xml

        <Response
            ReferenceNumber="5b1fa9a3-0cf3-46b6-8304-37c2e3b7d04f"
            InboundODMFileOID="1"
            IsTransactionSuccessful = "0"
            ReasonCode="RWS00024"
            ErrorOriginLocation="/ODM/ClinicalData[1]/SubjectData[1]"
            SuccessStatistics="Rave objects touched: Subjects=0; Folders=0; Forms=0; Fields=0; LogLines=0"
            ErrorClientResponseMessage="Subject already exists.">
        </Response>

    """

    def __init__(self, xml):
        """
        :param str xml: Error response
        """
        RWSResponse.__init__(self, xml)

        # Get additional properties
        r_get = self.root.get
        self.reason_code = r_get("ReasonCode")
        self.error_origin_location = r_get("ErrorOriginLocation")
        self.error_client_response_message = r_get("ErrorClientResponseMessage")


class RWSStudyListItem(object):
    """An item in the RWS Study List response"""

    def __init__(
        self,
        oid=None,
        studyname=None,
        protocolname=None,
        environment=None,
        projecttype=None,
    ):
        """
        :param str oid: Study OID
        :param str studyname: Study Name
        :param str protocolname: Protocol Name
        :param str environment: Study Environment
        :param str projecttype: Project Type
        """
        self.oid = oid
        self.studyname = studyname
        self.protocolname = protocolname
        self.environment = environment
        self.projecttype = projecttype

    def isProd(self):
        """
        Is production if environment is empty

        :rtype: bool
        """
        return self.environment == "" and self.projecttype != "GlobalLibraryVolume"

    @classmethod
    def fromElement(cls, elem):
        """
        Read properties from an XML Element to build a StudyList Item

        :param lxml.etree.Element elem: The source Study XML Element

        .. code-block:: xml

            <Study OID="Fixitol(Dev)" mdsol:ProjectType="GlobalLibraryVolume">
                <GlobalVariables>
                    <StudyName>Fixitol (Dev)</StudyName>
                    <StudyDescription/>
                    <ProtocolName>Fixitol</ProtocolName>
                </GlobalVariables>
            </Study>

        """
        e_global_variables = elem.find(ODM_NS + "GlobalVariables")
        studyname = e_global_variables.find(ODM_NS + "StudyName").text
        protocolname = e_global_variables.find(ODM_NS + "ProtocolName").text
        self = cls(
            oid=elem.get("OID"),
            projecttype=elem.get(MEDI_NS + "ProjectType", "Project"),
            studyname=studyname,
            protocolname=protocolname,
            environment=getEnvironmentFromNameAndProtocol(studyname, protocolname),
        )

        return self


# I hate multi-inheritance generally but since this is inheriting from a built-in like list I feel
# less bad about it.
class RWSStudies(list, ODMDoc):
    """
    Represents a list of studies. Extends the list class and adds a couple of extra properties:

    .. code-block:: xml

        <ODM FileType="Snapshot" FileOID="767a1f8b-7b72-4d12-adbe-37d4d62ba75e"
             CreationDateTime="2013-04-08T10:02:17.781-00:00"
             ODMVersion="1.3"
             xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata"
             xmlns:xlink="http://www.w3.org/1999/xlink"
             xmlns="http://www.cdisc.org/ns/odm/v1.3">
             <Study OID="Fixitol(Dev)">
                <GlobalVariables>
                      <StudyName>Fixitol (Dev)</StudyName>
                      <StudyDescription/>
                      <ProtocolName>Fixitol</ProtocolName>
                </GlobalVariables>
             </Study>
             <Study OID="IANTEST(Prod)">
                <GlobalVariables>
                      <StudyName>IANTEST</StudyName>
                      <StudyDescription/>
                      <ProtocolName>IANTEST</ProtocolName>
                </GlobalVariables>
             </Study>
        </ODM>
    """

    def __init__(self, xml):
        # Get basic properties
        ODMDoc.__init__(self, xml)

        for estudy in self.root.findall(ODM_NS + "Study"):
            self.append(RWSStudyListItem.fromElement(estudy))


class MetaDataVersion(object):
    """
    A single MetaDataVersion instance

    .. code-block:: xml

        <MetaDataVersion OID="1203" Name="Webservice Outbound"/>
    """

    def __init__(self):
        self.oid = None
        self.name = None

    @classmethod
    def fromElement(cls, elem):
        """
        Read properties from a MetaDataVersion element

        :param lxml.etree._Element elem: Source etree Element
        """

        self = cls()

        self.oid = elem.get("OID")
        self.name = elem.get("Name")
        return self


class RWSStudyMetadataVersions(list, ODMDoc, RWSStudyListItem):
    """
    Parses responses from MetaDataVersions request:

    .. code-block:: xml

        <ODM ODMVersion="1.3" Granularity="Metadata" FileType="Snapshot" FileOID="d26b4d33-376d-4037-9747-684411190179" CreationDateTime=" 2013-04-08T01:29:13 " xmlns="http://www.cdisc.org/ns/odm/v1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata">
            <Study OID="IANTEST">
                <GlobalVariables>
                    <StudyName>IANTEST</StudyName>
                    <StudyDescription></StudyDescription>
                    <ProtocolName>IANTEST</ProtocolName>
                </GlobalVariables>
                <MetaDataVersion OID="1203" Name="Webservice Outbound" />
                <MetaDataVersion OID="1195" Name="JC_Demo_Draft1" />
                <MetaDataVersion OID="1165" Name="Initial" />
            </Study>
        </ODM>
    """

    def __init__(self, xml):
        # Get basic properties
        ODMDoc.__init__(self, xml)

        root = self.root  # type: lxml.etree._Element

        e_study = root.find(ODM_NS + "Study")  # type: lxml.etree._Element

        # Quick way to grab the elements here, nasty though
        self.study = RWSStudyListItem.fromElement(e_study)

        for e_version in e_study.findall(ODM_NS + "MetaDataVersion"):
            self.append(MetaDataVersion.fromElement(e_version))


class RWSSubjectListItem(object):
    """
    Parses response of Subject List request:

    .. code-block:: xml

        <ClinicalData StudyOID="Fixitol(Dev)" MetaDataVersionOID="1111">
         <SubjectData SubjectKey="1111">
            <SiteRef LocationOID="335566"/>
         </SubjectData>
        </ClinicalData>

    Optionally ClinicalData may include status:

    .. code-block:: xml

        <SubjectData SubjectKey="1111" mdsol:Overdue="No"
                  mdsol:Touched="Yes"
                  mdsol:Empty="No"
                  mdsol:Incomplete="No"
                  mdsol:NonConformant="No"
                  mdsol:RequiresSecondPass="No"
                  mdsol:RequiresReconciliation="No"
                  mdsol:RequiresVerification="No"
                  mdsol:Verified="No"
                  mdsol:Frozen="No"
                  mdsol:Locked="No"
                  mdsol:RequiresReview="No"
                  mdsol:PendingReview="No"
                  mdsol:Reviewed="No"
                  mdsol:RequiresAnswerQuery="No"
                  mdsol:RequiresPendingCloseQuery="No"
                  mdsol:RequiresCloseQuery="No"
                  mdsol:StickyPlaced="No"
                  mdsol:Signed="No"
                  mdsol:SignatureCurrent="No"
                  mdsol:RequiresTranslation="No"
                  mdsol:RequiresCoding="No"
                  mdsol:RequiresPendingAnswerQuery="No"
                  mdsol:RequiresSignature="No"
                  mdsol:ReadyForFreeze="No"
                  mdsol:ReadyForLock="Yes">

    The SubjectKey can be either a Subject ID or a UUID depending on the value of SubjectKeyType:

    .. code-block:: xml

        <ClinicalData StudyOID="Fixitol(Dev)" MetaDataVersionOID="1111">
         <SubjectData SubjectKey="EC82F1AB-D463-4930-841D-36FC865E63B2" mdsol:SubjectName="1" mdsol:SubjectKeyType="SubjectUUID">
            <SiteRef LocationOID="335566"/>
         </SubjectData>
        </ClinicalData>

    The Response may include links:

    .. code-block:: xml

        <ClinicalData StudyOID="Fixitol(Dev)" MetaDataVersionOID="1111">
         <SubjectData SubjectKey="1111">
            <SiteRef LocationOID="335566"/>
            <mdsol:Link xlink:type="simple" xlink:href="http://innovate.mdsol.com/MedidataRAVE/HandleLink.aspx?page=SubjectPage.aspx?ID=849" />
         </SubjectData>
        </ClinicalData>

    """

    STATUS_PROPERTIES = [
        "Overdue",
        "Touched",
        "Empty",
        "Incomplete",
        "NonConformant",
        "RequiresSecondPass",
        "RequiresReconciliation",
        "RequiresVerification",
        "Verified",
        "Frozen",
        "Locked",
        "RequiresReview",
        "PendingReview",
        "Reviewed",
        "RequiresAnswerQuery",
        "RequiresPendingCloseQuery",
        "RequiresCloseQuery",
        "StickyPlaced",
        "Signed",
        "SignatureCurrent",
        "RequiresTranslation",
        "RequiresCoding",
        "RequiresPendingAnswerQuery",
        "RequiresSignature",
        "ReadyForFreeze",
        "ReadyForLock",
        "SubjectKeyType",
        "SubjectName",
    ]

    def __init__(self):
        """The ODM message has a ClinicalData element with a single SubjectData and SiteRef elements
           nested within. I collapse into a single object
        """
        self.studyoid = None
        self.metadataversionoid = None
        self.subjectkey = None
        self.subjectkeytype = None
        self.locationoid = None

        self.active = None  # SubjectActive
        self.deleted = None  # Deleted
        self.links = []  # Link if requested

        # Optional properties, only if status included
        for prop in RWSSubjectListItem.STATUS_PROPERTIES:
            setattr(self, prop.lower(), None)

    @property
    def subject_name(self):
        """
        Get the subject name consistently
        :rtype str
        :return: The Subject ID for the subject

        .. note::
          * If the `SubjectKeyType` is `SubjectUUID` then the subject name lives in the `mdsol:SubjectName` attribute
          * If the `SubjectKeyType` is `SubjectName` then the subject name lives in the `SubjectKey` attribute
        """
        if self.subjectkeytype and self.subjectkeytype == "SubjectUUID".lower():
            # if the SubjectKeyType is "SubjectUUID", then return the SubjectName
            return self.subjectname
        else:
            return self.subjectkey

    @classmethod
    def fromElement(cls, elem):
        """
        Read properties from an XML Element
        """
        self = cls()
        self.studyoid = elem.get("StudyOID")
        self.metadataversionoid = elem.get("MetaDataVersionOID")
        e_subjectdata = elem.findall(ODM_NS + "SubjectData")[0]
        self.subjectkey = e_subjectdata.get("SubjectKey")
        e_siteref = e_subjectdata.findall(ODM_NS + "SiteRef")[0]
        self.locationoid = e_siteref.get("LocationOID")

        e_links = e_subjectdata.findall(MEDI_NS + "Link")
        for e_link in e_links:
            self.links.append(e_link.get(XLINK_NS + "href"))

        decodes = {"yes": True, "no": False, "": None}
        for prop in RWSSubjectListItem.STATUS_PROPERTIES:
            val = e_subjectdata.get(MEDI_NS + prop, "").lower()
            setattr(self, prop.lower(), decodes.get(val, val))

        # By default we only get back active and non-deleted subjects
        self.active = decodes[
            e_subjectdata.get(MEDI_NS + "SubjectActive", "yes").lower()
        ]
        self.deleted = decodes[e_subjectdata.get(MEDI_NS + "Deleted", "no").lower()]

        return self


class RWSSubjects(list, ODMDoc):
    """
    Represents a list of subjects:

    .. code-block:: xml

        <ODM FileType="Snapshot"
             FileOID="770f1758-db33-4ab2-af72-38db863734aa"
             CreationDateTime="2013-04-08T14:08:06.875-00:00"
             ODMVersion="1.3">

             <ClinicalData StudyOID="Fixitol(Dev)" MetaDataVersionOID="1111">
                <SubjectData SubjectKey="000001">
                   <SiteRef LocationOID="BP001"/>
                   <mdsol:Link xlink:type="simple" xlink:href="http://innovate.mdsol.com/MedidataRAVE/HandleLink.aspx?page=SubjectPage.aspx?ID=849" />
                </SubjectData>
             </ClinicalData>

             <ClinicalData StudyOID="Fixitol(Dev)" MetaDataVersionOID="1111">
                 <SubjectData SubjectKey="1111">
                    <SiteRef LocationOID="335566"/>
                    <mdsol:Link xlink:type="simple" xlink:href="http://innovate.mdsol.com/MedidataRAVE/HandleLink.aspx?page=SubjectPage.aspx?ID=849" />
                 </SubjectData>
             </ClinicalData>
        </ODM>

    """

    def __init__(self, xml):
        # Get basic properties
        ODMDoc.__init__(self, xml)

        root = self.root  # from ODMDoc

        for e_clindata in root.findall(ODM_NS + "ClinicalData"):
            self.append(RWSSubjectListItem.fromElement(e_clindata))
