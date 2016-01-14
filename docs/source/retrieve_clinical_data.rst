.. _working_clinical_data:

Working with Clinical Data
**************************

The rws_requests module provides a number of standard requests which provide lists of clinical studies, extract
clinical data (from Rave Clinical Views) and post clinical data to Rave.

Projectnames, Studynames and Environments
------------------------------------------

rwslib uses some standard definitions for studyname, protocol names and environments. It defines them as:

* Projectname  - The name of the study without environment e.g. the Mediflex in **Mediflex** (Dev)
* Environment  - The environment within the study e.g. the Dev in Mediflex (**Dev**)
* StudyName    - The combination of projectname and environment **Mediflex (Dev)**


.. index:: ClinicalStudiesRequest
.. _clinical_studies:


ClinicalStudiesRequest()
------------------------

Authorization is required for this method.

Returns a :class:`rwsobjects.RWSStudies` object which has ODM document attributes and a list of
:class:`rwsobjects.RWSStudyListItem` objects. These are the clinical studies that you have access to as an EDC user.

Calls::

    https://{ host }/RaveWebServices/studies

Example::

    >>> from rwslib import RWSConnection
    >>> from rwslib.rws_requests import ClinicalStudiesRequest
    >>> r = RWSConnection('https://innovate.mdsol.com', 'username', 'password')  #Authorization required
    >>> studies = r.send_request(ClinicalStudiesRequest())
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
    ...    print("OID",study.oid)
    ...    print("Name",study.studyname)
    ...    print("protocolname",study.protocolname)
    ...    print("IsProd?",study.isProd())
    ...
    OID Mediflex(Dev)
    Name Mediflex (Dev)
    protocolname Mediflex
    IsProd? False


.. _study_subjects:
.. index:: StudySubjectsRequest

StudySubjectsRequest(self, project_name, environment_name)
----------------------------------------------------------

Authorization is required for this method.

Retrieves a :class:`rwsobjects.RWSSubjects` object which is a list of :class:`rwsobjects.RWSSubjectListItem` objects,
each representing key information about a subject. This does not include clinical data for a subject.

+-----------------------------------------------+-----------------------------------------------------------------------------------+
| Option                                        | Description                                                                       |
+===============================================+===================================================================================+
| status={True|False}                           | If True, extracts status information at the subject level. Default = False        |
+-----------------------------------------------+-----------------------------------------------------------------------------------+
| links={True|False}                            | If True, includes "deep link"(s) (URL) to the subject page in Rave.Default = False|
+-----------------------------------------------+-----------------------------------------------------------------------------------+
| include={inactive|deleted|inactiveAndDeleted} | Include inactive subjects, deleted subjects or both? By default these subjects are|
|                                               | omitted.                                                                          |
+-----------------------------------------------+-----------------------------------------------------------------------------------+
| subject_key_type={SubjectName|SubjectUUID}    | Request that the Subject Name is in the SubjectKey field (_SubjectName_) or in the|
|                                               | mdsol:SubjectName field (with the Subject UUID in the SubjectKey field).          |
+-----------------------------------------------+-----------------------------------------------------------------------------------+

Calls::

    https://{ host }/RaveWebServices/studies/{ projectname } ({ environment_name})/subjects?{options}

Example::

    >>> from rwslib import RWSConnection
    >>> from rwslib.rws_requests import StudySubjectsRequest
    >>> r = RWSConnection('https://innovate.mdsol.com', 'username', 'password')  #Authorization required
    >>> subject_list = rave.send_request(StudySubjectsRequest("SIMPLESTUDY","PROD")
    >>> subject_list.ODMVersion
    1.3
    >>> for subject in subject_list:
    ...     print "Name: %s" % subject.subjectkey
    Name: 1
    Name: 10
    Name: 2
    Name: 3
    Name: 4
    ...
    >>> r.last_url
    https://innovate.mdsol.com/RaveWebServices/studies/SIMPLESTUDY(PROD)/subjects
    >>> str(subject_list)
    <ODM xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.cdisc.org/ns/odm/v1.3" FileType="Snapshot" FileOID="1af945c7-8334-4eb8-b7a9-735fb5c7db03" CreationDateTime="2013-09-10T09:28:21.145-00:00" ODMVersion="1.3">
      <ClinicalData StudyOID="SIMPLESTUDY(TEST)" MetaDataVersionOID="1128">
        <SubjectData SubjectKey="1">
          <SiteRef LocationOID="TESTSITE"/>
        </SubjectData>
      </ClinicalData>
      <ClinicalData StudyOID="SIMPLESTUDY(TEST)" MetaDataVersionOID="1128">
        <SubjectData SubjectKey="10">
          <SiteRef LocationOID="TESTSITE"/>
        </SubjectData>
      </ClinicalData>
      <ClinicalData StudyOID="SIMPLESTUDY(TEST)" MetaDataVersionOID="1128">
        <SubjectData SubjectKey="2">
          <SiteRef LocationOID="TESTSITE"/>
        </SubjectData>
      </ClinicalData>
      <ClinicalData StudyOID="SIMPLESTUDY(TEST)" MetaDataVersionOID="1128">
        <SubjectData SubjectKey="3">
          <SiteRef LocationOID="TESTSITE"/>
        </SubjectData>
      </ClinicalData>
      <ClinicalData StudyOID="SIMPLESTUDY(TEST)" MetaDataVersionOID="1128">
        <SubjectData SubjectKey="4">
          <SiteRef LocationOID="TESTSITE"/>
        </SubjectData>
      </ClinicalData>
      <ClinicalData StudyOID="SIMPLESTUDY(TEST)" MetaDataVersionOID="1128">
      ...
    >>> subject_list = rave.send_request(StudySubjectsRequest("SIMPLESTUDY", "PROD", subject_key_type="SubjectUUID")
    >>> str(subject_list)
    <ODM xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.cdisc.org/ns/odm/v1.3" FileType="Snapshot" FileOID="1af945c7-8334-4eb8-b7a9-735fb5c7db03" CreationDateTime="2013-09-10T09:28:21.145-00:00" ODMVersion="1.3">
      <ClinicalData StudyOID="SIMPLESTUDY(TEST)" MetaDataVersionOID="1128">
        <SubjectData SubjectKey="0C1F5F71-B136-4C95-8199-1397F4262B31" mdsol:SubjectKeyType="SubjectUUID" mdsol:SubjectName="1">
          <SiteRef LocationOID="TESTSITE"/>
        </SubjectData>
      </ClinicalData>
      <ClinicalData StudyOID="SIMPLESTUDY(TEST)" MetaDataVersionOID="1128">
        <SubjectData SubjectKey="91F686CE-37A0-4A9D-BC3B-CFFC3C609ECC" mdsol:SubjectKeyType="SubjectUUID" mdsol:SubjectName="10">
          <SiteRef LocationOID="TESTSITE"/>
        </SubjectData>
      </ClinicalData>
      <ClinicalData StudyOID="SIMPLESTUDY(TEST)" MetaDataVersionOID="1128">
      ...
    >>> for subject in subject_list:
    ...     print "Name: %s (%s)" % (subject.subject_name, subject.subjectkey)
    Name: 1 (0C1F5F71-B136-4C95-8199-1397F4262B31)
    Name: 10 (91F686CE-37A0-4A9D-BC3B-CFFC3C609ECC)
    ...



.. _odm_clinical_datasets:
.. index:: ODM Clinical Datasets


ODM Clinical View Datasets
**************************

.. important::

    Clinical Views must be active for these requests to work.

RWS allows extraction of clinical data from Rave's Clinical Views by 3 strata:

1. By Study
2. By Individual Subject
3. By MetaData Version

All 3 variants take the same options:

+--------------------------------+-----------------------------------------------------------------------------------+
| Option                         | Description                                                                       |
+================================+===================================================================================+
| dataset_type={regular|raw}     | Limit extracts to regular or raw data. Default is regular.                        |
+--------------------------------+-----------------------------------------------------------------------------------+
| start={ISO 8601 date}          | Request changes to this dataset since the start date. Note that CV's must be set  |
|                                | to *Include Inactive* for this option to work.                                    |
+--------------------------------+-----------------------------------------------------------------------------------+
| rawsuffix={suffix}             | e.g. .RAW means raw field definitions are suffixes with .RAW  ex. AE_STDT.RAW     |
+--------------------------------+-----------------------------------------------------------------------------------+
| formoid={form oid}             | Only extracts dataset information for the named form. If missing extracts for     |
|                                | all forms.                                                                        |
+--------------------------------+-----------------------------------------------------------------------------------+
| versionitem={version_suffix}   | Add MetaDataVersionOID="<<datetime>>" and additional itemlevel version ItemData   |
|                                | element per ItemGroup to identify last CV update date and CRF Version each        |
|                                | itemgroup was entered under e.g. <ItemData ItemOID="AE.VERSION" Value="16" />     |
+--------------------------------+-----------------------------------------------------------------------------------+
| codelistsuffix={cl_suffix}     | Add name of codelist as an item for each field with data dictionary.              |
|                                | e.g. codelistsuffix="CL" results in                                               |
|                                | <ItemData ItemDataOID="DM.SEX.CL" Value="GENDERS"/>                               |
+--------------------------------+-----------------------------------------------------------------------------------+
| decodesuffix={decode_suffix}   | Add user value of codelist entry as an item for each field with data dictionary.  |
|                                | e.g.decodesuffix="DECODE" results in                                              |
|                                | <ItemData ItemDataOID="DM.SEX.DECODE" Value="Male"/>                              |
+--------------------------------+-----------------------------------------------------------------------------------+
| stdsuffix={decode_suffix}      | Adds standard and unit data values to a full or incremental dataset, and          |
|                                | identifies these values with {std-suffix}.                                        |
+--------------------------------+-----------------------------------------------------------------------------------+


.. _study_dataset:
.. index:: StudyDatasetRequest


StudyDatasetRequest(project_name, environment_name)
---------------------------------------------------

Authorization is required for this method.

Returns a unicode string of the ODM Clinical Data for the study / environment. Can be filtered by
form (i.e. to return only data for a single form type) and by start date for an incremental dataset.

.. warning::

    If not filtered by form this is a potentially very large download for an existing study.


Calls::

    https://{ host }/RaveWebServices/studies/{ projectname } ({ environment_name})/datasets/{ regular|raw }?{options}

    or (form filtered)

    https://{ host }/RaveWebServices/studies/{ projectname } ({ environment_name})/datasets/{ regular|raw }/{ formoid }?{options}

Example::


    >>> from rwslib import RWSConnection
    >>> from rwslib.rws_requests import StudyDatasetRequest
    >>> r = RWSConnection('innovate', 'username', 'password')
    >>> r.send_request(StudyDatasetRequest('Mediflex', 'DEV'))
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


Form Example::

    >>> from rwslib import RWSConnection
    >>> from rwslib.rws_requests import StudyDatasetRequest
    >>> r = RWSConnection('innovate', 'username', 'password')
    >>> r.send_request(StudyDatasetRequest('SimpleStudy', 'TEST', formoid='VITAL'))
    ï»¿<?xml version="1.0" encoding="utf-8"?>
       <ODM xmlns="http://www.cdisc.org/ns/odm/v1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata" xmlns:xlink="http://www.w3.org/1999/xlink" FileType="Snapshot" FileOID="f323dba3-b31b-4e61-8894-104353fac743" CreationDateTime="2013-09-10T08:33:25.811-00:00" ODMVersion="1.3">
           <ClinicalData StudyOID="SIMPLESTUDY(TEST)" MetaDataVersionOID="1128">
               <SubjectData SubjectKey="1">
                   <SiteRef LocationOID="TESTSITE" />
                   <StudyEventData StudyEventOID="SCREEN" StudyEventRepeatKey="1">
                       <FormData FormOID="VITAL" FormRepeatKey="1">
                           <ItemGroupData ItemGroupOID="VITAL_LOG_LINE">
                               <ItemData ItemOID="VITAL.VDAT" Value="2013-02-01" />
                               <ItemData ItemOID="VITAL.WEIGHT_KG" Value="132.0" />
                               <ItemData ItemOID="VITAL.HEIGHT_CM" Value="174.5" />
                           </ItemGroupData>
                       </FormData>
                   </StudyEventData>
               </SubjectData>
           </ClinicalData>
           <ClinicalData StudyOID="SIMPLESTUDY(TEST)" MetaDataVersionOID="1128">
               <SubjectData SubjectKey="2">
                   <SiteRef LocationOID="TESTSITE" />
           ...
    >>> r.last_url
    https://innovate.mdsol.com/RaveWebServices/studies/SIMPLESTUDY(TEST)/datasets/regular/VITAL


.. note::

    Note that the XML string returned by this method includes the Byte Order Mark (BOM) as sent by RWS and does not
    include line breaks as shown in the above example. Depending on how you intend to parse the XML returned you may
    need to strip the BOM.


.. _subject_datasets:
.. index:: SubjectDatasetRequest


SubjectDatasetRequest(project_name, environment_name, subjectkey)
-----------------------------------------------------------------

Authorization is required for this method.

Extracts ODM data for a single subject.

Calls::

    https://{ host }/RaveWebServices/studies/{ projectname } ({ environment_name})/subjects/{ subjectkey }/datasets/{ regular|raw }?{options}

    or (form filtered)

    https://{ host }/RaveWebServices/studies/{ projectname } ({ environment_name})/subjects/{ subjectkey }/datasets/{ regular|raw }/{ formoid }?{options}

Example::

    >>> from rwslib import RWSConnection
    >>> r = RWSConnection('innovate', 'username', 'password')
    >>> from rwslib.rws_requests import SubjectDatasetRequest
    >>> r.send_request(SubjectDatasetRequest('SIMPLESTUDY','TEST','1', formoid='ENROL'))
    ï»¿<?xml version="1.0" encoding="UTF-8"?>
    <ODM xmlns="http://www.cdisc.org/ns/odm/v1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata" xmlns:xlink="http://www.w3.org/1999/xlink" FileType="Snapshot" FileOID="c850bb82-f08f-4f43-9c8c-fce2b5e80e79" CreationDateTime="2013-09-10T15:23:22.395-00:00" ODMVersion="1.3">
        <ClinicalData StudyOID="SIMPLESTUDY(TEST)" MetaDataVersionOID="1128">
            <SubjectData SubjectKey="1">
                <SiteRef LocationOID="TESTSITE" />
                <StudyEventData StudyEventOID="SUBJECT">
                    <FormData FormOID="ENROL" FormRepeatKey="1">
                        <ItemGroupData ItemGroupOID="ENROL_LOG_LINE">
                            <ItemData ItemOID="ENROL.SUBID" Value="1" />
                            <ItemData ItemOID="ENROL.BIRTHDT" Value="1973-06-26" />
                        </ItemGroupData>
                    </FormData>
                </StudyEventData>
            </SubjectData>
        </ClinicalData>
    </ODM>
    >>> r.last_url
    https://innovate.mdsol.com/RaveWebServices/studies/SIMPLESTUDY(TEST)/subjects/1/datasets/regular/ENROL


.. _version_datasets:
.. index:: VersionDatasetRequest

VersionDatasetRequest(project_name, environment_name, version_oid)
------------------------------------------------------------------

Authorization is required for this method.

Extracts ODM data for a single Rave study version across all subjects.

Calls::

    https://{ host }/RaveWebServices/studies/{ projectname } ({ environment_name})/versions/{ version_id }/datasets/{ regular|raw }?{options}

    or (form filtered)

    https://{ host }/RaveWebServices/studies/{ projectname } ({ environment_name})/versions/{ version_id }/datasets/{ regular|raw }/{ formoid }?{options}

Example::

    >>> from rwslib import RWSConnection
    >>> r = RWSConnection('innovate', 'username', 'password')
    >>> from rwslib.rws_requests import VersionDatasetRequest
    >>> r.send_request(VersionDatasetRequest('SIMPLESTUDY','TEST',1128, formoid='VITAL'))
    ï»¿<?xml version="1.0" encoding="UTF-8"?>
    <ODM xmlns="http://www.cdisc.org/ns/odm/v1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata" xmlns:xlink="http://www.w3.org/1999/xlink" FileType="Snapshot" FileOID="00d28b0e-df45-43a4-93dc-7e4dd3cf36e7" CreationDateTime="2013-09-10T15:45:54.179-00:00" ODMVersion="1.3">
        <ClinicalData StudyOID="SIMPLESTUDY(TEST)" MetaDataVersionOID="1128">
            <SubjectData SubjectKey="1">
                <SiteRef LocationOID="TESTSITE" />
                <StudyEventData StudyEventOID="SCREEN" StudyEventRepeatKey="1">
                    <FormData FormOID="VITAL" FormRepeatKey="1">
                        <ItemGroupData ItemGroupOID="VITAL_LOG_LINE">
                            <ItemData ItemOID="VITAL.VDAT" Value="2013-02-01" />
                            <ItemData ItemOID="VITAL.WEIGHT_KG" Value="132.0" />
                            <ItemData ItemOID="VITAL.HEIGHT_CM" Value="174.5" />
                        </ItemGroupData>
                    </FormData>
                </StudyEventData>
            </SubjectData>
        </ClinicalData>
        <ClinicalData StudyOID="SIMPLESTUDY(TEST)" MetaDataVersionOID="1128">
            <SubjectData SubjectKey="2">
                <SiteRef LocationOID="TESTSITE" />
                <StudyEventData StudyEventOID="SCREEN" StudyEventRepeatKey="1">
                    <FormData FormOID="VITAL" FormRepeatKey="1">
                        <ItemGroupData ItemGroupOID="VITAL_LOG_LINE">
                            <ItemData ItemOID="VITAL.VDAT" Value="2013-02-09" />
                               .....
    >>> r.last_url
    https://innovate.mdsol.com/RaveWebServices/studies/SIMPLESTUDY(TEST)/versions/1128/datasets/regular/VITAL


.. _x_mws_cv_last_updated:
.. index:: X-MWS-CV-Last-Updated

X-MWS-CV-Last-Updated
---------------------

The Clinical View datasets return a header, X-MWS-CV-Last-Updated, which tells you the last time a Clinical View was
updated.

This is especially important with Incremental calls using the ``start`` option to know whether the dataset has actually
been updated since your last call.

You can get the value of X-MWS-CV-Last-Updated via the last_result.headers property::

    >>> from rwslib import RWSConnection
    >>> from rwslib.rws_requests import StudyDatasetRequest
    >>> r = RWSConnection('innovate', 'username', 'password')
    >>> xml = r.send_request(StudyDatasetRequest('Mediflex', 'DEV'))
    >>> r.last_result.headers['X-MWS-CV-Last-Updated']
    2013-05-02T19:11:46



