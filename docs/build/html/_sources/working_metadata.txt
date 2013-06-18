.. _glv:

Working with Global Library Metadata
************************************

rwslib provides access to metadata stored in Rave Global Library Volumes. You must provide credentials that
have access to Global Library Volumes to read this metadata. See :ref:`architect` for information on working
with Architect Study Designs.


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

.. note::

    At this time RWS does not provide a way retrieve the ODM for a Draft, only for a Version.

