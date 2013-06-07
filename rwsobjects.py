__author__ = 'isparks'

from lxml import etree

MEDI_NS = '{http://www.mdsol.com/ns/odm/metadata}'
ODM_NS = '{http://www.cdisc.org/ns/odm/v1.3}'


def getEnvironmentFromNameAndProtocol(studyname, protocolname):
    """Extract environment name using studyname and protocolname to guide"""
    #StudyName =    "TEST (1) (DEV)"
    #ProtocolName = "TEST (1)"
    #Raw Env      =           "(DEV)"

    raw_env = studyname[len(protocolname):].strip()

    if '(' in raw_env:
        l_brace_pos = raw_env.rfind('(')
        r_brace_pos = raw_env.rfind(')')
        return raw_env[l_brace_pos+1:r_brace_pos]
    else:
        return raw_env

def parseXMLString(xml):
    """Parse XML string, return root"""

    #Remove BOM if it exists (different requests seem to have different BOMs)
    unichr_captured = ''
    while xml[0] != u'<':
        unichr_captured += xml[0]
        xml = xml[1:]

    try:
        return etree.fromstring(xml.encode('utf-8'))
    except etree.XMLSyntaxError, e:
        print e.message
        print "XML WAS"
        print xml

def xpath(doc, path_elements):
    """Handle the evil plumbing of xpath elements for lxml / etree"""
    ns = {"odm": ODM_NS[1:-1],
          "mdsol": MEDI_NS[1:-1]}

    return doc.xpath('/'.join(["%s:%s" % (prefix, element,) for prefix, element in path_elements ]), namespaces=ns)


class RWSException(Exception):
    """RWS Exception. Usual to attach the error response object"""
    def __init__(self, msg, rws_error):
        Exception.__init__(self, msg)
        self.rws_error = rws_error

class XMLRepr(object):
    """Classes that represent objects passed back from RWS as XML"""
    def __init__(self, xml):
        self.root = parseXMLString(xml)


class ODMDoc(XMLRepr):
    """All ODM responses have the same wrapper"""
    def __init__(self, xml):
        #Call base class
        XMLRepr.__init__(self, xml)
        r_get = self.root.get

        self.filetype = r_get('FileType')
        self.creationdatetime = r_get('CreationDateTime')
        self.fileoid = r_get("FileOID")
        self.ODMVersion = r_get("ODMVersion")
        self.granularity = r_get("Granularity",None)



class RWSError(ODMDoc):
    """
    Extends ODMDoc, inheriting attributes like filetype, creationdatetime etc.

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
 <Response
    ReferenceNumber="0b47fe86-542f-4070-9e7d-16396a5ef08a"
    InboundODMFileOID="Not Supplied"
    IsTransactionSuccessful="0"
    ReasonCode="RWS00092"
    ErrorClientResponseMessage="CRF version not found">
    </Response>
    """
    def __init__(self, xml):
        #Call base class
        XMLRepr.__init__(self, xml)
        r_get = self.root.get

        self.referencenumber = r_get("ReferenceNumber")
        self.inboundodmfileoid = r_get('InboundODMFileOID')
        self.istransactionsuccessful = r_get('IsTransactionSuccessful') == "1"
        self.reasoncode = r_get("ReasonCode")
        self.errordescription = r_get("ErrorClientResponseMessage")



class RWSStudyListItem(object):
    """A item in the RWS Study List response"""
    def __init__(self):
        self.oid = None
        self.studyname = None
        self.protocolname = None
        self.environment = None
        self.projecttype = None


    def isProd(self):
        """Is production if environment is empty"""
        return self.environment == '' and self.projecttype != 'GlobalLibraryVolume'

    @classmethod
    def fromElement(cls, elem):
        """Read properties from an XML Element

         <Study OID="Fixitol(Dev) mdsol:ProjectType="GlobalLibraryVolume">
            <GlobalVariables>
                  <StudyName>Fixitol (Dev)</StudyName>
                  <StudyDescription/>
                  <ProtocolName>Fixitol</ProtocolName>
            </GlobalVariables>
         </Study>
        """

        self = cls()

        self.oid = elem.get('OID')

        #Not all returned documents have a projecttype (GlobalLibraryVolumes do)
        self.projecttype =  elem.get(MEDI_NS + "ProjectType")

        e_global_variables = elem.find(ODM_NS + 'GlobalVariables')
        self.studyname = e_global_variables.find(ODM_NS + 'StudyName').text
        self.protocolname = e_global_variables.find(ODM_NS + 'ProtocolName').text



        self.environment = getEnvironmentFromNameAndProtocol(self.studyname, self.protocolname)

        return self




class RWSStudies(list, ODMDoc): #I hate multi-inheritance generally.
    """
    Represents a list of studies. Extends the list class and adds a couple of extra properties.

    <ODM FileType="Snapshot" FileOID="767a1f8b-7b72-4d12-adbe-37d4d62ba75e"
         CreationDateTime="2013-04-08T10:02:17.781-00:00"
         ODMVersion="1.3">
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
        #Get basic properties
        ODMDoc.__init__(self, xml)

        for estudy in self.root.findall(ODM_NS + 'Study'):
            self.append(RWSStudyListItem.fromElement(estudy))


class MetaDataVersion(object):
    """
    <MetaDataVersion OID="1203" Name="Webservice Outbound"/>
    """
    def __init__(self):
        self.oid = None
        self.name = None

    @classmethod
    def fromElement(cls, elem):
        """Read properties from an XML Element

           <MetaDataVersion OID="1203" Name="Webservice Outbound"/>
        """

        self = cls()

        self.oid = elem.get('OID')
        self.name = elem.get('Name')
        return self



class RWSStudyMetadataVersions(list, ODMDoc, RWSStudyListItem):
    """
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
        #Get basic properties
        ODMDoc.__init__(self, xml)

        root = self.root #from ODMDoc

        e_study = root.find(ODM_NS + 'Study')

        #Quick way to grab the elements here, nasty though
        self.study = RWSStudyListItem.fromElement(e_study)


        for e_version in e_study.findall(ODM_NS + 'MetaDataVersion'):
            self.append(MetaDataVersion.fromElement(e_version))


class RWSSubjectListItem(object):
    """
         <ClinicalData StudyOID="Fixitol(Dev)" MetaDataVersionOID="1111">
             <SubjectData SubjectKey="1111">
                <SiteRef LocationOID="335566"/>
             </SubjectData>
         </ClinicalData>
    """
    def __init__(self):
        """The ODM message has a ClinicalData element with a single SubjectData and SiteRef elements
           nested within. I collapse into a single object
        """
        self.studyoid = None
        self.metadataversionoid = None
        self.subjectkey = None
        self.locationoid = None

    @classmethod
    def fromElement(cls, elem):
        """
        Read properties from an XML Element
        """
        self = cls()
        self.studyoid = elem.get('StudyOID')
        self.metadataversionoid = elem.get('MetaDataVersionOID')
        e_subjectdata = elem.findall(ODM_NS + 'SubjectData')[0]
        self.subjectkey = e_subjectdata.get('SubjectKey')
        e_siteref = e_subjectdata.findall(ODM_NS + 'SiteRef')[0]
        self.locationoid = e_siteref.get('LocationOID')
        return self


class RWSSubjects(list, ODMDoc): #I hate multi-inheritance generally.
    """
    Represents a list of subjects

    <ODM FileType="Snapshot"
         FileOID="770f1758-db33-4ab2-af72-38db863734aa"
         CreationDateTime="2013-04-08T14:08:06.875-00:00"
         ODMVersion="1.3">

         <ClinicalData StudyOID="Fixitol(Dev)" MetaDataVersionOID="1111">
            <SubjectData SubjectKey="000001">
               <SiteRef LocationOID="BP001"/>
            </SubjectData>
         </ClinicalData>

         <ClinicalData StudyOID="Fixitol(Dev)" MetaDataVersionOID="1111">
             <SubjectData SubjectKey="1111">
                <SiteRef LocationOID="335566"/>
             </SubjectData>
         </ClinicalData>
    </ODM>
    """

    def __init__(self, xml):
        #Get basic properties
        ODMDoc.__init__(self, xml)

        root = self.root #from ODMDoc

        for e_clindata in root.findall(ODM_NS + 'ClinicalData'):
            self.append(RWSSubjectListItem.fromElement(e_clindata))


