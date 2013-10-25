"""
Views related to clinical views and their metadata, Biostats Gateway/Adapter

http://rws-webhelp.s3.amazonaws.com/WebHelp_ENG/solutions/01_biostat_adapter.html#biostat-adapter

"""

from . import RWSAuthorizedGetRequest, QueryOptionGetRequest, check_dataset_type

#-----------------------------------------------------------------------------------------------------------------------
# Utilities

DATASET_FORMATS = {'csv': '.csv', 'xml': ''}


def check_dataset_format(ds_format):
    """Ensure dataset format is XML or CSV"""
    if ds_format.lower() not in DATASET_FORMATS.keys():
        raise ValueError("dataset_format is expected to be one of %s. '%s' is not valid" % (
        ', '.join(DATASET_FORMATS.keys()), ds_format,))


def dataset_format_to_extension(ds_format):
    try:
        return DATASET_FORMATS[ds_format]
    except KeyError:
        raise ValueError("dataset_format is expected to be one of %s. '%s' is not valid" % (
        ', '.join(DATASET_FORMATS.keys()), ds_format,))


#-----------------------------------------------------------------------------------------------------------------------
# Classes


class CVMetaDataRequest(QueryOptionGetRequest):
    """Return Clinical View Metadata as ODM string"""
    KNOWN_QUERY_OPTIONS = ['versionitem', 'rawsuffix', 'codelistsuffix', 'decodesuffix']

    def __init__(self, project_name, environment_name, versionitem=None, rawsuffix=None, codelistsuffix=None,
                 decodesuffix=None):
        self.project_name = project_name
        self.environment_name = environment_name

        self.versionitem = versionitem
        self.rawsuffix = rawsuffix
        self.codelistsuffix = codelistsuffix
        self.decodesuffix = decodesuffix

    def studyname_environment(self):
        return "%s(%s)" % (self.project_name, self.environment_name, )


    def url_path(self):
        return self.make_url('studies', self.studyname_environment(), 'datasets', 'metadata', 'regular',
                             **self._querystring())


class FormDataRequest(QueryOptionGetRequest):
    """Return CV Form Data as CSV or XML"""
    KNOWN_QUERY_OPTIONS = ['start']

    def __init__(self, project_name, environment_name, dataset_type, form_oid, start=None, dataset_format="csv"):
        check_dataset_format(dataset_format)
        self.dataset_format = dataset_format

        self.project_name = project_name
        self.environment_name = environment_name

        self.dataset_type = dataset_type
        check_dataset_type(self.dataset_type)

        self.form_oid = form_oid

        #TODO: Check start is iso8601 date/time
        self.start = start

    def studyname_environment(self):
        return "%s(%s)" % (self.project_name, self.environment_name, )

    def _dataset_name(self):
        return '%s%s' % (self.form_oid, dataset_format_to_extension(self.dataset_format),)

    def url_path(self):
        return self.make_url('studies', self.studyname_environment(), 'datasets', self.dataset_type,
                             self._dataset_name(), **self._querystring())


class MetaDataRequest(RWSAuthorizedGetRequest):
    """Return Metadata for Clinical Views in CSV or XML fornat"""

    def __init__(self, dataset_format="csv"):
        check_dataset_format(dataset_format)
        self.dataset_format = dataset_format

    def _dataset_name(self):
        return 'ClinicalViewMetadata%s' % dataset_format_to_extension(self.dataset_format)

    def url_path(self):
        return self.make_url('datasets', self._dataset_name())


class ProjectMetaDataRequest(RWSAuthorizedGetRequest):
    """Return Metadata for Clinical Views in CSV or XML fornat for a Project"""

    def __init__(self, project_name, dataset_format="csv"):
        check_dataset_format(dataset_format)
        self.dataset_format = dataset_format.lower()
        self.project_name = project_name

    def _dataset_name(self):
        return 'ClinicalViewMetadata%s' % dataset_format_to_extension(self.dataset_format)

    def url_path(self):
        return self.make_url('datasets', self._dataset_name(), **{'ProjectName': self.project_name})


class ViewMetaDataRequest(RWSAuthorizedGetRequest):
    """Return Metadata for Clinical Views in CSV fornat for a single View"""

    def __init__(self, view_name, dataset_format="csv"):
        check_dataset_format(dataset_format)
        self.dataset_format = dataset_format.lower()
        self.view_name = view_name

    def _dataset_name(self):
        return 'ClinicalViewMetadata%s' % dataset_format_to_extension(self.dataset_format)

    def url_path(self):
        return self.make_url('datasets', self._dataset_name(), **{'ViewName': self.view_name})


class CommentDataRequest(RWSAuthorizedGetRequest):
    """Return Comments from Rave as CSV or XML"""

    def __init__(self, project_name, environment_name, dataset_format="csv"):
        check_dataset_format(dataset_format)
        self.dataset_format = dataset_format.lower()
        self.project_name = project_name
        self.environment_name = environment_name

    def studyname_environment(self):
        return "%s(%s)" % (self.project_name, self.environment_name, )

    def _dataset_name(self):
        return 'SDTMComments%s' % dataset_format_to_extension(self.dataset_format)

    def url_path(self):
        return self.make_url('datasets', self._dataset_name(), **{'studyid': self.studyname_environment()})


class ProtocolDeviationsRequest(CommentDataRequest):
    """Retrieve Protocol Deviation Information from Rave"""

    def _dataset_name(self):
        return 'SDTMProtocolDeviations%s' % dataset_format_to_extension(self.dataset_format)

    def url_path(self):
        return self.make_url('datasets', self._dataset_name(), **{'studyid': self.studyname_environment()})


class DataDictionariesRequest(CommentDataRequest):
    """Retrieve Data Dictionaries from Rave"""

    def _dataset_name(self):
        return 'SDTMDataDictionaries%s' % dataset_format_to_extension(self.dataset_format)

    def url_path(self):
        return self.make_url('datasets', self._dataset_name(), **{'studyid': self.studyname_environment()})
