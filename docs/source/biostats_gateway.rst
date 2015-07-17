.. _biostats_gateway:

Biostats Gateway Requests
*************************

rwslib provides a module, :mod:`rws_requests.biostats_gateway` which provides datasets designed to assist in the creation
of SDTM datasets including comments and protocol violations.

Many of the Biostats gateway requests pull data from the Rave Clinical Views. They will not return any data unless
Clinical Views are active in Rave.

Read more about Biostats Gateway in the
`Rave Web Services documentation <http://rws-webhelp.s3.amazonaws.com/WebHelp_ENG/solutions/01_biostat_adapter.html>`_


.. _cv_metadata_request:
.. index:: CVMetaDataRequest

CVMetaDataRequest(project_name, environment_name)
-------------------------------------------------

Authorization is required for this method.

Returns an ODM string representing the metadata of clinical view columns for this study and environment. Note that the
structure of clinical views are influenced by all the study versions active for a particular study and environment. If
a field is defined as numeric in one version and text in another, the most permissive type (in this case text) will
result in the structure of the clinical views.

Calls::

    https://{{ host }}/RaveWebServices/studies/{ project name }(environment_name)/datasets/metadata/regular/?{options}

Options:

+--------------------------------+-----------------------------------------------------------------------------------+
| Option                         | Description                                                                       |
+================================+===================================================================================+
| rawsuffix={suffix}             | e.g. .RAW means raw field definitions are suffixes with .RAW  ex. AE_STDT.RAW     |
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

Example::

    >>> from rwslib import RWSConnection
    >>> from rwslib.rws_requests.biostats_gateway import *
    >>> r = RWSConnection('https://innovate.mdsol.com', 'username', 'password')  #Authorization required
    >>> cv_metadata_odm = r.send_request(CVMetaDataRequest('SIMPLESTUDY', 'TEST', rawsuffix='RAW'))
    >>> print(cv_metadata_odm)
    <?xml version="1.0" encoding="utf-8"?><ODM FileType="Snapshot" Granularity="Metadata"
          CreationDateTime="2013-10-07T13:39:33.334-00:00"
          FileOID="0299d82e-8b76-4363-bd3e-2e6985999ce4" ODMVersion="1.3"
          xmlns="http://www.cdisc.org/ns/odm/v1.3">
          <Study OID="SIMPLESTUDY (TEST)">
              <GlobalVariables>
                  <StudyName>SIMPLESTUDY (TEST)</StudyName>
                  <StudyDescription></StudyDescription>
                  <ProtocolName>SIMPLESTUDY</ProtocolName>
              </GlobalVariables>
              <MetaDataVersion OID="2013-06-24T09:47:04.000-00:00" Name="2013-06-24T09:47:04.000-00:00">
                  <FormDef OID="ENROL" Name="V_SIMPLESTUDY_ENROL" Repeating="Yes">
                      <ItemGroupRef ItemGroupOID="ENROL_LOG_LINE" Mandatory="No" />
                  </FormDef>
                  <FormDef OID="VITAL" Name="V_SIMPLESTUDY_VITAL" Repeating="Yes">
                      <ItemGroupRef ItemGroupOID="VITAL_LOG_LINE" Mandatory="No" />
                  </FormDef>
                  <ItemGroupDef OID="ENROL_LOG_LINE" Name="ENROL_LOG_LINE" Repeating="Yes">
                      <ItemRef ItemOID="ENROL.SUBID" Mandatory="No" />
                      <ItemRef ItemOID="ENROL.BIRTHDT" Mandatory="No" />
                      <ItemRef ItemOID="ENROL.BIRTHDTRAW" Mandatory="No" />
                  </ItemGroupDef>
                  <ItemGroupDef OID="VITAL_LOG_LINE" Name="VITAL_LOG_LINE" Repeating="Yes">
                      <ItemRef ItemOID="VITAL.VDAT" Mandatory="No" />
                      <ItemRef ItemOID="VITAL.VDATRAW" Mandatory="No" />
                      <ItemRef ItemOID="VITAL.WEIGHT_KG" Mandatory="No" />
                      <ItemRef ItemOID="VITAL.WEIGHT_KGRAW" Mandatory="No" />
                      <ItemRef ItemOID="VITAL.HEIGHT_CM" Mandatory="No" />
                      <ItemRef ItemOID="VITAL.HEIGHT_CMRAW" Mandatory="No" />
                  </ItemGroupDef>
                  <ItemDef OID="ENROL.SUBID" Name="SUBID" DataType="text" Length="10" />
                  <ItemDef OID="ENROL.BIRTHDT" Name="BIRTHDT" DataType="datetime" />
                  <ItemDef OID="ENROL.BIRTHDTRAW" Name="BIRTHDTRAW" DataType="text" Length="11" />
                  <ItemDef OID="VITAL.VDAT" Name="VDAT" DataType="datetime" />
                  <ItemDef OID="VITAL.VDATRAW" Name="VDATRAW" DataType="text" Length="11" />
                  <ItemDef OID="VITAL.WEIGHT_KG" Name="WEIGHT_KG" DataType="float" Length="4" SignificantDigits="1" />
                  <ItemDef OID="VITAL.WEIGHT_KGRAW" Name="WEIGHT_KGRAW" DataType="text" Length="6" />
                  <ItemDef OID="VITAL.HEIGHT_CM" Name="HEIGHT_CM" DataType="float" Length="4" SignificantDigits="1" />
                  <ItemDef OID="VITAL.HEIGHT_CMRAW" Name="HEIGHT_CMRAW" DataType="text" Length="6" />
              </MetaDataVersion>
          </Study>
      </ODM>



.. _form_data_request:
.. index:: FormDataRequest

FormDataRequest(project_name, environment_name, dataset_type, form_oid)
-----------------------------------------------------------------------

Authorization is required for this method.

Retrieve data from Clinical Views for a single form. Data can be extracted from raw or regular views and can be formatted
in XML or CSV. If CSV in selected (the default) then the first line contains heading information and the last line of
the results contain the string "EOF". The EOF marker allows you to know that you received the full dataset before
any RWS timeout cut off the data stream.

Calls::

    https://{{ host }}/RaveWebServices/studies/{ project name }(environment_name)/datasets/{dataset_type}/{form_oid[.csv]}/?{options}

Note that dataset_type can be 'regular' or 'raw'. When called with a dataset type of "csv" a .csv is appended to the end
of the form oid in the calling URL. When left off, XML will be returned.

Options:

+--------------------------------+-----------------------------------------------------------------------------------+
| Option                         | Description                                                                       |
+================================+===================================================================================+
| start={ISO 8601 date}          | Request changes to this dataset since the start date. Note that CV's must be set  |
|                                | to *Include Inactive* for this option to work.                                    |
+--------------------------------+-----------------------------------------------------------------------------------+
| dataset_format={csv | xml}     | Determine the format returned by the request object. CSV is the default, but      |
|                                | can also return XML in a simple format.                                           |
+--------------------------------+-----------------------------------------------------------------------------------+

Example::

    >>> from rwslib import RWSConnection
    >>> from rwslib.rws_requests.biostats_gateway import FormDataRequest
    >>> r = RWSConnection('https://innovate.mdsol.com', 'username', 'password')  #Authorization required
    >>> vital_csv_data = r.send_request(FormDataRequest('SIMPLESTUDY', 'TEST', 'REGULAR', 'VITAL', dataset_format="csv"))
    >>> print(vital_csv_data)
    userid,projectid,project,studyid,environmentName,subjectId,StudySiteId,Subject,siteid,Site,SiteNumber,SiteGroup,instanceId,InstanceName,InstanceRepeatNumber,folderid,Folder,FolderName,FolderSeq,TargetDays,DataPageId,DataPageName,PageRepeatNumber,RecordDate,RecordId,recordposition,RecordActive,SaveTs,MinCreated,MaxUpdated,VDAT,VDAT_RAW,VDAT_INT,VDAT_YYYY,VDAT_MM,VDAT_DD,WEIGHT_KG,WEIGHT_KG_RAW,HEIGHT_CM,HEIGHT_CM_RAW
    "457","85","SIMPLESTUDY","95","TEST","32112","143","1","120","TESTSITE","TESTSITE","World","192310","Screening","0","5791","SCREEN","Screening","1.0","","662502","Vitals","0","","1346659","0","1","2013-06-24T09:52:52","2013-06-24T09:52:10","2013-06-24T09:52:10","2013-02-01T00:00:00","2013 Feb 01","2013-02-01T00:00:00","2013","2","1","132.0","132","174.5","174.5"
    "457","85","SIMPLESTUDY","95","TEST","32113","143","2","120","TESTSITE","TESTSITE","World","192311","Screening","0","5791","SCREEN","Screening","1.0","","662504","Vitals","0","","1346661","0","1","2013-06-24T09:52:52","2013-06-24T09:52:11","2013-06-24T09:52:11","2013-02-09T00:00:00","2013 Feb 09","2013-02-09T00:00:00","2013","2","9","82.5","82.5","173.0","173"
    "457","85","SIMPLESTUDY","95","TEST","32114","143","3","120","TESTSITE","TESTSITE","World","192312","Screening","0","5791","SCREEN","Screening","1.0","","662506","Vitals","0","","1346663","0","1","2013-06-24T09:52:52","2013-06-24T09:52:12","2013-06-24T09:52:12","2013-03-14T00:00:00","2013 Mar 14","2013-03-14T00:00:00","2013","3","14","95.2","95.2","152.0","152"
    "457","85","SIMPLESTUDY","95","TEST","32115","143","4","120","TESTSITE","TESTSITE","World","192313","Screening","0","5791","SCREEN","Screening","1.0","","662508","Vitals","0","","1346665","0","1","2013-06-24T09:52:52","2013-06-24T09:52:13","2013-06-24T09:52:13","2013-03-16T00:00:00","2013 Mar 16","2013-03-16T00:00:00","2013","3","16","67.7","67.7","178.0","178"
    "457","85","SIMPLESTUDY","95","TEST","32116","143","5","120","TESTSITE","TESTSITE","World","192314","Screening","0","5791","SCREEN","Screening","1.0","","662510","Vitals","0","","1346667","0","1","2013-06-24T09:52:52","2013-06-24T09:52:15","2013-06-24T09:52:15","2013-03-19T00:00:00","2013 Mar 19","2013-03-19T00:00:00","2013","3","19","81.5","81.5","158.0","158"
    "457","85","SIMPLESTUDY","95","TEST","32117","143","6","120","TESTSITE","TESTSITE","World","192315","Screening","0","5791","SCREEN","Screening","1.0","","662512","Vitals","0","","1346669","0","1","2013-06-24T09:52:52","2013-06-24T09:52:16","2013-06-24T09:52:16","2013-03-24T00:00:00","2013 Mar 24","2013-03-24T00:00:00","2013","3","24","73.9","73.9","180.5","180.5"
    "457","85","SIMPLESTUDY","95","TEST","32118","143","7","120","TESTSITE","TESTSITE","World","192316","Screening","0","5791","SCREEN","Screening","1.0","","662514","Vitals","0","","1346671","0","1","2013-06-24T09:52:52","2013-06-24T09:52:17","2013-06-24T09:52:17","2013-04-06T00:00:00","2013 Apr 06","2013-04-06T00:00:00","2013","4","6","","","175.0","175"
    "457","85","SIMPLESTUDY","95","TEST","32119","143","8","120","TESTSITE","TESTSITE","World","192317","Screening","0","5791","SCREEN","Screening","1.0","","662516","Vitals","0","","1346673","0","1","2013-06-24T09:52:52","2013-06-24T09:52:18","2013-06-24T09:52:18","2013-04-11T00:00:00","2013 Apr 11","2013-04-11T00:00:00","2013","4","11","114.8","114.8","190.0","190"
    "457","85","SIMPLESTUDY","95","TEST","32120","143","9","120","TESTSITE","TESTSITE","World","192318","Screening","0","5791","SCREEN","Screening","1.0","","662518","Vitals","0","","1346675","0","1","2013-06-24T09:52:52","2013-06-24T09:52:19","2013-06-24T09:52:19","2013-04-16T00:00:00","2013 Apr 16","2013-04-16T00:00:00","2013","4","16","68.8","68.8","184.0","184"
    "457","85","SIMPLESTUDY","95","TEST","32121","143","10","120","TESTSITE","TESTSITE","World","192319","Screening","0","5791","SCREEN","Screening","1.0","","662520","Vitals","0","","1346677","0","1","2013-06-24T09:52:52","2013-06-24T09:52:20","2013-06-24T09:52:20","2013-04-26T00:00:00","2013 Apr 26","2013-04-26T00:00:00","2013","4","26","92.7","92.7","175.0","175"
    EOF



.. _cv_meta_data_request:
.. index:: MetaDataRequest

MetaDataRequest()
-----------------

Authorization is required for this method.

Returns metadata for all Clinical Views that you have access to in XML or CSV format.

.. warning::

    This could be a large download if you have access to several studies or to a large study. It may be better to request
    data only for a single study using ProjectMetaDataRequest

Options:

+--------------------------------+-----------------------------------------------------------------------------------+
| Option                         | Description                                                                       |
+================================+===================================================================================+
| dataset_format={csv | xml}     | Determine the format returned by the request object. CSV is the default, but      |
|                                | can also return XML in a simple format.                                           |
+--------------------------------+-----------------------------------------------------------------------------------+

Calls::

    https://{{ host }}/RaveWebServices/datasets/ClinicalViewMetadata[.csv]


Example::

    >>> from rwslib import RWSConnection
    >>> from rwslib.rws_requests.biostats_gateway import MetaDataRequest
    >>> r = RWSConnection('https://innovate.mdsol.com', 'username', 'password')  #Authorization required
    >>> all_csv_meta = rave.send_request(MetaDataRequest(dataset_format='xml'))
    >>> print(all_csv_meta)
    <?xml version="1.0" encoding="UTF-8"?>
    <datasets>
        <dataset>
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_ENROL" ordinal="1" varname="userid" vartype="num" varlength="8" varformat="10." varlabel="Internal id for the user" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_ENROL" ordinal="2" varname="projectid" vartype="num" varlength="8" varformat="10." varlabel="projectid" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_ENROL" ordinal="3" varname="project" vartype="char" varlength="255" varformat="$255." varlabel="project" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_ENROL" ordinal="4" varname="studyid" vartype="num" varlength="8" varformat="10." varlabel="Internal id for the study" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_ENROL" ordinal="5" varname="environmentName" vartype="char" varlength="20" varformat="$20." varlabel="Environment" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_ENROL" ordinal="6" varname="subjectId" vartype="num" varlength="8" varformat="10." varlabel="Internal id for the subject" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_ENROL" ordinal="7" varname="StudySiteId" vartype="num" varlength="8" varformat="10." varlabel="Internal id for study site" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_ENROL" ordinal="8" varname="Subject" vartype="char" varlength="50" varformat="$50." varlabel="Subject name or identifier" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_ENROL" ordinal="9" varname="siteid" vartype="num" varlength="8" varformat="10." varlabel="Internal id for the site" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_ENROL" ordinal="10" varname="Site" vartype="char" varlength="255" varformat="$255." varlabel="Site name" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_ENROL" ordinal="11" varname="SiteNumber" vartype="char" varlength="50" varformat="$50." varlabel="SiteNumber" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_ENROL" ordinal="12" varname="SiteGroup" vartype="char" varlength="40" varformat="$40." varlabel="SiteGroup" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_ENROL" ordinal="13" varname="instanceId" vartype="num" varlength="8" varformat="10." varlabel="Internal id for the instance" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_ENROL" ordinal="14" varname="InstanceName" vartype="char" varlength="255" varformat="$255." varlabel="Folder instance name" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_ENROL" ordinal="15" varname="InstanceRepeatNumber" vartype="num" varlength="8" varformat="10." varlabel="InstanceRepeatNumber" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_ENROL" ordinal="16" varname="folderid" vartype="num" varlength="8" varformat="10." varlabel="Internal id for the folder" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_ENROL" ordinal="17" varname="Folder" vartype="char" varlength="50" varformat="$50." varlabel="Folder OID" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_ENROL" ordinal="18" varname="FolderName" vartype="char" varlength="255" varformat="$255." varlabel="Folder name" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_ENROL" ordinal="19" varname="FolderSeq" vartype="num" varlength="8" varformat="12.1" varlabel="Folder sequence number" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_ENROL" ordinal="20" varname="TargetDays" vartype="num" varlength="8" varformat="10." varlabel="Target days from study start" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_ENROL" ordinal="21" varname="DataPageId" vartype="num" varlength="8" varformat="10." varlabel="Internal id for data page" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_ENROL" ordinal="22" varname="DataPageName" vartype="char" varlength="255" varformat="$255." varlabel="eCRF page name" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_ENROL" ordinal="23" varname="PageRepeatNumber" vartype="num" varlength="8" varformat="10." varlabel="Sequence number of eCRF page in folder" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_ENROL" ordinal="24" varname="RecordDate" vartype="num" varlength="8" varformat="datetime22.3" varlabel="Clinical date of record (ex: visit date)" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_ENROL" ordinal="25" varname="RecordId" vartype="num" varlength="8" varformat="10." varlabel="Internal id for the record" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_ENROL" ordinal="26" varname="recordposition" vartype="num" varlength="8" varformat="10." varlabel="Record number" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_ENROL" ordinal="27" varname="RecordActive" vartype="num" varlength="8" varformat="1." varlabel="Is record active" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_ENROL" ordinal="28" varname="SaveTs" vartype="num" varlength="8" varformat="datetime22.3" varlabel="Timestamp of last save in clinical views" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_ENROL" ordinal="29" varname="MinCreated" vartype="num" varlength="8" varformat="datetime22.3" varlabel="Earliest data creation time" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_ENROL" ordinal="30" varname="MaxUpdated" vartype="num" varlength="8" varformat="datetime22.3" varlabel="Latest data update time" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_ENROL" ordinal="31" varname="SUBID" vartype="char" varlength="10" varformat="$10." varlabel="SUBID" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_ENROL" ordinal="32" varname="BIRTHDT" vartype="num" varlength="8" varformat="datetime22.3" varlabel="BIRTHDT" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_ENROL" ordinal="33" varname="BIRTHDT_RAW" vartype="char" varlength="11" varformat="$11." varlabel="BIRTHDT(Character)" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_ENROL" ordinal="34" varname="BIRTHDT_INT" vartype="num" varlength="8" varformat="datetime22.3" varlabel="BIRTHDTInterpolated" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_ENROL" ordinal="35" varname="BIRTHDT_YYYY" vartype="num" varlength="8" varformat="4." varlabel="BIRTHDTYear" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_ENROL" ordinal="36" varname="BIRTHDT_MM" vartype="num" varlength="8" varformat="2." varlabel="BIRTHDTMonth" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_ENROL" ordinal="37" varname="BIRTHDT_DD" vartype="num" varlength="8" varformat="2." varlabel="BIRTHDTDay" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_ENROL_RAW" ordinal="1" varname="userid" vartype="num" varlength="8" varformat="10." varlabel="Internal id for the user" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_ENROL_RAW" ordinal="2" varname="projectid" vartype="num" varlength="8" varformat="10." varlabel="projectid" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_ENROL_RAW" ordinal="3" varname="project" vartype="char" varlength="255" varformat="$255." varlabel="project" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_ENROL_RAW" ordinal="4" varname="studyid" vartype="num" varlength="8" varformat="10." varlabel="Internal id for the study" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_ENROL_RAW" ordinal="5" varname="environmentName" vartype="char" varlength="20" varformat="$20." varlabel="Environment" />
            ....
        </dataset>
    </datasets>


.. _cv_project_meta_data_request:
.. index:: ProjectMetaDataRequest

ProjectMetaDataRequest(project_name)
------------------------------------

Authorization is required for this method.

Returns metadata for all Clinical Views related to a single project  in XML or CSV format.

Options:

+--------------------------------+-----------------------------------------------------------------------------------+
| Option                         | Description                                                                       |
+================================+===================================================================================+
| dataset_format={csv | xml}     | Determine the format returned by the request object. CSV is the default, but      |
|                                | can also return XML in a simple format.                                           |
+--------------------------------+-----------------------------------------------------------------------------------+


Calls::

    https://{{ host }}/RaveWebServices/datasets/ClinicalViewMetadata[.csv]?ProjectName={project_name}


Example::

    >>> from rwslib import RWSConnection
    >>> from rwslib.rws_requests.biostats_gateway import MetaDataRequest
    >>> r = RWSConnection('https://innovate.mdsol.com', 'username', 'password')  #Authorization required
    >>> simplestudy_csv_meta = r.send_request(ProjectMetaDataRequest('SIMPLESTUDY'))
    >>> print(simplestudy_csv_meta)
    projectname,viewname,ordinal,varname,vartype,varlength,varformat,varlabel
    "SIMPLESTUDY","V_SIMPLESTUDY_ENROL","1","userid","num","8","10.","Internal id for the user"
    "SIMPLESTUDY","V_SIMPLESTUDY_ENROL","2","projectid","num","8","10.","projectid"
    "SIMPLESTUDY","V_SIMPLESTUDY_ENROL","3","project","char","255","$255.","project"
    "SIMPLESTUDY","V_SIMPLESTUDY_ENROL","4","studyid","num","8","10.","Internal id for the study"
    "SIMPLESTUDY","V_SIMPLESTUDY_ENROL","5","environmentName","char","20","$20.","Environment"
    "SIMPLESTUDY","V_SIMPLESTUDY_ENROL","6","subjectId","num","8","10.","Internal id for the subject"
    "SIMPLESTUDY","V_SIMPLESTUDY_ENROL","7","StudySiteId","num","8","10.","Internal id for study site"
    "SIMPLESTUDY","V_SIMPLESTUDY_ENROL","8","Subject","char","50","$50.","Subject name or identifier"
    "SIMPLESTUDY","V_SIMPLESTUDY_ENROL","9","siteid","num","8","10.","Internal id for the site"
    "SIMPLESTUDY","V_SIMPLESTUDY_ENROL","10","Site","char","255","$255.","Site name"
    "SIMPLESTUDY","V_SIMPLESTUDY_ENROL","11","SiteNumber","char","50","$50.","SiteNumber"
    "SIMPLESTUDY","V_SIMPLESTUDY_ENROL","12","SiteGroup","char","40","$40.","SiteGroup"
    "SIMPLESTUDY","V_SIMPLESTUDY_ENROL","13","instanceId","num","8","10.","Internal id for the instance"
    "SIMPLESTUDY","V_SIMPLESTUDY_ENROL","14","InstanceName","char","255","$255.","Folder instance name"
    "SIMPLESTUDY","V_SIMPLESTUDY_ENROL","15","InstanceRepeatNumber","num","8","10.","InstanceRepeatNumber"
    "SIMPLESTUDY","V_SIMPLESTUDY_ENROL","16","folderid","num","8","10.","Internal id for the folder"
    "SIMPLESTUDY","V_SIMPLESTUDY_ENROL","17","Folder","char","50","$50.","Folder OID"
    "SIMPLESTUDY","V_SIMPLESTUDY_ENROL","18","FolderName","char","255","$255.","Folder name"
    "SIMPLESTUDY","V_SIMPLESTUDY_ENROL","19","FolderSeq","num","8","12.1","Folder sequence number"
    "SIMPLESTUDY","V_SIMPLESTUDY_ENROL","20","TargetDays","num","8","10.","Target days from study start"
    "SIMPLESTUDY","V_SIMPLESTUDY_ENROL","21","DataPageId","num","8","10.","Internal id for data page"
    "SIMPLESTUDY","V_SIMPLESTUDY_ENROL","22","DataPageName","char","255","$255.","eCRF page name"
    "SIMPLESTUDY","V_SIMPLESTUDY_ENROL","23","PageRepeatNumber","num","8","10.","Sequence number of eCRF page in folder"
    "SIMPLESTUDY","V_SIMPLESTUDY_ENROL","24","RecordDate","num","8","datetime22.3","Clinical date of record (ex: visit date)"
    "SIMPLESTUDY","V_SIMPLESTUDY_ENROL","25","RecordId","num","8","10.","Internal id for the record"
    "SIMPLESTUDY","V_SIMPLESTUDY_ENROL","26","recordposition","num","8","10.","Record number"
    "SIMPLESTUDY","V_SIMPLESTUDY_ENROL","27","RecordActive","num","8","1.","Is record active"
    ...many more lines
    EOF



.. _cv_view_meta_data_request:
.. index:: ViewMetaDataRequest

ViewMetaDataRequest(view_name)
------------------------------

Authorization is required for this method.

Returns metadata for a single clinical view in XML or CSV format. A clinical view name will have the format::

    V_{projectname}_{formoid}

for standard views and::

    prod.V_{projectname}_{formoid}

for production-only views if these are set to be created by the Rave Clinical View Settings.

Options:

+--------------------------------+-----------------------------------------------------------------------------------+
| Option                         | Description                                                                       |
+================================+===================================================================================+
| dataset_format={csv | xml}     | Determine the format returned by the request object. CSV is the default, but      |
|                                | can also return XML in a simple format.                                           |
+--------------------------------+-----------------------------------------------------------------------------------+

Calls::

    https://{{ host }}/RaveWebServices/datasets/ClinicalViewMetadata[.csv]?ViewName={view_name}


Example::

    >>> from rwslib import RWSConnection
    >>> from rwslib.rws_requests.biostats_gateway import MetaDataRequest
    >>> r = RWSConnection('https://innovate.mdsol.com', 'username', 'password')  #Authorization required
    >>> ss_vital_meta = r.send_request(ViewMetaDataRequest("V_SIMPLESTUDY_VITAL", dataset_format='xml'))
    >>> print(ss_vital_meta)
    <?xml version="1.0" encoding="UTF-8"?>
    <datasets>
        <dataset>
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_VITAL" ordinal="1" varname="userid" vartype="num" varlength="8" varformat="10." varlabel="Internal id for the user" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_VITAL" ordinal="2" varname="projectid" vartype="num" varlength="8" varformat="10." varlabel="projectid" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_VITAL" ordinal="3" varname="project" vartype="char" varlength="255" varformat="$255." varlabel="project" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_VITAL" ordinal="4" varname="studyid" vartype="num" varlength="8" varformat="10." varlabel="Internal id for the study" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_VITAL" ordinal="5" varname="environmentName" vartype="char" varlength="20" varformat="$20." varlabel="Environment" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_VITAL" ordinal="6" varname="subjectId" vartype="num" varlength="8" varformat="10." varlabel="Internal id for the subject" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_VITAL" ordinal="7" varname="StudySiteId" vartype="num" varlength="8" varformat="10." varlabel="Internal id for study site" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_VITAL" ordinal="8" varname="Subject" vartype="char" varlength="50" varformat="$50." varlabel="Subject name or identifier" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_VITAL" ordinal="9" varname="siteid" vartype="num" varlength="8" varformat="10." varlabel="Internal id for the site" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_VITAL" ordinal="10" varname="Site" vartype="char" varlength="255" varformat="$255." varlabel="Site name" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_VITAL" ordinal="11" varname="SiteNumber" vartype="char" varlength="50" varformat="$50." varlabel="SiteNumber" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_VITAL" ordinal="12" varname="SiteGroup" vartype="char" varlength="40" varformat="$40." varlabel="SiteGroup" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_VITAL" ordinal="13" varname="instanceId" vartype="num" varlength="8" varformat="10." varlabel="Internal id for the instance" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_VITAL" ordinal="14" varname="InstanceName" vartype="char" varlength="255" varformat="$255." varlabel="Folder instance name" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_VITAL" ordinal="15" varname="InstanceRepeatNumber" vartype="num" varlength="8" varformat="10." varlabel="InstanceRepeatNumber" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_VITAL" ordinal="16" varname="folderid" vartype="num" varlength="8" varformat="10." varlabel="Internal id for the folder" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_VITAL" ordinal="17" varname="Folder" vartype="char" varlength="50" varformat="$50." varlabel="Folder OID" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_VITAL" ordinal="18" varname="FolderName" vartype="char" varlength="255" varformat="$255." varlabel="Folder name" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_VITAL" ordinal="19" varname="FolderSeq" vartype="num" varlength="8" varformat="12.1" varlabel="Folder sequence number" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_VITAL" ordinal="20" varname="TargetDays" vartype="num" varlength="8" varformat="10." varlabel="Target days from study start" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_VITAL" ordinal="21" varname="DataPageId" vartype="num" varlength="8" varformat="10." varlabel="Internal id for data page" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_VITAL" ordinal="22" varname="DataPageName" vartype="char" varlength="255" varformat="$255." varlabel="eCRF page name" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_VITAL" ordinal="23" varname="PageRepeatNumber" vartype="num" varlength="8" varformat="10." varlabel="Sequence number of eCRF page in folder" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_VITAL" ordinal="24" varname="RecordDate" vartype="num" varlength="8" varformat="datetime22.3" varlabel="Clinical date of record (ex: visit date)" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_VITAL" ordinal="25" varname="RecordId" vartype="num" varlength="8" varformat="10." varlabel="Internal id for the record" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_VITAL" ordinal="26" varname="recordposition" vartype="num" varlength="8" varformat="10." varlabel="Record number" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_VITAL" ordinal="27" varname="RecordActive" vartype="num" varlength="8" varformat="1." varlabel="Is record active" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_VITAL" ordinal="28" varname="SaveTs" vartype="num" varlength="8" varformat="datetime22.3" varlabel="Timestamp of last save in clinical views" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_VITAL" ordinal="29" varname="MinCreated" vartype="num" varlength="8" varformat="datetime22.3" varlabel="Earliest data creation time" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_VITAL" ordinal="30" varname="MaxUpdated" vartype="num" varlength="8" varformat="datetime22.3" varlabel="Latest data update time" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_VITAL" ordinal="31" varname="VDAT" vartype="num" varlength="8" varformat="datetime22.3" varlabel="VDAT" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_VITAL" ordinal="32" varname="VDAT_RAW" vartype="char" varlength="11" varformat="$11." varlabel="VDAT(Character)" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_VITAL" ordinal="33" varname="VDAT_INT" vartype="num" varlength="8" varformat="datetime22.3" varlabel="VDATInterpolated" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_VITAL" ordinal="34" varname="VDAT_YYYY" vartype="num" varlength="8" varformat="4." varlabel="VDATYear" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_VITAL" ordinal="35" varname="VDAT_MM" vartype="num" varlength="8" varformat="2." varlabel="VDATMonth" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_VITAL" ordinal="36" varname="VDAT_DD" vartype="num" varlength="8" varformat="2." varlabel="VDATDay" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_VITAL" ordinal="37" varname="WEIGHT_KG" vartype="num" varlength="8" varformat="5.1" varlabel="WEIGHT_KG" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_VITAL" ordinal="38" varname="WEIGHT_KG_RAW" vartype="char" varlength="6" varformat="$6." varlabel="WEIGHT_KG(Character)" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_VITAL" ordinal="39" varname="HEIGHT_CM" vartype="num" varlength="8" varformat="5.1" varlabel="HEIGHT_CM" />
            <record projectname="SIMPLESTUDY" viewname="V_SIMPLESTUDY_VITAL" ordinal="40" varname="HEIGHT_CM_RAW" vartype="char" varlength="6" varformat="$6." varlabel="HEIGHT_CM(Character)" />
        </dataset>
    </datasets>



.. _comment_data_request:
.. index:: CommentDataRequest

CommentDataRequest(project_name, environment_name)
---------------------------------------------------

Provides all comments from Rave in CSV or XML format.

Options:

+--------------------------------+-----------------------------------------------------------------------------------+
| Option                         | Description                                                                       |
+================================+===================================================================================+
| dataset_format={csv | xml}     | Determine the format returned by the request object. CSV is the default, but      |
|                                | can also return XML in a simple format.                                           |
+--------------------------------+-----------------------------------------------------------------------------------+

Calls::

    https://{{ host }}/RaveWebServices/datasets/SDTMComments[.csv]?studyid={project_name}({environment_name})


Example::

    >>> from rwslib import RWSConnection
    >>> from rwslib.rws_requests.biostats_gateway import CommentDataRequest
    >>> r = RWSConnection('https://innovate.mdsol.com', 'username', 'password')  #Authorization required
    >>> r.send_request(CommentDataRequest("SIMPLESTUDY", "TEST"))
    ProjectName,EnvironmentName,SiteNumber,SubjectName,SubjectID,InstanceName,InstanceID,InstanceRepeatNumber,DataPageName,DatapageID,PageRepeatNumber,Datapointid,FormOID,RecordID,RecordPosition,FieldOID,Text,Updated,DataActive,RecordActive
    "SIMPLESTUDY","TEST","TESTSITE","3","32114","","","","Enrol","662507","0","2289018","ENROL","1346664","0","BIRTHDT","This subject was late","10/7/2013 3:50:18 PM","True","True"
    "SIMPLESTUDY","TEST","TESTSITE","8","32119","Screening","192317","0","Vitals","662516","0","2289046","VITAL","1346673","0","HEIGHT_CM","This weight was not taken during the visit. It was called in by the subject.","10/7/2013 3:50:46 PM","True","True"
    EOF



.. _protocol_deviation_request:
.. index:: ProtocolDeviationsRequest

ProtocolDeviationsRequest(project_name, environment_name)
---------------------------------------------------------

Provides all ProtocolDeviations from Rave in CSV or XML format.

Options:

+--------------------------------+-----------------------------------------------------------------------------------+
| Option                         | Description                                                                       |
+================================+===================================================================================+
| dataset_format={csv | xml}     | Determine the format returned by the request object. CSV is the default, but      |
|                                | can also return XML in a simple format.                                           |
+--------------------------------+-----------------------------------------------------------------------------------+

Calls::

    https://{{ host }}/RaveWebServices/datasets/SDTMProtocolDeviations[.csv]?studyid={project_name}({environment_name})


Example::

    >>> from rwslib import RWSConnection
    >>> from rwslib.rws_requests.biostats_gateway import ProtocolDeviationsRequest
    >>> r = RWSConnection('https://innovate.mdsol.com', 'username', 'password')  #Authorization required
    >>> r.send_request(ProtocolDeviationsRequest("SIMPLESTUDY", "TEST"))
    ProjectName,EnvironmentName,SiteNumber,SubjectName,SubjectID,InstanceName,InstanceID,InstanceRepeatNumber,DataPageName,DatapageID,PageRepeatNumber,Datapointid,FormOID,RecordID,RecordPosition,FieldOID,Text,Updated,PDClass,PDCode,DataActive,RecordActive
    "SIMPLESTUDY","TEST","TESTSITE","8","32119","","","","Enrol","662517","0","2289043","ENROL","1346674","0","BIRTHDT","Inc/Exc criteria do not seem to be met for this subject. Too young.","10/7/2013 3:16:29 PM","Incl/Excl Criteria not met","Deviation","True","True"
    "SIMPLESTUDY","TEST","TESTSITE","8","32119","Screening","192317","0","Vitals","662516","0","2289046","VITAL","1346673","0","HEIGHT_CM","Height/Weight outside range!","10/7/2013 3:21:01 PM","Incl/Excl Criteria not met","violation","True","True"
    EOF






.. _data_dictionaries_request:
.. index:: DataDictionariesRequest

DataDictionariesRequest(project_name, environment_name)
-------------------------------------------------------

Provides all Data Dictionaries from a study in CSV or XML format.

Options:

+--------------------------------+-----------------------------------------------------------------------------------+
| Option                         | Description                                                                       |
+================================+===================================================================================+
| dataset_format={csv | xml}     | Determine the format returned by the request object. CSV is the default, but      |
|                                | can also return XML in a simple format.                                           |
+--------------------------------+-----------------------------------------------------------------------------------+

Calls::

    https://{{ host }}/RaveWebServices/datasets/SDTMDataDictionaries[.csv]?studyid={project_name}({environment_name})


Example::

    >>> from rwslib import RWSConnection
    >>> from rwslib.rws_requests.biostats_gateway import DataDictionariesRequest
    >>> r = RWSConnection('https://innovate.mdsol.com', 'username', 'password')  #Authorization required
    >>> r.send_request(DataDictionariesRequest("CDASH Forms", "PROD", dataset_format="xml"))
    <?xml version="1.0" encoding="UTF-8"?>
    <datasets>
        <dataset>
            <record studyid="CDASH Forms(Prod)" ProjectName="CDASH Forms" EnvironmentName="Prod" CRFVersionID="18" DictionaryName="AE Action Taken" CodedValue="8" UserValue="Other (specify)" userid="457" />
            <record studyid="CDASH Forms(Prod)" ProjectName="CDASH Forms" EnvironmentName="Prod" CRFVersionID="18" DictionaryName="AE Action Taken" CodedValue="7" UserValue="Unknown" userid="457" />
            <record studyid="CDASH Forms(Prod)" ProjectName="CDASH Forms" EnvironmentName="Prod" CRFVersionID="18" DictionaryName="AE Action Taken" CodedValue="6" UserValue="Not Applicable" userid="457" />
            <record studyid="CDASH Forms(Prod)" ProjectName="CDASH Forms" EnvironmentName="Prod" CRFVersionID="18" DictionaryName="AE Action Taken" CodedValue="5" UserValue="Drug Withdrawn" userid="457" />
            <record studyid="CDASH Forms(Prod)" ProjectName="CDASH Forms" EnvironmentName="Prod" CRFVersionID="18" DictionaryName="AE Action Taken" CodedValue="4" UserValue="Drug Interrupted" userid="457" />
            <record studyid="CDASH Forms(Prod)" ProjectName="CDASH Forms" EnvironmentName="Prod" CRFVersionID="18" DictionaryName="AE Action Taken" CodedValue="3" UserValue="Dose Reduced" userid="457" />
            <record studyid="CDASH Forms(Prod)" ProjectName="CDASH Forms" EnvironmentName="Prod" CRFVersionID="18" DictionaryName="AE Action Taken" CodedValue="2" UserValue="Dose not Changed" userid="457" />
            <record studyid="CDASH Forms(Prod)" ProjectName="CDASH Forms" EnvironmentName="Prod" CRFVersionID="18" DictionaryName="AE Action Taken" CodedValue="1" UserValue="Dose Increased" userid="457" />
            <record studyid="CDASH Forms(Prod)" ProjectName="CDASH Forms" EnvironmentName="Prod" CRFVersionID="18" DictionaryName="AE Severity" CodedValue="3" UserValue="Severe" userid="457" />
            <record studyid="CDASH Forms(Prod)" ProjectName="CDASH Forms" EnvironmentName="Prod" CRFVersionID="18" DictionaryName="AE Severity" CodedValue="2" UserValue="Moderate" userid="457" />
            <record studyid="CDASH Forms(Prod)" ProjectName="CDASH Forms" EnvironmentName="Prod" CRFVersionID="18" DictionaryName="AE Severity" CodedValue="1" UserValue="Mild" userid="457" />
            ....
        </dataset>
    </datasets>