__author__ = 'isparks'
import unittest

from rwslib.extras.local_cv import SQLLiteDBAdapter, LocalCVBuilder

metadata = """projectname,viewname,ordinal,varname,vartype,varlength,varformat,varlabel
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
"SIMPLESTUDY","V_SIMPLESTUDY_ENROL","28","SaveTs","num","8","datetime22.3","Timestamp of last save in clinical views"
"SIMPLESTUDY","V_SIMPLESTUDY_ENROL","29","MinCreated","num","8","datetime22.3","Earliest data creation time"
"SIMPLESTUDY","V_SIMPLESTUDY_ENROL","30","MaxUpdated","num","8","datetime22.3","Latest data update time"
"SIMPLESTUDY","V_SIMPLESTUDY_ENROL","31","SUBID","char","10","$10.","SUBID"
"SIMPLESTUDY","V_SIMPLESTUDY_ENROL","32","BIRTHDT","num","8","datetime22.3","BIRTHDT"
"SIMPLESTUDY","V_SIMPLESTUDY_ENROL","33","BIRTHDT_RAW","char","11","$11.","BIRTHDT(Character)"
"SIMPLESTUDY","V_SIMPLESTUDY_ENROL","34","BIRTHDT_INT","num","8","datetime22.3","BIRTHDTInterpolated"
"SIMPLESTUDY","V_SIMPLESTUDY_ENROL","35","BIRTHDT_YYYY","num","8","4.","BIRTHDTYear"
"SIMPLESTUDY","V_SIMPLESTUDY_ENROL","36","BIRTHDT_MM","num","8","2.","BIRTHDTMonth"
"SIMPLESTUDY","V_SIMPLESTUDY_ENROL","37","BIRTHDT_DD","num","8","2.","BIRTHDTDay"
"SIMPLESTUDY","V_SIMPLESTUDY_ENROL_RAW","1","userid","num","8","10.","Internal id for the user"
"SIMPLESTUDY","V_SIMPLESTUDY_ENROL_RAW","2","projectid","num","8","10.","projectid"
"SIMPLESTUDY","V_SIMPLESTUDY_ENROL_RAW","3","project","char","255","$255.","project"
"SIMPLESTUDY","V_SIMPLESTUDY_ENROL_RAW","4","studyid","num","8","10.","Internal id for the study"
"SIMPLESTUDY","V_SIMPLESTUDY_ENROL_RAW","5","environmentName","char","20","$20.","Environment"
"SIMPLESTUDY","V_SIMPLESTUDY_ENROL_RAW","6","subjectId","num","8","10.","Internal id for the subject"
"SIMPLESTUDY","V_SIMPLESTUDY_ENROL_RAW","7","StudySiteId","num","8","10.","Internal id for study site"
"SIMPLESTUDY","V_SIMPLESTUDY_ENROL_RAW","8","Subject","char","50","$50.","Subject name or identifier"
"SIMPLESTUDY","V_SIMPLESTUDY_ENROL_RAW","9","siteid","num","8","10.","Internal id for the site"
"SIMPLESTUDY","V_SIMPLESTUDY_ENROL_RAW","10","Site","char","255","$255.","Site name"
"SIMPLESTUDY","V_SIMPLESTUDY_ENROL_RAW","11","SiteNumber","char","50","$50.","SiteNumber"
"SIMPLESTUDY","V_SIMPLESTUDY_ENROL_RAW","12","SiteGroup","char","40","$40.","SiteGroup"
"SIMPLESTUDY","V_SIMPLESTUDY_ENROL_RAW","13","instanceId","num","8","10.","Internal id for the instance"
"SIMPLESTUDY","V_SIMPLESTUDY_ENROL_RAW","14","InstanceName","char","255","$255.","Folder instance name"
"SIMPLESTUDY","V_SIMPLESTUDY_ENROL_RAW","15","InstanceRepeatNumber","num","8","10.","InstanceRepeatNumber"
"SIMPLESTUDY","V_SIMPLESTUDY_ENROL_RAW","16","folderid","num","8","10.","Internal id for the folder"
"SIMPLESTUDY","V_SIMPLESTUDY_ENROL_RAW","17","Folder","char","50","$50.","Folder OID"
"SIMPLESTUDY","V_SIMPLESTUDY_ENROL_RAW","18","FolderName","char","255","$255.","Folder name"
"SIMPLESTUDY","V_SIMPLESTUDY_ENROL_RAW","19","FolderSeq","num","8","12.1","Folder sequence number"
"SIMPLESTUDY","V_SIMPLESTUDY_ENROL_RAW","20","TargetDays","num","8","10.","Target days from study start"
"SIMPLESTUDY","V_SIMPLESTUDY_ENROL_RAW","21","DataPageId","num","8","10.","Internal id for data page"
"SIMPLESTUDY","V_SIMPLESTUDY_ENROL_RAW","22","DataPageName","char","255","$255.","eCRF page name"
"SIMPLESTUDY","V_SIMPLESTUDY_ENROL_RAW","23","PageRepeatNumber","num","8","10.","Sequence number of eCRF page in folder"
"SIMPLESTUDY","V_SIMPLESTUDY_ENROL_RAW","24","RecordDate","num","8","datetime22.3","Clinical date of record (ex: visit date)"
"SIMPLESTUDY","V_SIMPLESTUDY_ENROL_RAW","25","RecordId","num","8","10.","Internal id for the record"
"SIMPLESTUDY","V_SIMPLESTUDY_ENROL_RAW","26","recordposition","num","8","10.","Record number"
"SIMPLESTUDY","V_SIMPLESTUDY_ENROL_RAW","27","RecordActive","num","8","1.","Is record active"
"SIMPLESTUDY","V_SIMPLESTUDY_ENROL_RAW","28","SaveTs","num","8","datetime22.3","Timestamp of last save in clinical views"
"SIMPLESTUDY","V_SIMPLESTUDY_ENROL_RAW","29","MinCreated","num","8","datetime22.3","Earliest data creation time"
"SIMPLESTUDY","V_SIMPLESTUDY_ENROL_RAW","30","MaxUpdated","num","8","datetime22.3","Latest data update time"
"SIMPLESTUDY","V_SIMPLESTUDY_ENROL_RAW","31","SUBID","char","10","$10.","SUBID"
"SIMPLESTUDY","V_SIMPLESTUDY_ENROL_RAW","32","BIRTHDT","char","11","$11.","BIRTHDT"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","1","userid","num","8","10.","Internal id for the user"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","2","projectid","num","8","10.","projectid"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","3","project","char","255","$255.","project"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","4","studyid","num","8","10.","Internal id for the study"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","5","environmentName","char","20","$20.","Environment"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","6","subjectId","num","8","10.","Internal id for the subject"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","7","StudySiteId","num","8","10.","Internal id for study site"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","8","Subject","char","50","$50.","Subject name or identifier"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","9","siteid","num","8","10.","Internal id for the site"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","10","Site","char","255","$255.","Site name"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","11","SiteNumber","char","50","$50.","SiteNumber"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","12","SiteGroup","char","40","$40.","SiteGroup"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","13","instanceId","num","8","10.","Internal id for the instance"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","14","InstanceName","char","255","$255.","Folder instance name"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","15","InstanceRepeatNumber","num","8","10.","InstanceRepeatNumber"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","16","folderid","num","8","10.","Internal id for the folder"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","17","Folder","char","50","$50.","Folder OID"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","18","FolderName","char","255","$255.","Folder name"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","19","FolderSeq","num","8","12.1","Folder sequence number"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","20","TargetDays","num","8","10.","Target days from study start"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","21","DataPageId","num","8","10.","Internal id for data page"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","22","DataPageName","char","255","$255.","eCRF page name"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","23","PageRepeatNumber","num","8","10.","Sequence number of eCRF page in folder"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","24","RecordDate","num","8","datetime22.3","Clinical date of record (ex: visit date)"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","25","recordposition","num","8","10.","Record number"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","26","DatapointActive","num","8","1.","DatapointActive"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","27","SaveTs","num","8","datetime22.3","Timestamp of last save in clinical views"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","28","DataPointId","num","8","10.","DataPointId"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","29","RecordId","num","8","10.","Internal id for the record"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","30","FormId","num","8","10.","FormId"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","31","FieldId","num","8","10.","FieldId"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","32","AnalyteId","num","8","10.","AnalyteId"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","33","LabId","num","8","10.","LabId"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","34","AnalyteRangeId","num","8","10.","AnalyteRangeId"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","35","DataDictionaryId","num","8","10.","DataDictionaryId"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","36","LabUnitId","num","8","10.","LabUnitId"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","37","LabStandardGroupId","num","8","10.","LabStandardGroupId"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","38","LabUnitConversionId","num","8","10.","LabUnitConversionId"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","39","StandardLabUnitId","num","8","10.","StandardLabUnitId"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","40","ReferenceLabId","num","8","10.","ReferenceLabId"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","41","ReferenceRangeId","num","8","10.","ReferenceRangeId"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","42","ReferenceDataDictionaryId","num","8","10.","ReferenceDataDictionaryId"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","43","AlertLabId","num","8","10.","AlertLabId"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","44","AlertRangeId","num","8","10.","AlertRangeId"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","45","AlertDataDictionaryId","num","8","10.","AlertDataDictionaryId"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","46","Created","num","8","datetime22.3","Created"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","47","Updated","num","8","datetime22.3","Updated"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","48","Form","char","50","$50.","Form"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","49","FormName","char","255","$255.","FormName"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","50","fieldOrdinal","num","8","10.","fieldOrdinal"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","51","AnalyteName","char","255","$255.","AnalyteName"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","52","AnalyteValue","char","2000","$2000.","AnalyteValue"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","53","NumericValue","num","8","16.7","NumericValue"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","54","CodedValue","char","255","$255.","CodedValue"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","55","LabName","char","255","$255.","LabName"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","56","RangesApproved","num","8","1.","RangesApproved"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","57","LabDictionary","char","255","$255.","LabDictionary"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","58","LabLow","num","8","16.7","LabLow"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","59","LabHigh","num","8","16.7","LabHigh"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","60","LabUnits","char","255","$255.","LabUnits"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","61","LabFlag","char","1","$1.","LabFlag"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","62","LabComments","char","255","$255.","LabComments"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","63","StdGroup","char","255","$255.","StdGroup"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","64","StdValue","num","8","16.7","StdValue"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","65","StdLow","num","8","16.7","StdLow"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","66","StdHigh","num","8","16.7","StdHigh"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","67","StdUnits","char","255","$255.","StdUnits"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","68","RefLab","char","255","$255.","RefLab"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","69","RefDictionary","char","255","$255.","RefDictionary"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","70","RefLow","num","8","16.7","RefLow"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","71","RefHigh","num","8","16.7","RefHigh"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","72","RefFlag","char","1","$1.","RefFlag"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","73","RefComments","char","255","$255.","RefComments"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","74","AlertLab","char","255","$255.","AlertLab"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","75","AlertDictionary","char","255","$255.","AlertDictionary"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","76","AlertLow","num","8","16.7","AlertLow"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","77","AlertHigh","num","8","16.7","AlertHigh"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","78","AlertFlag","char","1","$1.","AlertFlag"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","79","AlertComments","char","255","$255.","AlertComments"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","80","ClinSigStatus","num","8","10.","ClinSigStatus"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","81","ClinSigValue","char","50","$50.","ClinSigValue"
"SIMPLESTUDY","V_SIMPLESTUDY_Lab","82","ClinSigComment","char","255","$255.","ClinSigComment"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL","1","userid","num","8","10.","Internal id for the user"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL","2","projectid","num","8","10.","projectid"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL","3","project","char","255","$255.","project"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL","4","studyid","num","8","10.","Internal id for the study"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL","5","environmentName","char","20","$20.","Environment"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL","6","subjectId","num","8","10.","Internal id for the subject"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL","7","StudySiteId","num","8","10.","Internal id for study site"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL","8","Subject","char","50","$50.","Subject name or identifier"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL","9","siteid","num","8","10.","Internal id for the site"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL","10","Site","char","255","$255.","Site name"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL","11","SiteNumber","char","50","$50.","SiteNumber"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL","12","SiteGroup","char","40","$40.","SiteGroup"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL","13","instanceId","num","8","10.","Internal id for the instance"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL","14","InstanceName","char","255","$255.","Folder instance name"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL","15","InstanceRepeatNumber","num","8","10.","InstanceRepeatNumber"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL","16","folderid","num","8","10.","Internal id for the folder"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL","17","Folder","char","50","$50.","Folder OID"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL","18","FolderName","char","255","$255.","Folder name"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL","19","FolderSeq","num","8","12.1","Folder sequence number"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL","20","TargetDays","num","8","10.","Target days from study start"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL","21","DataPageId","num","8","10.","Internal id for data page"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL","22","DataPageName","char","255","$255.","eCRF page name"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL","23","PageRepeatNumber","num","8","10.","Sequence number of eCRF page in folder"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL","24","RecordDate","num","8","datetime22.3","Clinical date of record (ex: visit date)"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL","25","RecordId","num","8","10.","Internal id for the record"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL","26","recordposition","num","8","10.","Record number"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL","27","RecordActive","num","8","1.","Is record active"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL","28","SaveTs","num","8","datetime22.3","Timestamp of last save in clinical views"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL","29","MinCreated","num","8","datetime22.3","Earliest data creation time"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL","30","MaxUpdated","num","8","datetime22.3","Latest data update time"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL","31","VDAT","num","8","datetime22.3","VDAT"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL","32","VDAT_RAW","char","11","$11.","VDAT(Character)"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL","33","VDAT_INT","num","8","datetime22.3","VDATInterpolated"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL","34","VDAT_YYYY","num","8","4.","VDATYear"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL","35","VDAT_MM","num","8","2.","VDATMonth"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL","36","VDAT_DD","num","8","2.","VDATDay"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL","37","WEIGHT_KG","num","8","5.1","WEIGHT_KG"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL","38","WEIGHT_KG_RAW","char","6","$6.","WEIGHT_KG(Character)"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL","39","HEIGHT_CM","num","8","5.1","HEIGHT_CM"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL","40","HEIGHT_CM_RAW","char","6","$6.","HEIGHT_CM(Character)"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL_RAW","1","userid","num","8","10.","Internal id for the user"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL_RAW","2","projectid","num","8","10.","projectid"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL_RAW","3","project","char","255","$255.","project"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL_RAW","4","studyid","num","8","10.","Internal id for the study"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL_RAW","5","environmentName","char","20","$20.","Environment"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL_RAW","6","subjectId","num","8","10.","Internal id for the subject"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL_RAW","7","StudySiteId","num","8","10.","Internal id for study site"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL_RAW","8","Subject","char","50","$50.","Subject name or identifier"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL_RAW","9","siteid","num","8","10.","Internal id for the site"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL_RAW","10","Site","char","255","$255.","Site name"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL_RAW","11","SiteNumber","char","50","$50.","SiteNumber"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL_RAW","12","SiteGroup","char","40","$40.","SiteGroup"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL_RAW","13","instanceId","num","8","10.","Internal id for the instance"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL_RAW","14","InstanceName","char","255","$255.","Folder instance name"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL_RAW","15","InstanceRepeatNumber","num","8","10.","InstanceRepeatNumber"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL_RAW","16","folderid","num","8","10.","Internal id for the folder"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL_RAW","17","Folder","char","50","$50.","Folder OID"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL_RAW","18","FolderName","char","255","$255.","Folder name"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL_RAW","19","FolderSeq","num","8","12.1","Folder sequence number"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL_RAW","20","TargetDays","num","8","10.","Target days from study start"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL_RAW","21","DataPageId","num","8","10.","Internal id for data page"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL_RAW","22","DataPageName","char","255","$255.","eCRF page name"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL_RAW","23","PageRepeatNumber","num","8","10.","Sequence number of eCRF page in folder"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL_RAW","24","RecordDate","num","8","datetime22.3","Clinical date of record (ex: visit date)"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL_RAW","25","RecordId","num","8","10.","Internal id for the record"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL_RAW","26","recordposition","num","8","10.","Record number"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL_RAW","27","RecordActive","num","8","1.","Is record active"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL_RAW","28","SaveTs","num","8","datetime22.3","Timestamp of last save in clinical views"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL_RAW","29","MinCreated","num","8","datetime22.3","Earliest data creation time"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL_RAW","30","MaxUpdated","num","8","datetime22.3","Latest data update time"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL_RAW","31","VDAT","char","11","$11.","VDAT"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL_RAW","32","WEIGHT_KG","char","6","$6.","WEIGHT_KG"
"SIMPLESTUDY","V_SIMPLESTUDY_VITAL_RAW","33","HEIGHT_CM","char","6","$6.","HEIGHT_CM"
EOF
"""

enrol_data = """userid,projectid,project,studyid,environmentName,subjectId,StudySiteId,Subject,siteid,Site,SiteNumber,SiteGroup,instanceId,InstanceName,InstanceRepeatNumber,folderid,Folder,FolderName,FolderSeq,TargetDays,DataPageId,DataPageName,PageRepeatNumber,RecordDate,RecordId,recordposition,RecordActive,SaveTs,MinCreated,MaxUpdated,SUBID,BIRTHDT,BIRTHDT_RAW,BIRTHDT_INT,BIRTHDT_YYYY,BIRTHDT_MM,BIRTHDT_DD
"457","85","SIMPLESTUDY","95","TEST","32112","143","1","120","TESTSITE","TESTSITE","World","","","","","","","0.0","","662503","Enrol","0","","1346660","0","1","2013-10-07T15:50:33","2013-06-24T09:52:09","2013-06-24T09:52:10","1","1973-06-26T00:00:00","1973 Jun 26","1973-06-26T00:00:00","1973","6","26"
"457","85","SIMPLESTUDY","95","TEST","32113","143","2","120","TESTSITE","TESTSITE","World","","","","","","","0.0","","662505","Enrol","0","","1346662","0","1","2013-10-07T15:50:33","2013-06-24T09:52:11","2013-06-24T09:52:11","2","1971-10-13T00:00:00","1971 Oct 13","1971-10-13T00:00:00","1971","10","13"
"457","85","SIMPLESTUDY","95","TEST","32114","143","3","120","TESTSITE","TESTSITE","World","","","","","","","0.0","","662507","Enrol","0","","1346664","0","1","2013-10-07T15:50:33","2013-06-24T09:52:12","2013-10-07T15:50:18","3","1953-08-10T00:00:00","1953 Aug 10","1953-08-10T00:00:00","1953","8","10"
"457","85","SIMPLESTUDY","95","TEST","32115","143","4","120","TESTSITE","TESTSITE","World","","","","","","","0.0","","662509","Enrol","0","","1346666","0","1","2013-10-07T15:50:33","2013-06-24T09:52:13","2013-06-24T09:52:13","4","1975-02-08T00:00:00","1975 Feb 08","1975-02-08T00:00:00","1975","2","8"
"457","85","SIMPLESTUDY","95","TEST","32116","143","5","120","TESTSITE","TESTSITE","World","","","","","","","0.0","","662511","Enrol","0","","1346668","0","1","2013-10-07T15:50:33","2013-06-24T09:52:15","2013-06-24T09:52:15","5","1977-10-23T00:00:00","1977 Oct 23","1977-10-23T00:00:00","1977","10","23"
"457","85","SIMPLESTUDY","95","TEST","32117","143","6","120","TESTSITE","TESTSITE","World","","","","","","","0.0","","662513","Enrol","0","","1346670","0","1","2013-10-07T15:50:33","2013-06-24T09:52:16","2013-06-24T09:52:16","6","1970-04-18T00:00:00","1970 Apr 18","1970-04-18T00:00:00","1970","4","18"
"457","85","SIMPLESTUDY","95","TEST","32118","143","7","120","TESTSITE","TESTSITE","World","","","","","","","0.0","","662515","Enrol","0","","1346672","0","1","2013-10-07T15:50:33","2013-06-24T09:52:17","2013-06-24T09:52:17","7","1957-10-14T00:00:00","1957 Oct 14","1957-10-14T00:00:00","1957","10","14"
"457","85","SIMPLESTUDY","95","TEST","32119","143","8","120","TESTSITE","TESTSITE","World","","","","","","","0.0","","662517","Enrol","0","","1346674","0","1","2013-10-07T15:50:33","2013-06-24T09:52:18","2013-10-07T15:16:29","8","1973-01-18T00:00:00","1973 Jan 18","1973-01-18T00:00:00","1973","1","18"
"457","85","SIMPLESTUDY","95","TEST","32120","143","9","120","TESTSITE","TESTSITE","World","","","","","","","0.0","","662519","Enrol","0","","1346676","0","1","2013-10-07T15:50:33","2013-06-24T09:52:19","2013-06-24T09:52:19","9","1974-03-04T00:00:00","1974 Mar 04","1974-03-04T00:00:00","1974","3","4"
"457","85","SIMPLESTUDY","95","TEST","32121","143","10","120","TESTSITE","TESTSITE","World","","","","","","","0.0","","662521","Enrol","0","","1346678","0","1","2013-10-07T15:50:33","2013-06-24T09:52:20","2013-06-24T09:52:20","10","1964-03-03T00:00:00","1964 Mar 03","1964-03-03T00:00:00","1964","3","3"
"457","85","SIMPLESTUDY","95","TEST","34128","147","012","123","TESTSITE2","TESTSITE2","World","","","","","","","0.0","","705383","Enrol","0","","1432815","0","1","2013-10-07T15:50:33","2013-10-03T13:18:48","2013-10-07T15:15:45","012","1973-06-26T00:00:00","1973 Jun 26","1973-06-26T00:00:00","1973","6","26"
EOF
"""

class FakeCursor(object):
    def __init__(self):
        self.sql = []

    def __call__(self):
        return self

    def execute(self, *args, **kwargs):
        self.sql.append((args, kwargs,))

    def executemany(self, stmt, rows):
        """Simple fake for unit tests"""
        for row in rows:
            self.execute(stmt, row)

class FakeConn(object):
    """Fake daabase connection."""
    def __init__(self):
        self.cursor = FakeCursor()

    def commit(self):
        pass

class TestRWSCSVReader(unittest.TestCase):
    def setUp(self):
        fake_db = FakeConn()
        self.tested = SQLLiteDBAdapter(fake_db)
        self.tested._setDatasets(metadata)

    def test_dataset(self):
        self.assertEqual("V_SIMPLESTUDY_ENROL" in self.tested.datasets, True)

    def test_cols(self):
        self.assertEqual(self.tested.datasets["V_SIMPLESTUDY_ENROL"][0]["ordinal"], "1")
        self.assertEqual(self.tested.datasets["V_SIMPLESTUDY_ENROL"][1]["varname"], "projectid")
        self.assertEqual(self.tested.datasets["V_SIMPLESTUDY_ENROL"][2]["vartype"], "char")
        self.assertEqual(self.tested.datasets["V_SIMPLESTUDY_ENROL"][3]["varformat"], "10.")
        self.assertEqual(self.tested.datasets["V_SIMPLESTUDY_ENROL"][4]["varlabel"], "Environment")

    def test_table_gen(self):
        "test generating tables"
        sql = self.tested._generateDDL()
        self.assertEqual(sql[0],'drop table if exists V_SIMPLESTUDY_ENROL;')
        self.assertEqual(sql[1][:34],u'CREATE TABLE V_SIMPLESTUDY_ENROL (')
        self.assertEqual(True, 'userid NUMERIC' in sql[1])
        self.assertEqual(True, 'projectid NUMERIC' in sql[1])
        self.assertEqual(True, 'project TEXT' in sql[1])


    def test_insert_gen(self):
        """Test generation of insert statements"""
        self.tested.processFormData(enrol_data, 'V_SIMPLESTUDY_ENROL')

        first_line = self.tested.conn.cursor.sql[0][0]
        first_statement = first_line[0]
        first_values = first_line[1]

        #Check sql construction
        self.assertEqual(first_statement.startswith('INSERT INTO V_SIMPLESTUDY_ENROL (userid,projectid,project'), True)
        self.assertEqual('SUBID,BIRTHDT,BIRTHDT_RAW,BIRTHDT_INT,BIRTHDT_YYYY,BIRTHDT_MM,BIRTHDT_DD)' in first_statement, True)

        #Check values
        self.assertEqual('457',first_values[0]) #First value
        self.assertEqual('26',first_values[-1]) #Last value


class TestSQLDataType(unittest.TestCase):
    def test_sql_typefor(self):

        sqlite_db = None
        tested = SQLLiteDBAdapter(sqlite_db)
        self.assertEqual(tested.getSQLDataType("num"), "NUMERIC")
        self.assertEqual(tested.getSQLDataType("char"), "TEXT")

class TestNameTypeFromViewname(unittest.TestCase):
    def test_name_type_from_viewname(self):
        self.assertEqual(LocalCVBuilder.name_type_from_viewname("V_SIMPLESTUDY_ENROL")[0],"ENROL")
        self.assertEqual(LocalCVBuilder.name_type_from_viewname("V_SIMPLESTUDY_ENROL")[1],"REGULAR")
        self.assertEqual(LocalCVBuilder.name_type_from_viewname("V_SIMPLESTUDY_ENROL_RAW")[0],"ENROL")
        self.assertEqual(LocalCVBuilder.name_type_from_viewname("V_SIMPLESTUDY_ENROL_RAW")[1],"RAW")
        self.assertEqual(LocalCVBuilder.name_type_from_viewname("V_SIMPLESTUDY_Lab")[0],"Lab")
        self.assertEqual(LocalCVBuilder.name_type_from_viewname("V_SIMPLESTUDY_Lab")[1],"REGULAR")
        self.assertEqual(LocalCVBuilder.name_type_from_viewname("V_SIMPLESTUDY_Lab_")[1],"REGULAR")

if __name__ == '__main__':
    unittest.main()
