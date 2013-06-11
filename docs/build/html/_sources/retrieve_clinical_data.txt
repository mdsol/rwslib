Retrieving Clinical Data
************************


.. _clinical_studies:

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



study_datasets(projectname)
-----------------------------------------

Authorization is required for this method.
Clinical Views must be active for this method to work.

Returns a unicode string of the ODM Clinical Data for all datasets for the study.

.. warning::

    This is a potentially very large download for an existing study.

This method takes a variety of options:

+--------------------------------+-----------------------------------------------------------------------------------+
| Option                         | Description                                                                       |
+================================+===================================================================================+
| environment_name={{env}}       | Only extracts dataset information for the environment named. Defaults to PROD     |
+--------------------------------+-----------------------------------------------------------------------------------+
| rawsuffix={{suffix}}           | e.g. .RAW means raw field definitions are suffixes with .RAW  ex. AE_STDT.RAW     |
+--------------------------------+-----------------------------------------------------------------------------------+
| dataset_type={{regular|raw}}   | Limit extracts to regular or raw data. Default is regular.                        |
+--------------------------------+-----------------------------------------------------------------------------------+
| start={{ISO 8601 date}}        | Request changes to this dataset since the start date. Note that CV's must be set  |
|                                | to Include Inactive for this option to work.                                      |
+--------------------------------+-----------------------------------------------------------------------------------+
| versionitem={{version_suffix}} | Add MetaDataVersionOID="<<datetime>>" and additional itemlevel version ItemData   |
|                                | element per ItemGroup to identify last CV update date and CRF Version each        |
|                                | itemgroup was entered under e.g. <ItemData ItemOID="AE.VERSION" Value="16" />     |
+--------------------------------+-----------------------------------------------------------------------------------+
| codelistsuffix={{cl_suffix}}   | Add name of codelist as an item for each field with data dictionary.              |
|                                | e.g. codelistsuffix="CL" results in                                               |
|                                | <ItemData ItemDataOID="DM.SEX.CL" Value="GENDERS"/>                               |
+--------------------------------+-----------------------------------------------------------------------------------+
| decodesuffix={{decode_suffix}} | Add user value of codelist entry as an item for each field with data dictionary.  |
|                                | e.g.decodesuffix="DECODE" results in                                              |
|                                | <ItemData ItemDataOID="DM.SEX.DECODE" Value="Male"/>                              |
+--------------------------------+-----------------------------------------------------------------------------------+


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

X-MWS-CV-Last-Updated
---------------------

Clinical View Datasets return a header, X-MWS-CV-Last-Updated, which tells you the last time a Clinical View was
updated. This is especially important with Incremental calls to know whether the dataset has actually been updated
since your last call.

You can get the value of X-MWS-CV-Last-Updated via the last_result.headers property::

    >>> from rwslib import RWSConnection
    >>> r = RWSConnection('innovate', 'username', 'password')
    >>> xml = rave.study_datasets(projectname, 'Dev', dataset_type='regular', rawsuffix='.RAW', versionitem="VERSION")
    >>> r.last_result.headers['X-MWS-CV-Last-Updated']
    2013-05-02T19:11:46


