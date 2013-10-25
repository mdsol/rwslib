.. _odm_adapter:

ODM Adapter Requests
********************

The ODM Adapter module provides Request implementations for the Rave Web Service ODM Adapter URLs. These include:

* Clinical Audit Records Dataset
* Version Folders Dataset
* Sites Dataset
* Users Dataset
* Signature Definitions Dataset

Read more about ODM Adapter in the
`Rave Web Services documentation <http://rws-webhelp.s3.amazonaws.com/WebHelp_ENG/solutions/clinical_data_audits/index.html#odm-adapter>`_


.. _oa_auditrecords_request:
.. index:: AuditRecordsRequest

AuditRecordsRequest(project_name, environment_name)
---------------------------------------------------

Authorization is required for this request.

Returns audit data in ODM format. Since the audit trail is a large table which cannot be downloaded in a single request,
this dataset returns headers that tell you what the next page of data to request is. This allows you to make further
requests until all data from the dataset has been received.

Calls::

    https://{{ host }}/RaveWebServices/datasets/ClinicalAuditRecords.odm/?studyoid={project_name}({environment_name})&startid={startid}&per_page={per_page}

Options:

+--------------------------------+-----------------------------------------------------------------------------------+
| Option                         | Description                                                                       |
+================================+===================================================================================+
| startid=1                      | The audit ID to start on. Defaults to 1. The first Audit ID                       |
+--------------------------------+-----------------------------------------------------------------------------------+
| per_page=100                   | How many audits to return per request. Default is 100.                            |
+--------------------------------+-----------------------------------------------------------------------------------+

Example::

    >>> from rwslib import RWSConnection
    >>> from rwslib.rws_requests.odm_adapter import *
    >>> r = RWSConnection('https://innovate.mdsol.com', 'username', 'password')
    >>> audits = r.send_request(AuditRecordsRequest('SIMPLESTUDY','TEST'))
    >>> r.last_request.headers #TO SEE
    WAITING FOR A URL TO TEST THIS ON


.. _oa_versionfolders_request:
.. index:: VersionFoldersRequest

VersionFoldersRequest(project_name, environment_name)
-----------------------------------------------------

Authorization is required for this request.

Returns a dataset in ODM format which represents the folders in-use. This is useful because the standard ODM Metadata
can only return the primary Matrix (folder structure) of Rave. VersionFoldersRequest provides all possible folders.

Calls::

    https://{{ host }}/RaveWebServices/datasets/VersionFolders.odm/?studyoid={project_name}({environment_name})


Example::

    >>> from rwslib import RWSConnection
    >>> from rwslib.rws_requests.odm_adapter import *
    >>> r = RWSConnection('https://innovate.mdsol.com', 'username', 'password')
    >>> r.send_request(VersionFoldersRequest('SIMPLESTUDY','TEST'))
    WAITING FOR A URL TO TEST THIS ON




.. _oa_sites_metadata_request:
.. index:: SitesMetadataRequest

SitesMetadataRequest()
----------------------

Authorization is required for this request.

Returns an ODM AdminData document which lists all sites along with their metadata versions and effective dates.
Optionally can take a project name and an environment to filter the list only to that study/environment.

To find the current active metadata version for a study/site you will need to sort the metadata versions for the site
by the effective date and take the latest one.

Calls::

    https://{{ host }}/RaveWebServices/datasets/Sites.odm/[?studyoid={project_name}({environment_name})]


Options:

+--------------------------------+-----------------------------------------------------------------------------------+
| Option                         | Description                                                                       |
+================================+===================================================================================+
| project_name={projectname}     | Project to filter the result set to (recommended)                                 |
+--------------------------------+-----------------------------------------------------------------------------------+
| environment_name={environment} | Environment to filter the result set to                                           |
+--------------------------------+-----------------------------------------------------------------------------------+

If used, the project_name and environmen_namet must both be supplied or an error will result.

Example::

    >>> from rwslib import RWSConnection
    >>> from rwslib.rws_requests.odm_adapter import *
    >>> r = RWSConnection('https://innovate.mdsol.com', 'username', 'password')
    >>> r.send_request(SitesMetadataRequest('SIMPLESTUDY','TEST'))
    WAITING FOR A URL TO TEST THIS ON




.. _oa_users_request:
.. index:: UsersRequest

UsersRequest(project_name, environment_name)
--------------------------------------------

Authorization is required for this request.

Returns an ODM AdminData document listing all users associated with a study with optional filtering to a single
location.

Calls::

    https://{{ host }}/RaveWebServices/datasets/Users.odm/?studyoid={project_name}({environment_name})[&locationoid={locationoid}]


Options:

+--------------------------------+-----------------------------------------------------------------------------------+
| Option                         | Description                                                                       |
+================================+===================================================================================+
| locationoid                    | A site number from Rave that uniquely identifies a site                           |
+--------------------------------+-----------------------------------------------------------------------------------+


Example::

    >>> from rwslib import RWSConnection
    >>> from rwslib.rws_requests.odm_adapter import *
    >>> r = RWSConnection('https://innovate.mdsol.com', 'username', 'password')
    >>> r.send_request(UsersRequest('SIMPLESTUDY','TEST'))
    WAITING FOR A URL TO TEST THIS ON






.. _oa_signature_defs_request:
.. index:: SignatureDefinitionsRequest

SignatureDefinitionsRequest(project_name, environment_name)
-----------------------------------------------------------

Authorization is required for this request.

Returns an ODM AdminData document listing the definition of all signatures for this study. This allows you to match
signature audits to their definitions and know in what context a signature was being made.

Calls::

    https://{{ host }}/RaveWebServices/datasets/Signatures.odm/?studyoid={project_name}({environment_name})


Example::

    >>> from rwslib import RWSConnection
    >>> from rwslib.rws_requests.odm_adapter import *
    >>> r = RWSConnection('https://innovate.mdsol.com', 'username', 'password')
    >>> r.send_request(SignatureDefinitionsRequest('SIMPLESTUDY','TEST'))
    WAITING FOR A URL TO TEST THIS ON


