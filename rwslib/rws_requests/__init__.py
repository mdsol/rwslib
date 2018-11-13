"""
Core request classes that implement calls available in all versions of RWS.

RWSRequest subclasses represent URL endpoints. They can be passed to a RWSConnection get or post method
as appropriate.

TODO: Note that might want to make the Request objects responsible for deciding whether they are get, post, patch etc.

"""
import datetime

from rwslib.rwsobjects import (
    RWSResponse,
    RWSStudies,
    RWSStudyMetadataVersions,
    RWSSubjects,
    RWSPostResponse,
)
from six.moves.urllib_parse import urlencode


# -----------------------------------------------------------------------------------------------------------------------
# Function utilities I don't want to muddy class heirarchy with


def check_dataset_type(dataset_type):
    """
    Datasets may only be regular or raw
    :type dataset_type: str
    """
    if dataset_type.lower() not in ["regular", "raw"]:
        raise ValueError("Dataset type not 'regular' or 'raw' is %s" % dataset_type)


def format_date_argument(date_element):
    """
    Take a date as either a datetime.date/datetime or a string and return it as a iso8601 formatted value
    :param Union[datetime.date, datetime.datetime] date_element: passed argument
    :rtype str
    :return:
    """
    if not isinstance(date_element, (datetime.datetime, datetime.date)):
        # TODO:
        if "T" in date_element:
            _date = datetime.datetime.strptime(date_element, "%Y-%m-%dT%H:%M:%S")
        else:
            _date = datetime.datetime.strptime(date_element, "%Y-%m-%d").date()
    else:
        _date = date_element
    return _date.isoformat()


# -------------------------------------------------------------------------------------------------------
# Utility functions
#
def make_url(*args, **kwargs):
    """Makes a URL from component parts"""
    base = "/".join(args)
    if kwargs:
        return "%s?%s" % (base, urlencode(kwargs))
    else:
        return base


class RWSRequest(object):
    """Base class for all RWS Requests"""

    requires_authorization = False
    method = "GET"  # Default

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def result(self, response):
        """
        Process a result to create a custom output
        :param requests.models.Response response: returned response
        :return:
        """
        # By default return text
        return response.text

    def url_path(self):
        """Return url path list"""
        raise NotImplementedError(
            "Override url_path in descendants of RWSRequest"
        )  # pragma: no cover

    def args(self):
        """Return additional args here as dict"""
        return {}

    def make_url(self, *args, **kwargs):
        # Note: Including this in the class as a convenience so that you can get all you need from a RWSObject rather
        # than having to import make_url as an additional import.
        return make_url(*args, **kwargs)


# -----------------------------------------------------------------------------------------------------------------------
# Useful subclasses
# -----------------------------------------------------------------------------------------------------------------------


class RWSGetRequest(RWSRequest):
    method = "GET"


class RWSAuthorizedGetRequest(RWSGetRequest):
    requires_authorization = True


class RWSPostRequest(RWSRequest):
    method = "POST"


class RWSAuthorizedPostRequest(RWSPostRequest):
    requires_authorization = True


class QueryOptionGetRequest(RWSAuthorizedGetRequest):
    """Manages requests that have known query string options"""

    KNOWN_QUERY_OPTIONS = []

    def _querystring(self):
        """Get additional keyword arguments"""

        kw = {}
        for key in self.KNOWN_QUERY_OPTIONS:
            val = getattr(self, key)
            if val is not None:
                kw[key] = val
        return kw


# ---------------------------------------------------------------------------------------------------------------------
# Implementations. These are all standards that have existed for a long time.
# ---------------------------------------------------------------------------------------------------------------------


class VersionRequest(RWSGetRequest):
    """Get RWS Version number"""

    def url_path(self):
        return make_url("version")


class BuildVersionRequest(RWSGetRequest):
    """Return the RWS build version number"""

    def url_path(self):
        return make_url("version", "build")


class CodeNameRequest(RWSGetRequest):
    """Return the RWS version codename"""

    def url_path(self):
        return make_url("version", "codename")


class DiagnosticsRequest(RWSGetRequest):
    """Return the RWS build version number"""

    def url_path(self):
        return make_url("diagnostics")


class TwoHundredRequest(RWSGetRequest):
    """Return RWS MAuth information"""

    def url_path(self):
        return make_url("twohundred")


class CacheFlushRequest(RWSAuthorizedGetRequest):
    """Calls RWS cache-flush"""

    def url_path(self):
        return make_url("webservice.aspx?CacheFlush")

    def result(self, response):
        """
        Return RWSResponse object for success
        :param requests.models.Response response: request respnse
        """
        return RWSResponse(response.text)


class ClinicalStudiesRequest(RWSAuthorizedGetRequest):
    """Return the list of clinical studies as a RWSStudies object.
       Clinical studies are the studies that you have access to as an EDC user.
    """

    def url_path(self):
        return make_url("studies")

    def result(self, response):
        """
        Return RWSResponse object for success
        :param requests.models.Response response: request respnse
        """
        return RWSStudies(response.text)


# ----------------------------------------------------------------------------------------------------------------------
# Base request classes for study versions (could also be used for drafts if ever implemented by RWS)
# ----------------------------------------------------------------------------------------------------------------------


class VersionRequestBase(RWSAuthorizedGetRequest):
    """Base class for study and library metadata version requests"""

    def __init__(self, project_name, oid):
        """
        :param str project_name: Project Name
        :param int oid: Metadata version OID (CRF Draft Number)
        """
        self.project_name = project_name
        self._oid = None  # Oid is a version OID, an integer identifier
        self.oid = oid

    @property
    def oid(self):
        return self._oid

    @oid.setter
    def oid(self, value):
        try:
            int(value)
        except ValueError:
            raise ValueError("oid must be an integer")
        self._oid = value

    def result(self, response):
        """
        Return RWSResponse object for success
        :param requests.models.Response response: request respnse
        """
        return response.text


# -----------------------------------------------------------------------------------------------------------------------
# Related to Architect Studies and their drafts/versions
# -----------------------------------------------------------------------------------------------------------------------


class MetadataStudiesRequest(RWSAuthorizedGetRequest):
    """Return the list of metadata studies as a RWSStudies object.
       metadata_studies are the list of studies that you have access to as an
       Architect user.
    """

    def url_path(self):
        return make_url("metadata", "studies")

    def result(self, response):
        """
        Return RWSResponse object for success
        :param requests.models.Response response: request respnse
        """
        return RWSStudies(response.text)


class StudyDraftsRequest(RWSAuthorizedGetRequest):
    """Return the list of study drafts"""

    def __init__(self, project_name):
        """
        :param str project_name: Project Name
        """
        self.project_name = project_name

    def url_path(self):
        return make_url("metadata", "studies", self.project_name, "drafts")

    def result(self, response):
        """
        Return RWSResponse object for success
        :param requests.models.Response response: request respnse
        """
        return RWSStudyMetadataVersions(response.text)


class StudyVersionsRequest(RWSAuthorizedGetRequest):
    """Return the list of study versions"""

    def __init__(self, project_name):
        """
        :param str project_name: Project Name
        """
        self.project_name = project_name

    def url_path(self):
        return make_url("metadata", "studies", self.project_name, "versions")

    def result(self, response):
        """
        Return RWSResponse object for success
        :param requests.models.Response response: request respnse
        """
        return RWSStudyMetadataVersions(response.text)


class StudyVersionRequest(VersionRequestBase):
    """Return a study version as a string"""

    def url_path(self):
        return make_url(
            "metadata", "studies", self.project_name, "versions", str(self._oid)
        )


# NOTE: There is no StudyDraftRequest, this is something of an omission since you can list them...


# -------------------------------------------------------------------------------------------------
# Related to Architect Global Libraries and their drafts/versions
# -------------------------------------------------------------------------------------------------


class GlobalLibrariesRequest(RWSAuthorizedGetRequest):
    """Return the list of global libraries as a RWSStudies object.
       metadata_libraries are the list of libraries that you have access to as an
       Architect Global Library Volume user
    """

    def url_path(self):
        return make_url("metadata", "libraries")

    def result(self, response):
        """
        Return RWSResponse object for success
        :param requests.models.Response response: request respnse
        """
        return RWSStudies(response.text)


class GlobalLibraryDraftsRequest(RWSAuthorizedGetRequest):
    """Return the list of global library drafts"""

    def __init__(self, project_name):
        """
        :param str project_name: Project Name
        """
        self.project_name = project_name

    def url_path(self):
        return make_url("metadata", "libraries", self.project_name, "drafts")

    def result(self, response):
        """
        Return RWSResponse object for success
        :param requests.models.Response response: request respnse
        """
        return RWSStudyMetadataVersions(response.text)


class GlobalLibraryVersionsRequest(RWSAuthorizedGetRequest):
    """Return the list of global library versions"""

    def __init__(self, project_name):
        """
        :param str project_name: Project Name
        """
        self.project_name = project_name

    def url_path(self):
        return make_url("metadata", "libraries", self.project_name, "versions")

    def result(self, response):
        """
        Return RWSResponse object for success
        :param requests.models.Response response: request respnse
        """
        return RWSStudyMetadataVersions(response.text)


class GlobalLibraryVersionRequest(VersionRequestBase):
    """Return a global library version as a string"""

    def url_path(self):
        return make_url(
            "metadata", "libraries", self.project_name, "versions", str(self._oid)
        )


class PostMetadataRequest(RWSAuthorizedPostRequest):
    """Post an ODM data transaction to Rave, get back an RWSResponse object"""

    def __init__(self, project_name, data, headers={"Content-type": "text/xml"}):
        """
        :param str project_name: Project Name
        :param str data: Data to dispatch
        :param dict headers: Headers to pass to client
        """
        self.project_name = project_name
        self.data = data
        self.headers = headers

    def args(self):
        """Return additional args here as dict (only for post data requests)"""
        kw = {"data": self.data, "headers": self.headers}
        return kw

    def url_path(self):
        return make_url("metadata", "studies", self.project_name, "drafts")

    def result(self, response):
        """
        Return RWSPostResponse object for success
        :param requests.models.Response response: request respnse
        """
        return RWSPostResponse(response.text)


# -------------------------------------------------------------------------------------------------
# Subject related
# -------------------------------------------------------------------------------------------------


class StudySubjectsRequest(RWSAuthorizedGetRequest):
    """
    Return the list of study subjects, defaults to the PROD environment
    """

    SUBJECT_KEY_TYPES = ["SubjectName", "SubjectUUID"]
    INCLUDE_OPTIONS = ["inactive", "deleted", "inactiveAndDeleted"]

    def __init__(
        self,
        project_name,
        environment_name,
        status=False,
        include=None,
        subject_key_type="SubjectName",
        links=False,
    ):
        """
        :param str project_name: Project/Study Name
        :param str environment_name: Study Environment Name (eg `Prod`)
        :param bool status: Add subject level workflow status
        :param str include: Query option to add to `include` parameter (see INCLUDE_OPTIONS for allowed values)
        :param str subject_key_type: Type of SubjectKey to have in the response (one of `SubjectName` or `SubjectUUID`)
        :param bool links: Add Deep Links to Output ODM

        .. note::
            If status == True then ?status=all
            If include then include parameter is also added to query string

        """

        self.project_name = project_name
        self.environment_name = environment_name
        self.status = status
        self.links = links
        self.include = None
        self.subject_key_type = subject_key_type
        # make sure the value for SubjectKeyType makes sense.
        if self.subject_key_type not in self.SUBJECT_KEY_TYPES:
            raise ValueError(
                "SubjectKeyType {} is not a valid value".format(self.subject_key_type)
            )

        if include is not None:
            if include not in self.INCLUDE_OPTIONS:
                raise ValueError(
                    "If provided, included must be one of %s"
                    % ",".join(self.INCLUDE_OPTIONS)
                )
        self.include = include

    def _querystring(self):
        """Additional keyword arguments"""
        kw = {}
        if self.status:
            kw["status"] = "all"

        if self.links:
            kw["links"] = "all"

        if self.include is not None:
            kw["include"] = self.include
        if self.subject_key_type != "SubjectName":
            kw["subjectKeyType"] = self.subject_key_type
        return kw

    def studyname_environment(self):
        return "%s(%s)" % (self.project_name, self.environment_name)

    def url_path(self):
        return make_url(
            "studies", self.studyname_environment(), "subjects", **self._querystring()
        )

    def result(self, response):
        """
        Return RWSSubjects object for success
        :param requests.models.Response response: request response
        """
        return RWSSubjects(response.text)


class PostDataRequest(RWSAuthorizedPostRequest):
    """Post an ODM data transaction to Rave, get back an RWSResponse object"""

    def __init__(self, data, headers={"Content-type": "text/xml"}):
        """
        Post an ODM to a RWS endpoint
        :param bytes data: Data to POST
        :param dict headers: Headers to add to request
        """
        self.data = data
        self.headers = headers

    def args(self):
        """Return additional args here as dict (only for post data requests)"""
        kw = {"data": self.data, "headers": self.headers}
        return kw

    def url_path(self):
        """
        Generate the Target Endpoint
        :return: Generated Endpoint
        """
        return make_url("webservice.aspx?PostODMClinicalData")

    def result(self, response):
        """
        Return RWSPostResponse object for success
        :param requests.models.Response response: request response
        """
        return RWSPostResponse(response.text)


# -------------------------------------------------------------------------------------------------
# ODM Clinical Data Datasets
# -------------------------------------------------------------------------------------------------


class ODMDatasetBase(RWSAuthorizedGetRequest):
    KNOWN_QUERY_OPTIONS = [
        "versionitem",
        "rawsuffix",
        "codelistsuffix",
        "decodesuffix",
        "stdsuffix",
        "start",
    ]

    def checkParams(self):
        check_dataset_type(self.dataset_type)
        # https://bitbucket.org/micktwomey/pyiso8601

    def _querystring(self):
        """Additional keyword arguments"""

        kw = {}

        for key in self.KNOWN_QUERY_OPTIONS:
            val = getattr(self, key)
            if val is not None:
                if key == "start":
                    # special case the date formatting
                    # this will raise a ValueError
                    # if the date format is a string and not one of
                    # YYYY-mm-ddTHH:MM:SS or YYYY-mm-dd
                    kw[key] = format_date_argument(val)
                else:
                    kw[key] = val
        return kw

    def _studyname_environment(self):
        return "%s(%s)" % (self.project_name, self.environment_name)


class StudyDatasetRequest(ODMDatasetBase):
    """Return the text of the full datasets listing as an ODM string."""

    def __init__(
        self,
        project_name,
        environment_name,
        dataset_type="regular",
        start=None,
        rawsuffix=None,
        formoid=None,
        versionitem=None,
        codelistsuffix=None,
        decodesuffix=None,
        stdsuffix=None,
    ):
        """
        :param str project_name: Name of the Rave Study
        :param str environment_name: Name of the Rave Study Environment
        :param str dataset_type: Dataset type, one of 'regular' or 'raw'
        :param str start: Start date for the Report (iso8601)
        :param str rawsuffix: Adds raw data values to a full or incremental dataset, and identifies these
            values with {rawsuffix}.
        :param str formoid: FormOID for which to report
        :param str versionitem: Adds the subject's CRF version to the dataset, and identifies it with {version-item}
        :param str codelistsuffix: Adds code list OIDS for fields that use a code list to the dataset,
            and identifies these values with {codelistsuffix}.
        :param str decodesuffix: Add decoded values of items that have an associated code list to the dataset,
            and identifies these values with {decodesuffix}.
        :param str stdsuffix: Adds standard data values to a full or incremental dataset, and identifies these
            values with {stdsuffix}.
        """
        self.project_name = project_name
        self.environment_name = environment_name

        self.dataset_type = dataset_type.lower()
        self.formoid = formoid

        self.rawsuffix = rawsuffix
        self.start = start
        self.versionitem = versionitem
        self.codelistsuffix = codelistsuffix
        self.decodesuffix = decodesuffix
        self.stdsuffix = stdsuffix

        self.checkParams()

    def url_path(self):
        args = ["studies", self._studyname_environment(), "datasets", self.dataset_type]
        if self.formoid is not None:
            args.append(self.formoid)

        return make_url(*args, **self._querystring())


class VersionDatasetRequest(ODMDatasetBase):
    """
    Return the text of the full datasets for a version as an ODM string.
    By supplying formoid, will be filtered to just that formoid data
    """

    def __init__(
        self,
        project_name,
        environment_name,
        version_oid,
        dataset_type="regular",
        start=None,
        rawsuffix=None,
        formoid=None,
        versionitem=None,
        codelistsuffix=None,
        decodesuffix=None,
        stdsuffix=None,
    ):
        """
        :param str project_name: Name of the Rave Study
        :param str environment_name: Name of the Rave Study Environment
        :param str dataset_type: Dataset type, one of 'regular' or 'raw'
        :param str start: Start date for the Report (iso8601)
        :param str rawsuffix: Adds raw data values to a full or incremental dataset, and identifies these
            values with {rawsuffix}.
        :param str formoid: FormOID for which to report
        :param str versionitem: Adds the subject's CRF version to the dataset, and identifies it with {version-item}
        :param str codelistsuffix: Adds code list OIDS for fields that use a code list to the dataset,
            and identifies these values with {codelistsuffix}.
        :param str decodesuffix: Add decoded values of items that have an associated code list to the dataset,
            and identifies these values with {decodesuffix}.
        :param str stdsuffix: Adds standard data values to a full or incremental dataset, and identifies these
            values with {stdsuffix}.
        :param str version_oid: version for which to report
        """
        self.project_name = project_name
        self.environment_name = environment_name
        self.version_oid = version_oid

        self.dataset_type = dataset_type.lower()
        self.formoid = formoid

        self.rawsuffix = rawsuffix
        self.start = start
        self.versionitem = versionitem
        self.codelistsuffix = codelistsuffix
        self.decodesuffix = decodesuffix
        self.stdsuffix = stdsuffix

        self.checkParams()

    def url_path(self):
        args = [
            "studies",
            self._studyname_environment(),
            "versions",
            str(self.version_oid),
            "datasets",
            self.dataset_type,
        ]
        if self.formoid is not None:
            args.append(self.formoid)

        return make_url(*args, **self._querystring())


class SubjectDatasetRequest(ODMDatasetBase):
    """
    Return the text of the full datasets for a version as an ODM string.
    By supplying formoid, will be filtered to just that formoid data
    """

    def __init__(
        self,
        project_name,
        environment_name,
        subjectkey,
        dataset_type="regular",
        start=None,
        rawsuffix=None,
        formoid=None,
        versionitem=None,
        codelistsuffix=None,
        decodesuffix=None,
        stdsuffix=None,
    ):
        """
        :param str project_name: Name of the Rave Study
        :param str environment_name: Name of the Rave Study Environment
        :param str dataset_type: Dataset type, one of 'regular' or 'raw'
        :param str start: Start date for the Report (iso8601)
        :param str rawsuffix: Adds raw data values to a full or incremental dataset, and identifies these
            values with {rawsuffix}.
        :param str formoid: FormOID for which to report
        :param str versionitem: Adds the subject's CRF version to the dataset, and identifies it with {version-item}
        :param str codelistsuffix: Adds code list OIDS for fields that use a code list to the dataset,
            and identifies these values with {codelistsuffix}.
        :param str decodesuffix: Add decoded values of items that have an associated code list to the dataset,
            and identifies these values with {decodesuffix}.
        :param str stdsuffix: Adds standard data values to a full or incremental dataset, and identifies these
            values with {stdsuffix}.
        :param str subjectkey: Subject Key for subject for which to report
        """
        self.project_name = project_name
        self.environment_name = environment_name
        self.subjectkey = subjectkey

        self.dataset_type = dataset_type.lower()
        self.formoid = formoid

        self.rawsuffix = rawsuffix
        self.start = start
        self.versionitem = versionitem
        self.codelistsuffix = codelistsuffix
        self.decodesuffix = decodesuffix
        self.stdsuffix = stdsuffix

        self.checkParams()

    def url_path(self):
        args = [
            "studies",
            self._studyname_environment(),
            "subjects",
            str(self.subjectkey),
            "datasets",
            self.dataset_type,
        ]
        if self.formoid is not None:
            args.append(self.formoid)

        return make_url(*args, **self._querystring())


class ConfigurableDatasetRequest(RWSAuthorizedGetRequest):
    VALID_DATASET_FORMATS = ()

    def __init__(self, dataset_name, dataset_format="", params={}):
        """
        Create a new Configurable Dataset Request
        :param dataset_name: Name for the dataset
        :type dataset_name: str
        :param dataset_format: Format for the dataset
        :type dataset_format: str
        :param params: set of parameters to pass to URL
        :type params: dict
        """
        self.dataset_name = dataset_name
        if self.VALID_DATASET_FORMATS:
            if dataset_format and dataset_format not in self.VALID_DATASET_FORMATS:
                raise ValueError(
                    "Dataset format %s is not valid for %s"
                    % (dataset_format, dataset_name)
                )
        self.dataset_format = dataset_format
        self.params = params

    @property
    def dataset(self):
        """
        Qualify the dataset_name with the dataset_format if supplied
        :return: dataset name
        :rtype: str
        """
        if self.dataset_format:
            return ".".join([self.dataset_name, self.dataset_format])
        return self.dataset_name

    def url_path(self):
        """
        Get the correct URL Path for the Dataset
        :return:
        """
        args = ["datasets", self.dataset]
        return make_url(*args, **self.params)
