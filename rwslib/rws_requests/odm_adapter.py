"""
Requests related to the ODM Adapter

http://rws-webhelp.s3.amazonaws.com/WebHelp_ENG/solutions/clinical_data_audits/index.html#odm-adapter
"""
from . import RWSRequest


class AuditRecordsRequest(RWSRequest):
    """Clinical Audit Records Dataset"""
    requires_authorization = True
    method = "GET"

    def __init__(self, project_name, environment_name, startid=1, per_page=100):
        self.project_name = project_name
        self.environment_name = environment_name
        self.startid = startid
        self.per_page = per_page

    def studyname_environment(self):
        return "%s(%s)" % (self.project_name, self.environment_name,)

    def _querystring(self):
        """Additional keyword arguments"""

        kw = {'studyoid': self.studyname_environment(),
              'startid': self.startid,
              'per_page': self.per_page,
        }
        return kw

    def url_path(self):
        """Return url path list"""
        return self.make_url('datasets', 'ClinicalAuditRecords.odm', **self._querystring())

class VersionFoldersRequest(RWSRequest):
    """Identify all folders in use in study"""
    requires_authorization = True
    method = "GET"

    def __init__(self, project_name, environment_name):
        self.project_name = project_name
        self.environment_name = environment_name

    def studyname_environment(self):
        return "%s(%s)" % (self.project_name, self.environment_name,)

    def _querystring(self):
        """Additional keyword arguments"""

        kw = {'studyoid': self.studyname_environment() }
        return kw

    def _dataset_name(self):
        return 'VersionFolders.odm'

    def url_path(self):
        """Return url path list"""
        return self.make_url('datasets', self._dataset_name(), **self._querystring())


class SitesMetadataRequest(RWSRequest):
    """List all sites in a study along with their StudyVersions"""
    requires_authorization = True
    method = "GET"

    def __init__(self, project_name=None, environment_name=None):
        self.project_name = project_name
        self.environment_name = environment_name

        if project_name is not None:
            if environment_name in [None,'']:
                raise AttributeError("environment_name cannot be empty if project_name is set")

        if environment_name is not None:
            if project_name in [None,'']:
                raise AttributeError("project_name cannot be empty if environment_name is set")

    def _querystring(self):
        """Additional keyword arguments if filtered to project_name and environment_name"""
        if self.project_name is not None:
            return {'studyoid': self.studyname_environment() }
        return {}

    def url_path(self):
        """Return url path list"""
        return self.make_url('datasets', 'Sites.odm', **self._querystring())


class UsersRequest(RWSRequest):
    """Return list of users for study (can be filtered by location)"""
    requires_authorization = True
    method = "GET"

    def __init__(self, project_name, environment_name, location_oid=None):
        self.project_name = project_name
        self.environment_name = environment_name
        self.location_oid = location_oid

    def studyname_environment(self):
        return "%s(%s)" % (self.project_name, self.environment_name,)

    def _querystring(self):
        """Additional keyword arguments"""

        kw = {'studyoid': self.studyname_environment()}
        if self.location is not None:
            kw['locationoid'] = self.location_oid
        return kw

    def url_path(self):
        """Return url path list"""
        return self.make_url('datasets', 'Users.odm', **self._querystring())


class SignatureDefinitionsRequest(RWSRequest):
    """Return signature definitions for all versions of the study"""
    requires_authorization = True
    method = "GET"

    def __init__(self, project_name):
        self.project_name = project_name

    def _querystring(self):
        """Additional keyword arguments"""

        kw = {'studyid': self.project_name}
        return kw

    def url_path(self):
        """Return url path list"""
        return self.make_url('datasets', 'Signatures.odm', **self._querystring())
