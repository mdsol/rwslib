API
***

The rwslib API.

ProtocolNames, StudyNames and Environments
------------------------------------------

rwslib uses some standard definitions for studyname, protocol names and environments. It defines them as:

* ProtocolName - The name of the study without environment e.g. the Mediflex in **Mediflex** (Dev)
* Environment  - The environment within the study e.g. the Dev in Mediflex (**Dev**)
* StudyName    - The combination of ProtocolName and Environment **Mediflex (Dev)**


version()
---------

Returns the text result of calling::

    https://{{ host }}.mdsol.com/RaveWebServices/version

Example::

    >>> from rwslib import RWSConnection
    >>> r = RWSConnection('https://innovate.mdsol.com', 'username', 'password')  #Authorization optional
    >>> r.version()
    1.8.0


studies()
---------

Authorization is required for this method.

Returns a RWSStudies object which has ODM document attributes and a list of RWSStudy objects.

Calls::

    https://{{ host }}.mdsol.com/RaveWebServices/version

Example::

    >>> from rwslib import RWSConnection
    >>> r = RWSConnection('https://innovate.mdsol.com', 'username', 'password')  #Authorization required
    >>> studies = r.studies()
    >>> studies.ODMVersion
    '1.3'
    >>> studies.fileoid
    'aa0dc756-b9f3-4bb2-ab4c-ee91e573e8fb'
    >>> studies.filetype
    'Snapshot'
    >>> studies.creationdatetime
    '2013-06-04T15:58:24.781-00:00'
    >>> len(studies)
    1
    >>> for study in studies:
    ...    print "OID",study.oid
    ...    print "Name",study.studyname
    ...    print "Protocolname",study.protocolname
    ...    print "IsProd?",study.isProd()
    ...
    OID Mediflex(Dev)
    Name Mediflex (Dev)
    Protocolname Mediflex
    IsProd? False


study_drafts(protocol_name)
---------------------------

Authorization is required for this method.

Returns a RWSStudyMetadataVersions object which inherits from RWSStudy. This has ODM document attributes,
study attributes and a list of MetaDataVersion objects representing Rave Architect Drafts.

Calls::

    https://{{ host }}.mdsol.com/RaveWebServices/metadata/studies/{{ protocol_name }}/drafts


Example::


    >>> from rwslib import RWSConnection
    >>> r = RWSConnection('https://innovate.mdsol.com', 'username', 'password')

    >>> protocol_name = 'Mediflex'
    >>> drafts = r.study_drafts(protocol_name)

    >>> drafts.fileoid
    e88d622d-8ddd-476c-8978-ccfe23b26969

    >>> drafts.study.studyname
    Mediflex

    >>> for draft in drafts:
    ...    print draft.name, draft.oid
    Draft2 1006
    Draft1 126


study_versions(protocol_name)
-----------------------------

Authorization is required for this method.

Returns a RWSStudyMetadataVersions object which inherits from RWSStudy. This has ODM document attributes,
study attributes and a list of MetaDataVersion objects representing Rave Architect Versions.

Calls::

    https://{{ host }}.mdsol.com/RaveWebServices/metadata/studies/{{ protocol_name }}/versions

Example::


    >>> from rwslib import RWSConnection
    >>> r = RWSConnection('https://innovate.mdsol.com', 'username', 'password')

    >>> protocol_name = 'Mediflex'
    >>> versions = r.study_versions(protocol_name)

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



study_version(protocol_name, version_oid)
-----------------------------------------

Authorization is required for this method.

Returns a unicode string of the ODM Metadata for this study version.

Calls::

    https://{{ host }}.mdsol.com/RaveWebServices/metadata/studies/{{ protocol_name }}/versions/{{ version_oid }}

Example::


    >>> from rwslib import RWSConnection
    >>> r = RWSConnection('https://innovate.mdsol.com', 'username', 'password')

    >>> protocol_name = 'Mediflex'
    >>> version_oid = 1015
    >>> r.study_version(protocol_name, version_oid)
    <ODM FileType="Snapshot" Granularity="Metadata" CreationDateTime="2013-06-05T08:30:45.900-00:00" FileOID="012d24dd-d7d8-44fe-997b-b287ae4faf7e" ODMVersion="1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata" xmlns="http://www.cdisc.org/ns/odm/v1.3">
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






