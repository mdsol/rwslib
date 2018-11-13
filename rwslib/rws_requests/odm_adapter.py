"""
Requests related to the ODM Adapter

http://rws-webhelp.s3.amazonaws.com/WebHelp_ENG/solutions/clinical_data_audits/index.html#odm-adapter
"""
from . import RWSAuthorizedGetRequest, QueryOptionGetRequest


class AuditRecordsRequest(QueryOptionGetRequest):
    """Clinical Audit Records Dataset"""

    KNOWN_QUERY_OPTIONS = ["studyoid", "startid", "per_page"]

    def __init__(self, project_name, environment_name, startid=1, per_page=100):
        """
        :param str project_name: Project Name
        :param str environment_name: Environment Name
        :param int startid: Starting Audit
        :param int per_page: Page Size
        """
        self.project_name = project_name
        self.environment_name = environment_name
        self.startid = startid
        self.per_page = per_page

    @property
    def studyoid(self):
        """Create studyoid from project name and environment"""
        return "%s(%s)" % (self.project_name, self.environment_name)

    def url_path(self):
        """Return url path list"""
        return self.make_url(
            "datasets", "ClinicalAuditRecords.odm", **self._querystring()
        )


class VersionFoldersRequest(QueryOptionGetRequest):
    """Identify all folders in use in study"""

    KNOWN_QUERY_OPTIONS = ["studyoid"]

    def __init__(self, project_name, environment_name):
        """
        :param str project_name: Project Name
        :param str environment_name: Environment Name
        """
        self.project_name = project_name
        self.environment_name = environment_name

    @property
    def studyoid(self):
        """Create studyoid from project name and environment"""
        return "%s(%s)" % (self.project_name, self.environment_name)

    def _dataset_name(self):
        return "VersionFolders.odm"

    def url_path(self):
        """Return url path list"""
        return self.make_url("datasets", self._dataset_name(), **self._querystring())


class SitesMetadataRequest(RWSAuthorizedGetRequest):
    """List all sites in a study along with their StudyVersions"""

    def __init__(self, project_name=None, environment_name=None):
        """
        :param str project_name: Project Name
        :param str environment_name: Environment Name
        """
        self.project_name = project_name
        self.environment_name = environment_name

        if project_name is not None:
            if environment_name in [None, ""]:
                raise AttributeError(
                    "environment_name cannot be empty if project_name is set"
                )

        if environment_name is not None:
            if project_name in [None, ""]:
                raise AttributeError(
                    "project_name cannot be empty if environment_name is set"
                )

    @property
    def studyoid(self):
        """Create studyoid from project name and environment"""
        return "%s(%s)" % (self.project_name, self.environment_name)

    def _querystring(self):
        """Additional keyword arguments if filtered to project_name and environment_name"""
        if self.project_name is not None:
            return {"studyoid": self.studyoid}
        return {}

    def url_path(self):
        """Return url path list"""
        return self.make_url("datasets", "Sites.odm", **self._querystring())


class UsersRequest(RWSAuthorizedGetRequest):
    """Return list of users for study (can be filtered by location)"""

    def __init__(self, project_name, environment_name, location_oid=None):
        """
        :param str project_name: Project Name
        :param str environment_name: Environment Name
        :param str location_oid: Study Site Name to filter with
        """
        self.project_name = project_name
        self.environment_name = environment_name
        self.location_oid = location_oid

    @property
    def studyoid(self):
        """Create studyoid from project name and environment"""
        return "%s(%s)" % (self.project_name, self.environment_name)

    def _querystring(self):
        """Additional keyword arguments"""

        kw = {"studyoid": self.studyoid}
        if self.location_oid is not None:
            kw["locationoid"] = self.location_oid
        return kw

    def url_path(self):
        """Return url path list"""
        return self.make_url("datasets", "Users.odm", **self._querystring())


class SignatureDefinitionsRequest(RWSAuthorizedGetRequest):
    """Return signature definitions for all versions of the study"""

    def __init__(self, project_name):
        """
        :param str project_name: Project Name
        """
        self.project_name = project_name

    def _querystring(self):
        """Additional keyword arguments"""

        kw = {"studyid": self.project_name}
        return kw

    def url_path(self):
        """Return url path list"""
        return self.make_url("datasets", "Signatures.odm", **self._querystring())
