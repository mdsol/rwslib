from rwslib.rws_requests import (
    ClinicalStudiesRequest,
    MetadataStudiesRequest,
    StudyDatasetRequest,
    StudySubjectsRequest,
    StudyVersionRequest,
    StudyVersionsRequest,
)
from rwslib.rws_requests.biostats_gateway import (
    CVMetaDataRequest,
    FormDataRequest,
    ProjectMetaDataRequest,
)
from rwslib.rws_requests.odm_adapter import (
    AuditRecordsRequest,
    SitesMetadataRequest,
    VersionFoldersRequest,
)


class UTF8Result:
    UTF8_BOM = b"\xEF\xBB\xBF"
    DEFAULT_REQUEST_ENCODING = "ISO-8859-1"

    def result(self, response):
        if response.content.startswith(self.UTF8_BOM):
            response.encoding = "utf-8-sig"
        elif (
            response.encoding == self.DEFAULT_REQUEST_ENCODING
            and response.apparent_encoding == "utf-8"
        ):
            # Force UTF-8 when request's default "ISO-8859-1" is used
            response.encoding = "utf-8"

        return super().result(response)


class MetadataStudiesRequestUTF8(UTF8Result, MetadataStudiesRequest):
    pass


class SitesMetadataRequestUTF8(UTF8Result, SitesMetadataRequest):
    pass


class AuditRecordsRequestUTF8(UTF8Result, AuditRecordsRequest):
    KNOWN_QUERY_OPTIONS = AuditRecordsRequest.KNOWN_QUERY_OPTIONS + ["unicode"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unicode = True


class ClinicalStudiesRequestUTF8(UTF8Result, ClinicalStudiesRequest):
    pass


class CVMetaDataRequestUTF8(UTF8Result, CVMetaDataRequest):
    pass


class StudyDatasetRequestUTF8(UTF8Result, StudyDatasetRequest):
    pass


class FormDataRequestUTF8(UTF8Result, FormDataRequest):
    pass


class ProjectMetaDataRequestUTF8(UTF8Result, ProjectMetaDataRequest):
    pass


class StudyVersionRequestUTF8(UTF8Result, StudyVersionRequest):
    pass


class VersionFoldersRequestUTF8(UTF8Result, VersionFoldersRequest):
    pass


class StudySubjectsRequestUTF8(UTF8Result, StudySubjectsRequest):
    pass


class StudyVersionsRequestUTF8(UTF8Result, StudyVersionsRequest):
    pass
