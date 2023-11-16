"""
Requests related to the ODM Adapter

See the following for more information (from the Knowledge Hub - requires login):
https://learn.medidata.com/en-US/bundle/rave-web-services/page/odm_operational_data_model_adapter.html

"""
from typing import Optional

from . import RWSAuthorizedGetRequest, QueryOptionGetRequest


class AuditRecordsRequest(QueryOptionGetRequest):
    """Clinical Audit Records Dataset"""

    KNOWN_QUERY_OPTIONS = ["studyoid", "startid", "per_page", "mode", "unicode"]
    # Permissible values for mode
    ALLOWABLE_MODES = ("default", "all", "enhanced")

    def __init__(self, project_name: str,
                 environment_name: str,
                 startid: Optional[int] = 1,
                 per_page: Optional[int] = 100,
                 mode: Optional[str] = None,
                 unicode: Optional[bool] = False):
        """
        :param str project_name: Project Name
        :param str environment_name: Environment Name
        :param int startid: Starting Audit
        :param int per_page: Page Size
        :param str mode: extract more Audit Subcategories (allowed values: default, all, enhanced)
        :param bool unicode: specify Unicode characters are required in the response.
        """
        self.project_name = project_name
        self.environment_name = environment_name
        self.startid = startid
        self.per_page = per_page
        if mode and mode not in self.ALLOWABLE_MODES:
            raise ValueError("mode must be one of %s" % ", ".join(self.ALLOWABLE_MODES))
        self.mode = mode
        self._unicode = unicode

    @property
    def unicode(self) -> str:
        return 'true' if self._unicode else None

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
