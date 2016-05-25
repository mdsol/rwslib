Exec spWebServicesCdsInstaller
@datasetname = 'rwscmd_getdata',
@requiresuserfiltering = 1,
@databaseobjecttype = 2,
@sequence = 1,
@dbobject = 'csp_rwscmd_getdata',
@paging_enabled = 0,
@per_page_default = 1000,
@per_page_min = 1,
@per_page_max = 9999,
@verbs_enabled = 0,
@request_body_enabled = 0,
@allowed_request_content_type = NULL
go

declare @format nvarchar(max)
set @format = '{% if document.section == "header" %}
  <ODM ODMVersion="1.3" FileType="Transactional" FileOID="{{ request.Id }}" CreationDateTime="{{ request.Date | date:''yyyy-MM-ddTHH:mm:ss.fff-00:00'' }}" xmlns="http://www.cdisc.org/ns/odm/v1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata">
{% elsif document.section == "body" %}
{% if current.SubjectUUID != previous.SubjectUUID %}
  <ClinicalData StudyOID="{{ current.StudyOID | escape }}" MetaDataVersionOID="{{ current.MetaDataVersionOID | escape }}" >
  <SubjectData SubjectKey="{{ current.SubjectUUID | escape }}" mdsol:SubjectKeyType="SubjectUUID" mdsol:SubjectName="{{ current.SubjectName | escape }}">
  <SiteRef LocationOID="{{ current.LocationOID | escape }}" />
{% endif %}
{% if current.InstanceID != previous.InstanceID %}
 <StudyEventData StudyEventOID="{{ current.StudyEventOID | escape }}"
{% if current.StudyEventRepeatKey != "" %}
 StudyEventRepeatKey="{{ current.StudyEventRepeatKey | escape }}"
{% endif %}
{% if current.IncludeIDs == 1 %}
 mdsol:InstanceId="{{ current.InstanceID }}"
{% if current.InstanceDate != "" %}
 mdsol:InstanceDate="{{ current.InstanceDate | escape }}"
{% endif %}{% endif %}>
{% endif %}
{% if current.DatapageID != previous.DatapageID %}
 <FormData FormOID="{{ current.FormOID | escape }}" FormRepeatKey="{{ current.FormRepeatKey | escape }}"
{% if current.IncludeIDs == 1 %}
 mdsol:DataPageID="{{ current.DatapageID }}"
{% if current.DatapageDate != "" %}
 mdsol:DatapageDate="{{ current.DatapageDate | escape }}"
{% endif %}{% endif %}>
{% endif %}
{% if current.RecordID != previous.RecordID %}
{% if current.ItemGroupRepeatKey == "0" %}
 <ItemGroupData ItemGroupOID="{{ current.FormOID | escape }}"
{% else %}
 <ItemGroupData ItemGroupOID="{{ current.FormOID | escape }}_LOG_LINE" ItemGroupRepeatKey="{{ current.ItemGroupRepeatKey | escape }}"
{% if current.IncludeIDs == 1 %}
 mdsol:RecordID="{{ current.RecordID }}"
{% if current.RecordDate != "" %}
 mdsol:RecordDate="{{ current.RecordDate | escape }}"
{% endif %}{% endif %}
{% endif %}>
{% endif %}
 <ItemData ItemOID="{{ current.FormOID | escape }}.{{ current.ItemOID | escape }}" Value="{{ current.Data | escape }}"/>
{% if current.RecordID != next.RecordID %}
</ItemGroupData>
{% endif %}
{% if current.DatapageID != next.DatapageID %}
</FormData>
{% endif %}
{% if current.InstanceID != next.InstanceID %}
</StudyEventData>
{% endif %}
{% if current.SubjectUUID != next.SubjectUUID %}
 </SubjectData></ClinicalData>
{% endif %}
 {% elsif document.section == "footer" %}    </ODM>{% endif %}
'

Exec spWebServicesCdsFormatInstaller
@datasetname = 'rwscmd_getdata',
@formatName = 'odm',
@formatTypeId = 2,
@rowTemplate = @format,
@header = '',
@footer = '',
@contentType = 'text/xml'




