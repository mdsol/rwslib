if exists (select 1 from sysobjects where [name] = 'csp_rwscmd_getdata')
	drop procedure dbo.csp_rwscmd_getdata

GO
CREATE procedure [dbo].csp_rwscmd_getdata

		@StudyOID NVARCHAR(100),
		@SubjectKey NVARCHAR(100) = '',
		@SubjectName NVARCHAR(100) = '',
		@IncludeValues INT = 0,
		@IncludeIDs INT = 0,
		@UserID INT

AS
BEGIN


select distinct s.StudyOID, s.LocationOID, s.SubjectName, s.SubjectUUID, s.MetaDataVersionOID,
isnull(fl.OID, 'SUBJECT') as StudyEventOID,
case when isnull(i.parentinstanceid,0) = 0 and isnull(i.instancerepeatnumber,0) = 0
	then ''
	when isnull(i.parentinstanceid,0) = 0
	then fl.oid + '['+CAST(i.instanceRepeatNumber AS varchar(50))+']'
else
dbo.fnWebServicesGetNestedFolderPath(i.InstanceID)
end as StudyEventRepeatKey,
REPLACE(CONVERT(varchar, i.instancedate, 120), ' ', 'T') as InstanceDate,
 i.instanceid as InstanceID,
fo.oid as FormOID, dp.PageRepeatNumber + 1 as FormRepeatKey, dp.datapageid as DatapageID,
REPLACE(CONVERT(varchar, dp.datapagedate, 120), ' ', 'T') as DatapageDate,
r.recordid as RecordID, r.recordposition as ItemGroupRepeatKey, fi.oid as ItemOID,
REPLACE(CONVERT(varchar, r.recorddate, 120), ' ', 'T') as RecordDate,
d.datapointid as DatapointID, d.data as Data,
fl.ordinal, fo.ordinal, fi.ordinal, @IncludeIDs as IncludeIDs
from records r
join forms fo on r.formid = fo.formid
join fields fi on fo.formid = fi.formid
join variables v on fi.variableid = v.variableid
join datapages dp on r.datapageid = dp.datapageid
join instances i on dp.instanceid = i.instanceid
join (
select distinct dbo.fnLocalDefault(p.ProjectName)+'('+dbo.fnLocalDefault(st.EnvironmentNameID)+')' AS StudyOID,
	si.SiteNumber as LocationOID, s2.SubjectName as SubjectName,  s2.Guid as SubjectUUID, s2.subjectid,  s2.CRFVersionID as MetaDataVersionOID,
	uor.roleid
	from
subjects s2
JOIN StudySites ss ON ss.StudySiteID = s2.StudySiteID
JOIN UserStudySites uss on uss.studysiteid = ss.studysiteid
JOIN Sites si ON si.SiteID = ss.SiteID
JOIN Studies st on ss.studyid = st.studyid
JOIN Projects p on st.projectid = p.projectid
JOIN UserObjectRole uor on uor.granttoobjecttypeid = 17 and uor.granttoobjectid = uss.userid
and uor.grantonobjecttypeid = 7 and uor.grantonobjectid = st.studyid
where (s2.subjectname = isnull(@SubjectName,'') or s2.guid = isnull(@SubjectKey, ''))
and uss.userid = @UserID
and uss.isuserstudysiteactive = 1
and uor.active = 1
and st.studyactive = 1
and st.deleted = 0
and p.projectactive = 1
and dbo.fnLocalDefault(p.ProjectName)+'('+dbo.fnLocalDefault(st.EnvironmentNameID)+')' = @StudyOID
and s2.subjectactive = 1
and s2.deleted = 0
and isnull(s2.isuserdeactivated, 0) = 0
and s2.isunavailable = 0
and ss.studysiteactive = 1
and ss.deleted = 0
and isnull(ss.isuserdeactivated, 0) = 0
and si.siteactive = 1
 ) s on r.subjectid = s.subjectid
left join folders fl on fl.folderid = i.folderid
left join datapoints d on r.recordid = d.recordid and fi.fieldid = d.fieldid
where
 fi.fieldactive = 1
and fi.isvisible = 1
and v.derivationid is null

and i.instanceactive = 1
and i.deleted = 0
and isnull(i.isuserdeactivated, 0) = 0

and dp.datapageactive = 1
and dp.deleted = 0
and isnull(dp.isuserdeactivated, 0) = 0

and r.recordactive = 1
and r.deleted = 0
and isnull(r.isuserdeactivated, 0) = 0

and isnull(d.dataactive, 1) = 1
and isnull(d.deleted, 0) = 0
and isnull(d.isuserdeactivated, 0) = 0
and isnull(d.isvisible, 1) = 1
and isnull(d.isfrozen, 0) = 0
and isnull(d.islocked, 0) = 0

and (@IncludeValues = 1 or (@IncludeValues = 0 and isnull(d.data, '') = ''))

and (fi.islog = 0 or (fi.islog = 1 and r.recordposition > 0))

and not exists (select null from fieldrestrictions fir
where fir.fieldid = fi.fieldid
and roleid = s.roleid)
and not exists (select null from formrestrictions fr
where fr.formid = fo.formid
and roleid = s.roleid)
order by StudyOID, LocationOID, SubjectName, SubjectUUID, fl.ordinal, studyeventrepeatkey, fo.ordinal, formrepeatkey, recordposition, fi.ordinal






END