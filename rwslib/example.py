from rwslib import RWSConnection
from rwslib.rws_requests import *
from rwslib.rws_requests.odm_adapter import *
from rwslib.rws_requests.biostats_gateway import *

if __name__ == '__main__':

    from _settings import accounts

    # Accounts is a dict of dicts like
    # accounts = {'innovate' : {'username': 'username',
    #                          'password':'password'},
    #             'otherurl' : {'username': 'username',
    #                          'password':'password'},
    #            }

    acc = accounts['innovate']
    rave = RWSConnection('innovate', acc['username'], acc['password'])

    print(rave.send_request(VersionRequest(), retries=3))

    print(rave.send_request(BuildVersionRequest()))
    print(rave.send_request(DiagnosticsRequest()))
    print(rave.send_request(CacheFlushRequest()).istransactionsuccessful)

    print("Clinical studies request")
    studies = rave.send_request(ClinicalStudiesRequest(), timeout=60)
    print(len(studies))
    print(rave.last_result.url)
    print(rave.last_result.text)
    print(rave.request_time)

    print("Metadata studies request")
    m_studies = rave.send_request(MetadataStudiesRequest())
    print(len(m_studies))
    print(rave.last_result.text)

    print("Study %s Drafts" % 'Mediflex')
    drafts = rave.send_request(StudyDraftsRequest('Mediflex'))
    for draft in drafts:
        print(draft.oid.ljust(20), draft.name)

    print("Study %s Versions" % 'Mediflex')
    versions = rave.send_request(StudyVersionsRequest('Mediflex'))
    for version in versions:
        print(version.oid.ljust(20), version.name)

    sv1 = versions[0]
    version_odm = rave.send_request(StudyVersionRequest('Mediflex', sv1.oid))
    print("Mediflex Study version OID = %s %s" % (str(sv1.oid), version_odm[0:50] + '...',))

    gl_studies = rave.send_request(GlobalLibrariesRequest())
    print("There are %d global libaries" % len(gl_studies))
    for study in gl_studies:
        print(study.studyname)
    gl_1 = gl_studies[0]

    gl_drafts = rave.send_request(GlobalLibraryDraftsRequest(gl_1.studyname))
    print("There are %d drafts for GlobalLibrary %s" % (len(gl_drafts), gl_1.studyname,))

    gl_versions = rave.send_request(GlobalLibraryVersionsRequest(gl_1.studyname))
    print("There are %d versions for GlobalLibrary %s" % (len(gl_versions), gl_1.studyname,))

    glv1 = gl_versions[0]
    gl1_version_odm = rave.send_request(GlobalLibraryVersionRequest(gl_1.studyname, glv1.oid))
    print("Global library 1, OID = %s %s" % (str(glv1.oid), gl1_version_odm[0:50] + '...',))

    try:
        subs = rave.send_request(StudySubjectsRequest('SimpleStudy', 'PROD', status=True))
        print(rave.last_result.url)
    except:
        print(rave.last_result.url)
        raise
    print("SimpleStudy(PROD) has %d subjects " % len(subs))

    try:
        subs = rave.send_request(StudySubjectsRequest('SimpleStudy', 'TEST'))
    except:
        print(rave.last_result.url)
        raise
    print("SimpleStudy(TEST) has %d subjects " % len(subs))

    data = u"""<?xml version="1.0" encoding="utf-8" ?>
<ODM CreationDateTime="2013-06-17T17:03:29" FileOID="3b9fea8b-e825-4e5f-bdc8-1464bdd7a664" FileType="Transactional" ODMVersion="1.3" xmlns="http://www.cdisc.org/ns/odm/v1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata">
  <ClinicalData MetaDataVersionOID="DEFAULT" StudyOID="SIMPLESTUDY (TEST)">
    <SubjectData SubjectKey="012" TransactionType="Insert">
      <SiteRef LocationOID="TESTSITE" />
      <StudyEventData StudyEventOID="SUBJECT" TransactionType="Update">
        <FormData FormOID="ENROL">
          <ItemGroupData ItemGroupOID="ENROL">
            <ItemData ItemOID="SUBID" Value="012" />
            <ItemData ItemOID="BIRTHDT" Value="1973 Jun 26" />
          </ItemGroupData>
        </FormData>
      </StudyEventData>
    </SubjectData>
  </ClinicalData>
</ODM>"""

    # Post data example
    res = rave.send_request(PostDataRequest(data))
    print(res)

    data = """<ODM FileType="Snapshot" Granularity="Metadata" CreationDateTime="2013-06-18T15:09:54.843-00:00" FileOID="82370e27-a6a5-41dc-8c07-829e489823df" ODMVersion="1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata" xmlns="http://www.cdisc.org/ns/odm/v1.3">
  <Study OID="SIMPLESTUDY">
    <GlobalVariables>
      <StudyName>SIMPLESTUDY</StudyName>
      <StudyDescription></StudyDescription>
      <ProtocolName>SIMPLESTUDY</ProtocolName>
    </GlobalVariables>
    <BasicDefinitions/>
    <MetaDataVersion OID="1" Name="Version 5" mdsol:PrimaryFormOID="ENROL" mdsol:DefaultMatrixOID="DEFAULT" mdsol:SignaturePrompt="Sign this please.">
      <Protocol>
        <StudyEventRef StudyEventOID="SCREEN" OrderNumber="1" Mandatory="No" />
      </Protocol>
      <StudyEventDef OID="SCREEN" Name="Screening" Type="Common" Repeating="Yes" mdsol:OrderNumber="1">
        <FormRef FormOID="VITAL" OrderNumber="2" Mandatory="No" />
      </StudyEventDef>
      <FormDef OID="ENROL" Repeating="No" Name="Enrol" mdsol:OrderNumber="1" mdsol:ConfirmationStyle="None">
        <ItemGroupRef ItemGroupOID="ENROL" Mandatory="Yes" />
      </FormDef>
      <FormDef OID="VITAL" Repeating="No" Name="Vitals" mdsol:OrderNumber="2">
        <ItemGroupRef ItemGroupOID="VITAL" Mandatory="Yes" />
      </FormDef>
      <ItemGroupDef OID="ENROL" Name="ENROL" Repeating="No">
        <ItemRef ItemOID="SUBID" OrderNumber="1" Mandatory="No" />
        <ItemRef ItemOID="BIRTHDT" OrderNumber="2" Mandatory="No" />
      </ItemGroupDef>
      <ItemGroupDef OID="VITAL" Name="VITAL" Repeating="No">
        <ItemRef ItemOID="VDAT" OrderNumber="1" Mandatory="No" />
        <ItemRef ItemOID="WEIGHT_KG" OrderNumber="2" Mandatory="No" />
        <ItemRef ItemOID="HEIGHT_CM" OrderNumber="3" Mandatory="No" />
      </ItemGroupDef>
      <ItemDef OID="SUBID" Name="SUBID" DataType="text" Length="10" mdsol:ControlType="Text">
        <Question>
          <TranslatedText xml:lang="en">Subject ID</TranslatedText>
        </Question>
      </ItemDef>

      <ItemDef OID="VDAT" Name="VDAT" DataType="date" mdsol:DateTimeFormat="yyyy MMM dd" mdsol:ControlType="DateTime">
        <Question>
          <TranslatedText xml:lang="en">Visit Date</TranslatedText>
        </Question>
      </ItemDef>
      <ItemDef OID="BIRTHDT" Name="BIRTHDT" DataType="date" mdsol:DateTimeFormat="yyyy MMM dd" mdsol:ControlType="DateTime">
        <Question>
          <TranslatedText xml:lang="en">Date of Birth</TranslatedText>
        </Question>
      </ItemDef>
      <ItemDef OID="WEIGHT_KG" Name="WEIGHT_KG" DataType="float" Length="4" SignificantDigits="1" mdsol:ControlType="Text">
        <Question>
          <TranslatedText xml:lang="en">Weight</TranslatedText>
        </Question>
      </ItemDef>
      <ItemDef OID="HEIGHT_CM" Name="HEIGHT_CM" DataType="float" Length="4" SignificantDigits="1" mdsol:ControlType="Text">
        <Question>
          <TranslatedText xml:lang="en">Height</TranslatedText>
        </Question>
      </ItemDef>
    </MetaDataVersion>
  </Study>
</ODM>"""

    try:
        res = rave.send_request(PostMetadataRequest("SIMPLESTUDY", data))
    except:
        print(rave.last_result.url)
        raise
    print(res)

    print("Study")
    study = rave.send_request(StudyDatasetRequest('SIMPLESTUDY', 'TEST', formoid="VITAL"))
    print(study)

    print("Version")
    version = rave.send_request(VersionDatasetRequest('SIMPLESTUDY', 'TEST', 1128, formoid="VITAL"))
    print(version)

    print("Subject")
    subject = rave.send_request(SubjectDatasetRequest('SIMPLESTUDY', 'TEST', '1', formoid="VITAL"))
    print(subject)

    cv_metadata_odm = rave.send_request(CVMetaDataRequest('SIMPLESTUDY', 'TEST', rawsuffix='RAW'))
    print("CV Metadata")
    print(cv_metadata_odm)

    print("CSV Data for VITAL")
    vital_csv_data = rave.send_request(FormDataRequest('SIMPLESTUDY', 'TEST', 'REGULAR', 'VITAL', dataset_format="csv"))
    print(vital_csv_data)

    print("All CSV Metadata")
    all_csv_meta = rave.send_request(MetaDataRequest(dataset_format='csv'))
    print(all_csv_meta)

    print("SIMPLESTUDY Project Metadata")
    proj_csv_meta = rave.send_request(ProjectMetaDataRequest('SIMPLESTUDY'))
    print(proj_csv_meta)

    print("SIMPLESTUDY VITALS View Metadata")
    view_csv_meta = rave.send_request(ViewMetaDataRequest("V_SIMPLESTUDY_VITAL", dataset_format='xml'))
    print(view_csv_meta)

    print("SIMPLESTUDY(TEST) Comments")
    com_csv = rave.send_request(CommentDataRequest("SIMPLESTUDY", "TEST"))
    print(com_csv)

    print("SIMPLESTUDY(TEST) Deviations")
    dev_csv = rave.send_request(ProtocolDeviationsRequest("SIMPLESTUDY", "TEST"))
    print(dev_csv)

    print("CDASH Forms(PROD) Data Dictionaries")
    dd_csv = rave.send_request(DataDictionariesRequest("CDASH Forms", "PROD", dataset_format="xml"))
    print(dd_csv)

    print("First 100 rows of Audits for SIMPLESTUDY TEST")
    audits = rave.send_request(AuditRecordsRequest('SIMPLESTUDY', 'TEST'))
    print(rave.last_result.headers)  # Get headers, next and last entries?
    print(audits)

    print("Folder Definitions for SIMPLESTUDY")
    version_folders = rave.send_request(VersionFoldersRequest('SIMPLESTUDY', 'TEST'))
    print(version_folders)

    print("Signature Definitions for SIMPLESTUDY")
    sigdefs = rave.send_request(SignatureDefinitionsRequest('SIMPLESTUDY'))
    print(sigdefs)

    print("Site Definitions for SIMPLESTUDY TEST")
    sitedefs = rave.send_request(SitesMetadataRequest('SIMPLESTUDY', 'TEST'))
    print(sitedefs)

    print("Users for sites in SIMPLESTUDY TEST")
    users = rave.send_request(UsersRequest('SIMPLESTUDY', 'TEST'))
    print(users)
