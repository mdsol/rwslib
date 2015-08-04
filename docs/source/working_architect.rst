.. _architect:

Working with Architect Metadata
*******************************

Access to Architect study designs relies on the credentials you supply having access to Rave Architect.
See :ref:`glv` for details on how to access study Metadata in Global Libraries.

.. index:: MetadataStudiesRequest
.. _metdata_studies_request:

MetadataStudiesRequest()
------------------------

Authorization is required for this method.

Returns a :class:`rwsobjects.RWSStudies` object which has :class:`rwsobjects.ODMDoc` document attributes and a list of
:class:`rwsobjects.RWSStudyListItem` objects. These are the studies you have access to as an Architect user.

Use :ref:`clinical_studies` to get a list of studies that you an interact with as an EDC user.

Calls::

    https://{ host }/RaveWebServices/metadata/studies

Example::

    >>> from rwslib import RWSConnection
    >>> from rwslib.rws_requests import MetadataStudiesRequest
    >>> r = RWSConnection('innovate', 'username', 'password')  #Authorization required
    >>> studies = r.send_request(MetadataStudiesRequest())
    >>> studies.ODMVersion
    1.3
    >>> studies.fileoid
    4e7f5b37-3f77-4a80-8b91-c48978103bae
    >>> studies.filetype
    Snapshot
    >>> studies.creationdatetime
    2013-06-07T02:13:31
    >>> len(studies)
    1
    >>> for study in studies:
    ...    print("------")
    ...    print("OID",study.oid)
    ...    print("Name",study.studyname)
    ...    print("protocolname",study.protocolname)
    ...    print("IsProd?",study.isProd())
    ...    print("ProjectType",study.projecttype)
    ...
    ------
    OID Bill's New Library
    Name Bill's New Library
    protocolname Bill's New Library
    IsProd? False
    ProjectType GlobalLibraryVolume
    ------
    OID Rave CDASH
    Name Rave CDASH
    protocolname Rave CDASH
    IsProd? False
    ProjectType GlobalLibraryVolume

Studies returned in the list from metadata_studies() have an empty environment attribute since they represent
study designs, they do not have associated environments.

.. index:: StudyDraftsRequest
.. _study_drafts_requests:

StudyDraftsRequest(project_name)
--------------------------------

Authorization is required for this method.

Returns a :class:`rwsobjects.RWSStudyMetadataVersions` object which inherits from :class:`rwsobjects.RWSStudyListItem`.
This has ODM document attributes, study attributes and a list of :class:`rwsobjects.MetaDataVersion` objects
representing Rave Architect Drafts.

Calls::

    https://{ host }/RaveWebServices/metadata/studies/{ projectname }/drafts


Example::


    >>> from rwslib import RWSConnection
    >>> from rwslib.rws_requests import StudyDraftsRequest
    >>> r = RWSConnection('innovate', 'username', 'password')  #Authorization required
    >>> projectname = 'Mediflex'
    >>> drafts = r.send_request(StudyDraftsRequest(projectname))
    >>> drafts.fileoid
    e88d622d-8ddd-476c-8978-ccfe23b26969

    >>> drafts.study.studyname
    Mediflex

    >>> for draft in drafts:
    ...    print(draft.name, draft.oid)
    Draft2 1006
    Draft1 126


.. index:: StudyVersionsRequest

StudyVersionsRequest(projectname)
---------------------------------

Authorization is required for this method.

Returns a :class:`rwsobjects.RWSStudyMetadataVersions` object which inherits from :class:`rwsobjects.RWSStudyListItem`.
This has ODM document attributes, study attributes and a list of :class:`rwsobjects.MetaDataVersion` objects
representing Rave Architect Versions


Calls::

    https://{ host }/RaveWebServices/metadata/studies/{ projectname }/versions

Example::

    >>> from rwslib import RWSConnection
    >>> from rwslib.rws_requests import StudyVersionsRequest
    >>> r = RWSConnection('https://innovate.mdsol.com', 'username', 'password')
    >>> projectname = 'Mediflex'
    >>> versions = r.send_request(StudyVersionsRequest(projectname))
    >>> versions.fileoid
    66567494-c76a-4b94-afbb-64f5c1b21cbb
    >>> versions.study.studyname
    Mediflex
    >>> for version in versions:
    ...    print(version.name, version.oid)
    v19 1015
    v18 1007
    v17 999
    v16 481


.. index:: StudyVersionRequest

StudyVersionRequest(projectname, oid)
-------------------------------------

Authorization is required for this method.

Returns a unicode string of the ODM Metadata for this study version.

Calls::

    https://{ host }/RaveWebServices/metadata/studies/{ projectname }/versions/{ oid }

Example::


    >>> from rwslib import RWSConnection
    >>> from rwslib.rws_requests import StudyVersionRequest
    >>> r = RWSConnection('innovate', 'username', 'password')

    >>> projectname = 'Mediflex'
    >>> version_oid = 1015
    >>> r.send_request(StudyVersionRequest(projectname, version_oid))
    <ODM FileType="Snapshot" Granularity="Metadata" CreationDateTime="2013-06-05T08:30:45.900-00:00"
         FileOID="012d24dd-d7d8-44fe-997b-b287ae4faf7e" ODMVersion="1.3"
         xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata" xmlns="http://www.cdisc.org/ns/odm/v1.3">
      <Study OID="Mediflex">
        <GlobalVariables>
          <StudyName>Mediflex</StudyName>
          <StudyDescription></StudyDescription>
          <ProtocolName>Mediflex</ProtocolName>
        </GlobalVariables>
        <BasicDefinitions>
        ....

rwslib does not automatically parse this xml for you (you may want to control this yourself) but rwslib
does include some XML helper methods that make working with XML that is generated from web-services easier.

.. note::

    At this time RWS does not provide a way retrieve the ODM for a Draft, only for a Version.

.. index:: PostMetadataRequest

PostMetadataRequest(projectname, data)
--------------------------------------

Authorization is required for this method.

Creates a new study draft (or overwrites an existing one) with a new ODM definition.

Calls::

    POST https://{ host }/RaveWebServices/metadata/studies/{ projectname }/drafts

Options:

+------------------------------------------+--------------------------------------------------------------------------+
| Option                                   | Description                                                              |
+==========================================+==========================================================================+
| headers={'Content-type': "text/xml"}     | Set custom headers. May need to provide a Content-type if your RWS       |
|                                          | version is set to accept different standard content-type than default.   |
+------------------------------------------+--------------------------------------------------------------------------+

Example::


    >>> from rwslib import RWSConnection
    >>> from rwslib.rws_requests import PostMetadataRequest
    >>> r = RWSConnection('innovate', 'username', 'password')

    >>> projectname = 'TESTSTUDY'
    >>> odm_definition = """<ODM FileType="Snapshot" Granularity="Metadata"
    ...  CreationDateTime="2013-06-18T15:09:54.843-00:00" FileOID="82370e27-a6a5-41dc-8c07-829e489823df" ODMVersion="1.3"
    ...  xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata" xmlns="http://www.cdisc.org/ns/odm/v1.3">
    ...  <Study OID="TESTSTUDY">
    ...    <GlobalVariables>
    ...      <StudyName>TESTSTUDY</StudyName>
    ...      <StudyDescription></StudyDescription>
    ...      <ProtocolName>TESTSTUDY</ProtocolName>
    ...    </GlobalVariables>
    ...    <BasicDefinitions/>
    ...    <MetaDataVersion OID="1" Name="TINY STUDY" mdsol:PrimaryFormOID="ENROL" mdsol:DefaultMatrixOID="DEFAULT" mdsol:SignaturePrompt="Sign this please.">
    ...      <Protocol>
    ...        <StudyEventRef StudyEventOID="SCREEN" OrderNumber="1" Mandatory="No" />
    ...      </Protocol>
    ...      <StudyEventDef OID="SCREEN" Name="Screening" Type="Common" Repeating="Yes" mdsol:OrderNumber="1">
    ...        <FormRef FormOID="VITAL" OrderNumber="2" Mandatory="No" />
    ...      </StudyEventDef>
    ...      <FormDef OID="ENROL" Name="Enrol" Repeating="No" mdsol:OrderNumber="1" mdsol:ConfirmationStyle="None">
    ...        <ItemGroupRef ItemGroupOID="ENROL" Mandatory="Yes" />
    ...      </FormDef>
    ...      <FormDef OID="VITAL" Name="Vitals" Repeating="No" mdsol:OrderNumber="2">
    ...        <ItemGroupRef ItemGroupOID="VITAL" Mandatory="Yes" />
    ...      </FormDef>
    ...      <ItemGroupDef OID="ENROL" Name="ENROL" Repeating="No">
    ...        <ItemRef ItemOID="SUBID" OrderNumber="1" Mandatory="No" />
    ...        <ItemRef ItemOID="BIRTHDT" OrderNumber="2" Mandatory="No" />
    ...      </ItemGroupDef>
    ...      <ItemGroupDef OID="VITAL" Name="VITAL" Repeating="No">
    ...        <ItemRef ItemOID="WEIGHT_KG" OrderNumber="1" Mandatory="No" />
    ...        <ItemRef ItemOID="HEIGHT_CM" OrderNumber="2" Mandatory="No" />
    ...      </ItemGroupDef>
    ...      <ItemDef OID="SUBID" Name="SUBID" DataType="text" Length="10" mdsol:ControlType="Text">
    ...        <Question>
    ...          <TranslatedText xml:lang="en">Subject ID</TranslatedText>
    ...        </Question>
    ...      </ItemDef>
    ...      <ItemDef OID="BIRTHDT" Name="BIRTHDT" DataType="date" mdsol:DateTimeFormat="yyyy MMM dd" mdsol:ControlType="DateTime">
    ...        <Question>
    ...          <TranslatedText xml:lang="en">Date of Birth</TranslatedText>
    ...        </Question>
    ...      </ItemDef>
    ...      <ItemDef OID="WEIGHT_KG" Name="WEIGHT_KG" DataType="float" Length="4" SignificantDigits="1" mdsol:ControlType="Text">
    ...        <Question>
    ...          <TranslatedText xml:lang="en">Weight</TranslatedText>
    ...        </Question>
    ...      </ItemDef>
    ...      <ItemDef OID="HEIGHT_CM" Name="HEIGHT_CM" DataType="float" Length="4" SignificantDigits="1" mdsol:ControlType="Text">
    ...        <Question>
    ...          <TranslatedText xml:lang="en">Height</TranslatedText>
    ...        </Question>
    ...      </ItemDef>
    ...    </MetaDataVersion>
    ...  </Study>
    ... </ODM>

    >>> response = r.send_request(PPostMetadataRequest(projectname, odm_definition))
    >>> print(str(response))
    <Response ReferenceNumber="5b260cff-e136-4b44-9211-e473fa4d6048"
              InboundODMFileOID="82370e27-a6a5-41dc-8c07-829e489823df"
              IsTransactionSuccessful="1"
              SuccessStatistics="N/A" NewRecords="" DraftImported="1">
    </Response>


