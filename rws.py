__author__ = 'isparks'
import requests
from urllib import urlencode



from rwsobjects import RWSException, RWSError, RWSStudies, RWSStudyMetadataVersions, RWSSubjects, RWSErrorResponse
from rwsobjects import ODM_NS, parseXMLString #TODO: Consider moving this elsewhere

"""
Design thoughts are that you shouldn't be completely separated from the fact that you are making
requests to web-services. That could lead you to some bad behaviour.

So maybe RWS should be more like a factory which returns results. e.g.:

rws = RWSDConnection("http://...")

version_request = rws.versionRequest()

version_request() #Executes it. Then you can ask for result, headers etc. Which makes it not that much
#different from the request object.

#Another way to do this is:

rws = RWSConnectio("http://....")
version_number = rws.getVersion() #Just the result I want.
rws.last_request.headers (get information on the last request, so I can get if I need it.)



"""

# rave = RWSConnection(domain)
# rave.getVersion()  #1.6.1
#
# rave.studies: (list of study proxy objects which can then be looked at more deeply)
#
#
EMPTY_ITEMS = [None,'']

class RWSConnection(object):
    """A connection to RWS"""

    def __init__(self, domain, username=None, password=None):
        """Create a connection to Rave"""
        self.domain = domain
        self.username = username
        self.password = password


        self.base_url = self.domain + '/RaveWebServices'

        #Keep track of results of last request so users can get if they need.
        self.last_result = None

    def _make_url(self, *args, **kwargs):
        """Makes a URL from component parts"""
        base = '/'.join(args)
        if kwargs:
            return "%s?%s" % (base, urlencode(kwargs),)
        else:
            return base



    def execute(self, action, *args, **kwargs):
        """Dispatches web request, captures last result and timings"""
        r = action(*args, **kwargs)
        self.last_result = r

        if r.status_code == 404:
            #Is it a RWS response?
            if r.text.startswith('<Response'):
                error = RWSErrorResponse(r.text)
            raise RWSException(error.errordescription, error)

        return r

    def get_auth(self):
        """Get authorization headers"""
        return (self.username, self.password,)

    def _get(self, **kwargs):
        """
        Wraps a get request:

        Requires:

        url (the base URL to call, domain and RaveWebServices endpoint will be added)
        auth=True (default to false if not present, whether to add basic auth to this request)

        """
        if not 'url' in kwargs:
            raise AttributeError('No url set')
        else:
            url = self._make_url(self.base_url, kwargs['url'])
            del kwargs['url']

        #Add authorization headers?
        if 'auth' in kwargs:
            if kwargs['auth'] == True:
                kwargs['auth'] = self.get_auth()
            else:
                #Remove from request
                del kwargs['auth']

        #Do the execution
        r = self.execute(requests.get,url,**kwargs)

        #Check authorization was not required
        if r.text == 'Authorization Header not provided':
            raise Exception(r.text)

        if r.status_code != 200:
            error = RWSError(r.text)
            raise RWSException(error.errordescription, error)

        return r

    def version(self):
        """Return the RWS version number."""
        r = self._get(url='version')
        return r.text


    def studies(self):
        """Return the list of studies"""
        r = self._get(url='studies', auth=True)

        if r.status_code != 200:
            error = RWSError(r.text)
            raise RWSException(error.errordescription, error)

        return RWSStudies(r.text)


    def study_drafts(self, protocolname):
        """Return the list of study drafts"""
        #https://partner.mdsol.com/RaveWebServices/metadata/studies/IANTEST/drafts

        url = self._make_url('metadata','studies',protocolname,'drafts')

        r = self._get(url=url, auth=True)

        return RWSStudyMetadataVersions(r.text)

    def study_versions(self, protocolname):
        """Return the list of study versions"""
        #https://partner.mdsol.com/RaveWebServices/metadata/studies/IANTEST/versions

        url = self._make_url('metadata','studies',protocolname,'versions')

        r = self._get(url=url, auth=True)

        return RWSStudyMetadataVersions(r.text)


    def study_version(self, protocolname, versionoid):
        """Return the text of a study version

        https://{{ host}}.mdsol.com/RaveWebServices/metadata/studies/{{ protocol_name }}/versions/{{ version_oid }}
        """

        url = self._make_url('metadata','studies',protocolname,'versions',str(versionoid))

        r = self._get(url=url, auth=True)

        return r.text


    def ensure_no_environment_in_protocol_name(self, studyname):
        """Check that environment name has not been mixed into study name"""
        if "(" in studyname:
            raise ValueError("Environment included in study name, ( detected")


    def ensure_no_parens_in_environment_name(self, environment_name):
        """Check that environment name has not been provided with parens in it"""
        if "(" in environment_name:
            raise ValueError("Environment should not include parenthesis! e.g. 'Dev' not '(Dev)'")

    def make_study_name_from_protocolname_and_environment(self, protocolname, environment_name):
        """Given a protocol name an environment name, make a study name string"""
        studyname_environment = protocolname
        if environment_name != '':
            studyname_environment = "%s(%s)" % (protocolname, environment_name)
        return studyname_environment


    def study_subjects(self, protocolname, environment_name=''):
        """
        Return the list of study subjects
           https://partner.mdsol.com/RaveWebServices/studies/Fixitol(Dev)/subjects
        """

        self.ensure_no_environment_in_protocol_name(protocolname)
        self.ensure_no_parens_in_environment_name(environment_name)

        studyname_environment = self.make_study_name_from_protocolname_and_environment(protocolname, environment_name)


        url = self._make_url('studies',studyname_environment,'subjects',links="all") #status="all" -Not convinced of value of status

        r = self._get(url=url, auth=True)

        return RWSSubjects(r.text)

    def study_datasets(self, protocol_name, environment_name='', ds_type='regular', rawsuffix=None):
        """
        Return the text of the full datasets listing as an ODM string
           https://{{ host }}.mdsol.com/RaveWebServices/studies/{{ protocol_name }} ({{ environment_name}})/datasets/regular
        """

        if ds_type not in ['regular','raw']:
            raise ValueError("Dataset type not regular or raw")



        self.ensure_no_environment_in_protocol_name(protocol_name)
        self.ensure_no_parens_in_environment_name(environment_name)

        studyname_environment = self.make_study_name_from_protocolname_and_environment(protocol_name, environment_name)

        kwargs = {}

        if rawsuffix is not None:
            kwargs['rawsuffix'] = rawsuffix

        url = self._make_url('studies',studyname_environment,'datasets',ds_type, **kwargs)

        r = self._get(url=url, auth=True)

        return r.text



if __name__ == '__main__':

    from _settings import username, password #Not exactly 12 factor, but a start
    rave = RWSConnection('https://innovate.mdsol.com', username, password)

    studyname = 'Mediflex' #IANTEST

    # print rave.version()
    #
    # print rave.last_result.url
    # print rave.last_result.status_code
    # print rave.last_result.headers['content-type']
    # print rave.last_result.text


    # try:
    #     for study in rave.studies():
    #         print study.studyname
    #         print study.environment
    #         print study.isProd()
    #     print rave.last_result.headers['content-type']
    # except RWSException, e:
    #     print e.rws_error.creationdatetime




    # #print rave.last_result.headers
    # #print rave.last_result.status_code
    #
    # drafts = rave.study_drafts(studyname)
    #
    # print drafts.fileoid
    # print drafts.study.studyname
    #
    # for version in drafts:
    #     print version.name, version.oid
    #     print dir(version)

    versions = rave.study_versions(studyname)
    print versions.fileoid
    print versions.study.studyname
    for version in versions:
        print version.name, version.oid


    print rave.study_version(studyname,1015)

    #Stopping here....
    import sys; sys.exit()

    val = rave.study_datasets(studyname,'Dev', ds_type='regular', rawsuffix='.RAW')
    doc = parseXMLString(val)

    ns = {"odm": ODM_NS[1:-1]}

    form_nodes = doc.xpath('/odm:ODM/odm:ClinicalData/odm:SubjectData/odm:StudyEventData/odm:FormData', namespaces=ns)
    print len(form_nodes)
    counts = {}
    for node in form_nodes:
        oid = node.get('FormOID')
        cnt = counts.get(oid, 0)
        cnt += 1
        counts[oid] = cnt

    print counts


    #print doc.findall(ODM_NS + 'ClinicalData') #)/SubjectData/StudyEventData/FormData')

    #
    # for subject in rave.study_subjects('IANTEST'):
    #     print subject.locationoid
    #     print subject.subjectkey
    #     print subject.metadataversionoid
    #     print subject.studyoid
    # #print rave.last_result.text
    # print dir(rave.last_result)
    print rave.last_result.url
    # print rave.last_result.elapsed
    #rave.make_request_for("Study", "Environment", "Site", "Subject")
    #How do I know which MetaDataVersion applies?


