API
***

The rwslib API.

Projectnames, Studynames and Environments
------------------------------------------

rwslib uses some standard definitions for studyname, protocol names and environments. It defines them as:

* Projectname  - The name of the study without environment e.g. the Mediflex in **Mediflex** (Dev)
* Environment  - The environment within the study e.g. the Dev in Mediflex (**Dev**)
* StudyName    - The combination of projectname and environment **Mediflex (Dev)**


version()
---------

Returns the text result of calling::

    https://{{ host }}/RaveWebServices/version

Example::

    >>> from rwslib import RWSConnection
    >>> r = RWSConnection('innovate', 'username', 'password')  #Authorization optional
    >>> r.version()
    1.8.0


clinical_studies()
------------------

Authorization is required for this method.

Returns a RWSStudies object which has ODM document attributes and a list of RWSStudy objects. These are
the clinical studies that you have access to as an EDC user.

Calls::

    https://{{ host }}/RaveWebServices/studies

Example::

    >>> from rwslib import RWSConnection
    >>> r = RWSConnection('https://innovate.mdsol.com', 'username', 'password')  #Authorization required
    >>> studies = r.clinical_studies()
    >>> studies.ODMVersion
    1.3
    >>> studies.fileoid
    aa0dc756-b9f3-4bb2-ab4c-ee91e573e8fb
    >>> studies.filetype
    Snapshot
    >>> studies.creationdatetime
    2013-06-04T15:58:24.781-00:00
    >>> len(studies)
    1
    >>> for study in studies:
    ...    print "OID",study.oid
    ...    print "Name",study.studyname
    ...    print "protocolname",study.protocolname
    ...    print "IsProd?",study.isProd()
    ...
    OID Mediflex(Dev)
    Name Mediflex (Dev)
    protocolname Mediflex
    IsProd? False


metadata_studies()
------------------

Authorization is required for this method.

Returns a RWSStudies object which has ODM document attributes and a list of RWSStudy objects. These are
the studies you have access to as an Architect user. Use clinical_studies to get a list of studies that
you an interact with as an EDC user.

Calls::

    https://{{ host }}/RaveWebServices/metadata/studies

Example::

    >>> from rwslib import RWSConnection
    >>> r = RWSConnection('innovate', 'username', 'password')  #Authorization required
    >>> studies = r.metadata_studies()
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
    ...    print "------"
    ...    print "OID",study.oid
    ...    print "Name",study.studyname
    ...    print "protocolname",study.protocolname
    ...    print "IsProd?",study.isProd()
    ...    print "ProjectType",study.projecttype
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


study_drafts(projectname)
---------------------------

Authorization is required for this method.

Returns a RWSStudyMetadataVersions object which inherits from RWSStudy. This has ODM document attributes,
study attributes and a list of MetaDataVersion objects representing Rave Architect Drafts.

Calls::

    https://{{ host }}/RaveWebServices/metadata/studies/{{ projectname }}/drafts


Example::


    >>> from rwslib import RWSConnection
    >>> r = RWSConnection('innovate', 'username', 'password')

    >>> projectname = 'Mediflex'
    >>> drafts = r.study_drafts(projectname)

    >>> drafts.fileoid
    e88d622d-8ddd-476c-8978-ccfe23b26969

    >>> drafts.study.studyname
    Mediflex

    >>> for draft in drafts:
    ...    print draft.name, draft.oid
    Draft2 1006
    Draft1 126


library_drafts(projectname)
---------------------------

Authorization is required for this method.

Returns a RWSStudyMetadataVersions object which inherits from RWSStudy. This has ODM document attributes,
study attributes and a list of MetaDataVersion objects representing Rave Architect Global Library Drafts

Calls::

    https://{{ host }}/RaveWebServices/metadata/libraries/{{ projectname }}/drafts


Example::


    >>> from rwslib import RWSConnection
    >>> r = RWSConnection('https://innovate.mdsol.com', 'username', 'password')

    >>> drafts = r.library_drafts('Rave CDASH')
    >>> print drafts.fileoid
    be117ac3-e7ea-48fc-8bd8-373eb387703f

    >>> for draft in drafts:
         print "%s - %s" % (draft.name, draft.oid,)
    Rave CDASH 01 - 397

study_versions(projectname)
-----------------------------

Authorization is required for this method.

Returns a RWSStudyMetadataVersions object which inherits from RWSStudy. This has ODM document attributes,
study attributes and a list of MetaDataVersion objects representing Rave Architect Versions.

Calls::

    https://{{ host }}/RaveWebServices/metadata/studies/{{ projectname }}/versions

Example::


    >>> from rwslib import RWSConnection
    >>> r = RWSConnection('https://innovate.mdsol.com', 'username', 'password')

    >>> projectname = 'Mediflex'
    >>> versions = r.study_versions(projectname)

    >>> versions.fileoid
    66567494-c76a-4b94-afbb-64f5c1b21cbb

    >>> versions.study.studyname
    Mediflex

    >>> for version in versions:
    ...    print version.name, version.oid
    v19 1015
    v18 1007
    v17 999
    v16 481


library_versions(projectname)
-----------------------------

Authorization is required for this method.

Returns a RWSStudyMetadataVersions object which inherits from RWSStudy. This has ODM document attributes,
study attributes and a list of MetaDataVersion objects representing Rave Global Library Versions for
a library volume.

Calls::

    https://{{ host }}/RaveWebServices/metadata/libraries/{{ projectname }}/versions

Example::


    >>> from rwslib import RWSConnection
    >>> r = RWSConnection('https://innovate.mdsol.com', 'username', 'password')

    >>> versions = r.library_versions('Rave CDASH')
    >>> versions.fileoid
    50252a80-e233-4d30-9e69-b510e965e44a

    >>> versions.study.studyname
    Rave CDASH

    >>> for version in versions:
    ...    print "%s - %s" % (version.name, version.oid,)
    1.0 - 398


study_version(projectname, version_oid)
-----------------------------------------

Authorization is required for this method.

Returns a unicode string of the ODM Metadata for this study version.

Calls::

    https://{{ host }}/RaveWebServices/metadata/studies/{{ projectname }}/versions/{{ version_oid }}

Example::


    >>> from rwslib import RWSConnection
    >>> r = RWSConnection('innovate', 'username', 'password')

    >>> projectname = 'Mediflex'
    >>> version_oid = 1015
    >>> r.study_version(projectname, version_oid)
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


library_version(projectname, version_oid)
-----------------------------------------

Authorization is required for this method.

Returns a unicode string of the ODM Metadata for this study version.

Calls::

    https://{{ host }}/RaveWebServices/metadata/libraries/{{ projectname }}/versions/{{ version_oid }}

Example::


    >>> from rwslib import RWSConnection
    >>> r = RWSConnection('innovate', 'username', 'password')

    >>> r.library_version("Rave CDASH", 395)
    <ODM FileType="Snapshot" Granularity="Metadata" CreationDateTime="2013-06-07T15:36:23.531-00:00" FileOID="f914dbf8-41fc-492b-bc8f-f4c98e471c38" ODMVersion="1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata" xmlns="http://www.cdisc.org/ns/odm/v1.3">
      <Study OID="Rave CDASH" mdsol:ProjectType="GlobalLibraryVolume">
        <GlobalVariables>
          <StudyName>Rave CDASH</StudyName>
          <StudyDescription></StudyDescription>
          <ProtocolName>Rave CDASH</ProtocolName>
        </GlobalVariables>
        <BasicDefinitions />
        <MetaDataVersion OID="398" Name="1.0" mdsol:PrimaryFormOID="SUBJECT" mdsol:DefaultMatrixOID="PRIMARY" mdsol:SignaturePrompt="I hereby confirm that all data is accurate to the best of my knowledge.">
          <Protocol>
          ...


study_datasets(projectname)
-----------------------------------------

Authorization is required for this method.
Clinical Views must be active for this method to work.

Returns a unicode string of the ODM Clinical Data for all datasets for the study.

.. warning::

    This is a potentially very large download for an existing study.

This method takes a variety of options:

+-------------------------------+-----------------------------------------------------------------------------------+
| Option                        | Description                                                                       |
+===============================+===================================================================================+
| environment_name={{env}}      | Only extracts dataset information for the environment named. Defaults to PROD     |
+-------------------------------+-----------------------------------------------------------------------------------+
| rawsuffix={{suffix}}          | e.g. .RAW means raw field definitions are suffixes with .RAW  ex. AE_STDT.RAW     |
+-------------------------------+-----------------------------------------------------------------------------------+
| dataset_type={{regular|raw}}  | Limit extracts to regular or raw data                                             |
+-------------------------------+-----------------------------------------------------------------------------------+
| start={{ISO 8601 date}}       | Request changes to this dataset since the start date. Note that CV's must be set  |
|                               | to Include Inactive for this option to work.                                      |
+-------------------------------+-----------------------------------------------------------------------------------+



Calls::

    https://{{ host }}/RaveWebServices/studies/{{ projectname }} ({{ environment_name}})/datasets/{{regular|raw}}?<{{options}}

Example::


    >>> from rwslib import RWSConnection
    >>> r = RWSConnection('innovate', 'username', 'password')

    >>> projectname = 'Mediflex'
    >>> r.study_datasets(projectname, 'Dev', dataset_type='regular', rawsuffix='.RAW')
    ï»¿<?xml version="1.0" encoding="utf-8"?>
       <ODM FileType="Snapshot" FileOID="6b967555-8e05-4890-afb2-c2d2f1496031"
            CreationDateTime="2013-06-07T13:13:52.883-00:00"
            ODMVersion="1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata"
            xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.cdisc.org/
            ....
            <ClinicalData StudyOID="Mediflex(Dev)" MetaDataVersionOID="16">
                <SubjectData SubjectKey="123 ABC">
                    <SiteRef LocationOID="MDSOL" />
                    <StudyEventData StudyEventOID="SUBJECT">
                        <FormData FormOID="AE" FormRepeatKey="1">
                            <ItemGroupData ItemGroupOID="AE_LOG_LINE" ItemGroupRepeatKey="1">
                                <ItemData ItemOID="AE.AEYN" Value="Y" />
                                <ItemData ItemOID="AE.AETERM" Value="HEADACHE" />
                                <ItemData ItemOID="AE.AESTDTC" Value="2008-01-01" />
                                <ItemData ItemOID="AE.AESTDTC.RAW" Value="01 JAN 2008" />
                                <ItemData ItemOID="AE.AEONG" Value="N" />
                                <ItemData ItemOID="AE.AEENDTC" Value="2008-01-01" />
                                <ItemData ItemOID="AE.AEENDTC.RAW" Value="01 JAN 2008" />
                                ...

.. note::

    Note that this XML string includes the Byte Order Mark (BOM) as sent by RWS and does not include line breaks
    as shown in the above example. Depending on how you intend to parse the XML returned you may need to
    strip the BOM.