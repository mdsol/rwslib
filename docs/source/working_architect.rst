.. _architect:

Working with Architect Metadata
*******************************

Access to Architect study designs relies on the credentials you supply having access to Rave Architect.
See :ref:`glv` for details on how to access study Metadata in Global Libraries.

.. index:: metadata_studies
.. _metdata_studies:

metadata_studies()
------------------

Authorization is required for this method.

Returns a RWSStudies object which has ODM document attributes and a list of RWSStudy objects. These are
the studies you have access to as an Architect user. Use :ref:`clinical_studies` to get a list of studies that
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



