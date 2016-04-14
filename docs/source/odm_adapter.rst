.. _odm_adapter:

ODM Adapter Requests
********************

The ODM Adapter module provides Request implementations for the Rave Web Service ODM Adapter URLs. These include:

* Clinical Audit Records Dataset
* Version Folders Dataset
* Sites Dataset
* Users Dataset
* Signature Definitions Dataset

Read more about ODM Adapter in the
`Rave Web Services documentation <http://rws-webhelp.s3.amazonaws.com/WebHelp_ENG/solutions/clinical_data_audits/index.html#odm-adapter>`_


.. _oa_auditrecords_request:
.. index:: AuditRecordsRequest

AuditRecordsRequest(project_name, environment_name)
---------------------------------------------------

Authorization is required for this request.

Returns audit data in ODM format. Since the audit trail is a large table which cannot be downloaded in a single request,
this dataset returns headers that tell you what the next page of data to request is. This allows you to make further
requests until all data from the dataset has been received.

Calls::

    https://{{ host }}/RaveWebServices/datasets/ClinicalAuditRecords.odm/?studyoid={project_name}({environment_name})&startid={startid}&per_page={per_page}

Options:

+--------------------------------+-----------------------------------------------------------------------------------+
| Option                         | Description                                                                       |
+================================+===================================================================================+
| startid=1                      | The audit ID to start on. Defaults to 1. The first Audit ID                       |
+--------------------------------+-----------------------------------------------------------------------------------+
| per_page=100                   | How many audits to return per request. Default is 100.                            |
+--------------------------------+-----------------------------------------------------------------------------------+

Example::

    >>> from rwslib import RWSConnection
    >>> from rwslib.rws_requests.odm_adapter import *
    >>> r = RWSConnection('https://innovate.mdsol.com', 'username', 'password')
    >>> audits = r.send_request(AuditRecordsRequest('MEDIFLEX','DEV'))
    >>> r.last_request.headers
    {.....'Link': '<https://innovate.mdsol.com/RaveWebServices/datasets/ClinicalAuditRecords.odm?studyoid=MEDIFLEX%28DEV%29&startid=3842&per_page=1000>; rel="next"',...., 'Content-Type': 'text/xml'}

Note that the audit_event example in the extras package of rwslib provides a parser for the content of audit records and
a class to simplify the consumption of this web service. See the README for that project in the extras/audit_event
package.


.. _oa_versionfolders_request:
.. index:: VersionFoldersRequest

VersionFoldersRequest(project_name, environment_name)
-----------------------------------------------------

Authorization is required for this request.

Returns a dataset in ODM format which represents the folders in-use. This is useful because the standard ODM Metadata
can only return the primary Matrix (folder structure) of Rave. VersionFoldersRequest provides all possible folders.

Calls::

    https://{{ host }}/RaveWebServices/datasets/VersionFolders.odm/?studyoid={project_name}({environment_name})


Example::

    >>> from rwslib import RWSConnection
    >>> from rwslib.rws_requests.odm_adapter import *
    >>> r = RWSConnection('https://innovate.mdsol.com', 'username', 'password')
    >>> r.send_request(VersionFoldersRequest('MEDIFLEX','DEV'))
    <?xml version="1.0" encoding="UTF-8"?>
    <ODM xmlns="http://www.cdisc.org/ns/odm/v1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata" ODMVersion="1.3" Granularity="Metadata" FileType="Snapshot" FileOID="2f4f7fdf-f5db-4150-bf41-79060d4b5ffb" CreationDateTime="2016-04-13T13:53:04.000-00:00">
       <Study OID="Mediflex(Dev)">
          <GlobalVariables>
             <StudyName>Mediflex(Dev)</StudyName>
             <StudyDescription />
             <ProtocolName>Mediflex</ProtocolName>
          </GlobalVariables>
          <MetaDataVersion OID="16" Name="1" mdsol:PrimaryFormOID="EN">
             <Protocol>
                <StudyEventRef StudyEventOID="YEAR1" OrderNumber="7" Mandatory="No" mdsol:StudyEventDefName="Year 01" mdsol:StudyEventDefType="Common" mdsol:StudyEventDefRepeating="No" />
             </Protocol>
          </MetaDataVersion>
          <MetaDataVersion OID="16" Name="1" mdsol:MatrixOID="ADDCYCLE" mdsol:PrimaryFormOID="EN">
             <Protocol>
                <StudyEventRef StudyEventOID="ADDCYCLE" OrderNumber="11" Mandatory="No" mdsol:StudyEventDefName="Additional Cycle" mdsol:StudyEventDefType="Common" mdsol:StudyEventDefRepeating="No" />
             </Protocol>
          </MetaDataVersion>
          <MetaDataVersion OID="16" Name="1" mdsol:DefaultMatrixOID="BASE" mdsol:PrimaryFormOID="EN">
             <Protocol>
                <StudyEventRef StudyEventOID="SCREEN" OrderNumber="1" Mandatory="No" mdsol:StudyEventDefName="Screening" mdsol:StudyEventDefType="Common" mdsol:StudyEventDefRepeating="No" />
                <StudyEventRef StudyEventOID="VISIT01" OrderNumber="2" Mandatory="No" mdsol:StudyEventDefName="Visit 01" mdsol:StudyEventDefType="Common" mdsol:StudyEventDefRepeating="No" />
                <StudyEventRef StudyEventOID="VISIT02" OrderNumber="3" Mandatory="No" mdsol:StudyEventDefName="Visit 02" mdsol:StudyEventDefType="Common" mdsol:StudyEventDefRepeating="No" />
                <StudyEventRef StudyEventOID="VISIT03" OrderNumber="4" Mandatory="No" mdsol:StudyEventDefName="Visit 03" mdsol:StudyEventDefType="Common" mdsol:StudyEventDefRepeating="No" />
                <StudyEventRef StudyEventOID="VISIT04" OrderNumber="5" Mandatory="No" mdsol:StudyEventDefName="Visit 04" mdsol:StudyEventDefType="Common" mdsol:StudyEventDefRepeating="No" />
                <StudyEventRef StudyEventOID="CYCLE1" OrderNumber="8" Mandatory="No" mdsol:StudyEventDefName="Cycle 01" mdsol:StudyEventDefType="Common" mdsol:StudyEventDefRepeating="No" />
                <StudyEventRef StudyEventOID="CYCLE2" OrderNumber="9" Mandatory="No" mdsol:StudyEventDefName="Cycle 02" mdsol:StudyEventDefType="Common" mdsol:StudyEventDefRepeating="No" />
             </Protocol>
          </MetaDataVersion>
          <MetaDataVersion OID="16" Name="1" mdsol:MatrixOID="EXTCYCLE" mdsol:PrimaryFormOID="EN">
             <Protocol>
                <StudyEventRef StudyEventOID="EXTCYCLE" OrderNumber="10" Mandatory="No" mdsol:StudyEventDefName="Extended Cycle" mdsol:StudyEventDefType="Common" mdsol:StudyEventDefRepeating="No" />
             </Protocol>
          </MetaDataVersion>
          <MetaDataVersion OID="16" Name="1" mdsol:MatrixOID="UNSCHEDULED" mdsol:PrimaryFormOID="EN">
             <Protocol>
                <StudyEventRef StudyEventOID="UNSCHEDULED" OrderNumber="6" Mandatory="No" mdsol:StudyEventDefName="Visit" mdsol:StudyEventDefType="Common" mdsol:StudyEventDefRepeating="No" />
             </Protocol>
          </MetaDataVersion>
          <MetaDataVersion OID="16" Name="1" mdsol:MatrixOID="VISITS" mdsol:PrimaryFormOID="EN">
             <Protocol>
                <StudyEventRef StudyEventOID="VISIT01" OrderNumber="2" Mandatory="No" mdsol:StudyEventDefName="Visit 01" mdsol:StudyEventDefType="Common" mdsol:StudyEventDefRepeating="No" />
                mdsol:MatrixOID="VISITS"
                <StudyEventRef StudyEventOID="VISIT02" OrderNumber="3" Mandatory="No" mdsol:StudyEventDefName="Visit 02" mdsol:StudyEventDefType="Common" mdsol:StudyEventDefRepeating="No" />
                mdsol:MatrixOID="VISITS"
                <StudyEventRef StudyEventOID="VISIT03" OrderNumber="4" Mandatory="No" mdsol:StudyEventDefName="Visit 03" mdsol:StudyEventDefType="Common" mdsol:StudyEventDefRepeating="No" />
             </Protocol>
          </MetaDataVersion>
          <MetaDataVersion OID="23" Name="2" mdsol:PrimaryFormOID="EN">
             <Protocol>
                <StudyEventRef StudyEventOID="YEAR1" OrderNumber="7" Mandatory="No" mdsol:StudyEventDefName="Year 01" mdsol:StudyEventDefType="Common" mdsol:StudyEventDefRepeating="No" />
             </Protocol>
          </MetaDataVersion>
          <MetaDataVersion OID="23" Name="2" mdsol:MatrixOID="ADDCYCLE" mdsol:PrimaryFormOID="EN">
             <Protocol>
                <StudyEventRef StudyEventOID="ADDCYCLE" OrderNumber="11" Mandatory="No" mdsol:StudyEventDefName="Additional Cycle" mdsol:StudyEventDefType="Common" mdsol:StudyEventDefRepeating="No" />
             </Protocol>
          </MetaDataVersion>
          ....
       </Study>
    </ODM>



.. _oa_sites_metadata_request:
.. index:: SitesMetadataRequest

SitesMetadataRequest()
----------------------

Authorization is required for this request.

Returns an ODM AdminData document which lists all sites along with their metadata versions and effective dates.
Optionally can take a project name and an environment to filter the list only to that study/environment.

To find the current active metadata version for a study/site you will need to sort the metadata versions for the site
by the effective date and take the latest one.

Calls::

    https://{{ host }}/RaveWebServices/datasets/Sites.odm/[?studyoid={project_name}({environment_name})]


Options:

+--------------------------------+-----------------------------------------------------------------------------------+
| Option                         | Description                                                                       |
+================================+===================================================================================+
| project_name={projectname}     | Project to filter the result set to (recommended)                                 |
+--------------------------------+-----------------------------------------------------------------------------------+
| environment_name={environment} | Environment to filter the result set to                                           |
+--------------------------------+-----------------------------------------------------------------------------------+

If used, the project_name and environmen_namet must both be supplied or an error will result.

Example::

    >>> from rwslib import RWSConnection
    >>> from rwslib.rws_requests.odm_adapter import *
    >>> r = RWSConnection('https://innovate.mdsol.com', 'username', 'password')
    >>> r.send_request(SitesMetadataRequest('Mediflex','DEV'))
    <?xml version="1.0" encoding="UTF-8"?>
    <ODM xmlns="http://www.cdisc.org/ns/odm/v1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata" ODMVersion="1.3" FileType="Snapshot" FileOID="b4e9560d-0e67-4788-aa04-9b9dfe5d740b" CreationDateTime="2016-04-13T13:59:25">
       <AdminData>
          <Location OID="4567" Name="Uxbridge Medical Centre" LocationType="Site" mdsol:Active="Yes">
             <MetaDataVersionRef StudyOID="Mediflex(Dev)" MetaDataVersionOID="23" EffectiveDate="2009-04-20" mdsol:StudySiteNumber="" />
          </Location>
          <Location OID="MEDI0001" Name="Medidata" LocationType="Site" mdsol:Active="Yes">
             <MetaDataVersionRef StudyOID="Mediflex(Dev)" MetaDataVersionOID="1015" EffectiveDate="2013-05-02" mdsol:StudySiteNumber="" />
          </Location>
       </AdminData>
    </ODM>


.. _oa_users_request:
.. index:: UsersRequest

UsersRequest(project_name, environment_name, location_oid=None)
---------------------------------------------------------------

Authorization is required for this request.

Returns an ODM AdminData document listing all users associated with a study with optional filtering to a single
location.

Calls::

    https://{{ host }}/RaveWebServices/datasets/Users.odm/?studyoid={project_name}({environment_name})[&locationoid={locationoid}]


Options:

+--------------------------------+-----------------------------------------------------------------------------------+
| Option                         | Description                                                                       |
+================================+===================================================================================+
| locationoid                    | A site number from Rave that uniquely identifies a site                           |
+--------------------------------+-----------------------------------------------------------------------------------+


Example::

    >>> from rwslib import RWSConnection
    >>> from rwslib.rws_requests.odm_adapter import *
    >>> r = RWSConnection('https://innovate.mdsol.com', 'username', 'password')
    >>> r.send_request(UsersRequest('SIMPLESTUDY','TEST'))
    <?xml version="1.0" encoding="UTF-8"?>
    <ODM xmlns="http://www.cdisc.org/ns/odm/v1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata" ODMVersion="1.3" FileType="Snapshot" FileOID="7c2ef3a2-8df5-405c-bacc-c3ae220ed2bd" CreationDateTime="2016-04-13T14:20:01">
       <AdminData>
          <User OID="isparks_other_account" UserType="Other" mdsol:Active="Yes" mdsol:UserGroup="Test" mdsol:SiteGroup="World" mdsol:UserRole="Batch Upload">
             <LoginName>isparks_other_account</LoginName>
             <DisplayName>Ian Sparks</DisplayName>
             <FullName>Ian  Sparks</FullName>
             <FirstName>Ian</FirstName>
             <LastName>Sparks</LastName>
             <Address />
             <Email>isparks@mdsol.com</Email>
             <Fax />
             <Phone />
             <LocationRef LocationOID="TESTSITE" />
             <LocationRef LocationOID="TESTSITE2" />
          </User>
          <!-- More Users here -->
       </AdminData>
    </ODM>


.. _oa_signature_defs_request:
.. index:: SignatureDefinitionsRequest

SignatureDefinitionsRequest(project_name)
-----------------------------------------

Authorization is required for this request.

Returns an ODM AdminData document listing the definition of all signatures for this study (across all environments).
This allows you to match signature audits to their definitions and know in what context a signature was being made.

Calls::

    https://{{ host }}/RaveWebServices/datasets/Signatures.odm/?studyid={project_name}


Example::

    >>> from rwslib import RWSConnection
    >>> from rwslib.rws_requests.odm_adapter import *
    >>> r = RWSConnection('https://innovate.mdsol.com', 'username', 'password')
    >>> r.send_request(SignatureDefinitionsRequest('SIMPLESTUDY'))
    <?xml version="1.0" encoding="UTF-8"?>
    <ODM xmlns="http://www.cdisc.org/ns/odm/v1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata" ODMVersion="1.3"
         FileType="Snapshot" FileOID="1d885ac2-ffc7-4b10-a2ab-bfc056a1d57e" CreationDateTime="2016-04-13T16:08:44">
       <AdminData>
          <SignatureDef Methodology="Electronic" OID="2866" mdsol:Study="SIMPLESTUDY">
             <Meaning>Approval</Meaning>
             <LegalReason>I hereby confirm that all data is accurate to the best of my knowledge.</LegalReason>
          </SignatureDef>
          <SignatureDef Methodology="Electronic" OID="2867" mdsol:Study="SIMPLESTUDY">
             <Meaning>Approval</Meaning>
             <LegalReason>I hereby confirm that all data is accurate to the best of my knowledge.</LegalReason>
          </SignatureDef>
          <SignatureDef Methodology="Electronic" OID="2919" mdsol:Study="SIMPLESTUDY">
             <Meaning>Approval</Meaning>
             <LegalReason>I hereby confirm that all data is accurate to the best of my knowledge.</LegalReason>
          </SignatureDef>
          <SignatureDef Methodology="Electronic" OID="2976" mdsol:Study="SIMPLESTUDY">
             <Meaning>Approval</Meaning>
             <LegalReason>I hereby confirm that all data is accurate to the best of my knowledge.</LegalReason>
          </SignatureDef>
       </AdminData>
    </ODM>


