.. _rws_requests:
.. index:: rws_requests

rws_requests
************

The rws_requests module contains the core RWSRequest class and a set of Request classes that are standard in all
versions of Rave Web Services for Rave.

Also part of this module:

* :ref:`architect`
* :ref:`glv`
* :ref:`working_clinical_data`
* :ref:`post_clinical_data`

rws_requests also provides additional requests in sub-modules for additional features:

* :ref:`biostats_gateway`
* :ref:`odm_adapter`


.. _version_request:
.. index:: VersionRequest

VersionRequest()
----------------

Returns the text result of calling::

    https://{ host }/RaveWebServices/version

Example::

    >>> from rwslib import RWSConnection
    >>> from rwslib.rws_requests import VersionRequest
    >>> r = RWSConnection('innovate', 'username', 'password')  #Authorization optional
    >>> r.send_request(VersionRequest())
    u'1.15.0'


.. _buildversion_request:
.. index:: BuildVersionRequest

BuildVersionRequest()
---------------------

Returns the text result of calling::

    https://{ host }/RaveWebServices/version/build

Returns a 200 response code and the internal build number.

Example::

    >>> from rwslib import RWSConnection
    >>> from rwslib.rws_requests import BuildVersionRequest
    >>> r = RWSConnection('innovate', 'username', 'password')  #Authorization optional
    >>> r.send_request(BuildVersionRequest())
    u'5.6.5.213'



.. _codename_request:
.. index:: CodeNameRequest

CodeNameRequest()
-----------------

Returns the text result of calling::

    https://{ host }/RaveWebServices/version/codename

Returns a 200 response code and the internal code name of the RWS version.

Example::

    >>> from rwslib import RWSConnection
    >>> from rwslib.rws_requests import CodeNameRequest
    >>> r = RWSConnection('innovate')  #Authorization optional
    >>> r.send_request(CodeNameRequest())
    u'Uakari'


.. _diagnostics_request:
.. index:: DiagnosticsRequest

DiagnosticsRequest()
--------------------

Returns the text result of calling::

    https://{ host }/RaveWebServices/diagnostics

Returns a 200 response code and the text *OK* if RWS self-checks pass.

Example::

    >>> from rwslib import RWSConnection
    >>> from rwslib.rws_requests import DiagnosticsRequest
    >>> r = RWSConnection('innovate', 'username', 'password')  #Authorization optional
    >>> r.send_request(DiagnosticsRequest())
    u'OK'


.. _twohundred_request:
.. index:: TwoHundredRequest

TowHundredRequest()
-------------------

Returns the html result of calling::

    https://{ host }/RaveWebServices/twohundred

Returns a 200 response code and a html document that contains information about the MAuth configuration of Rave
Web Services on this url.

Example::

    >>> from rwslib import RWSConnection
    >>> from rwslib.rws_requests import TwoHundredRequest
    >>> r = RWSConnection('innovate') #Authorization optional
    >>> r.send_request(TwoHundredRequest())
    u'<!DOCTYPE html>\r\n<html>\r\n<head><script.....


.. _cacheflush_request:
.. index:: CacheFlushRequest

CacheFlushRequest()
-------------------

Authorization is required for this method call.

Returns the text result of calling::

    https://{ host }/RaveWebServices/webservice.aspx?CacheFlush


.. warning::

    Calling CacheFlush unnecessarily causes RWS to re-load objects, causing additional resource utilization that
    could have a detrimental affect on Rave performance.


Flushes the RWS cache. Generally Rave and RWS manage their own caching. You should not need to use this method
in normal operation. Returns a  :class:`rwsobjects.RWSResponse` object with a istransactionsuccessful attribute:

Example::

    >>> from rwslib import RWSConnection
    >>> from rwslib.rws_requests import CacheFlushRequest
    >>> r = RWSConnection('innovate', 'username', 'password')  #Authorization REQUIRED
    >>> response = r.send_request(CacheFlushRequest())
    >>> response.istransactionsucessful
    True


.. _configurabledatasetrequest_request:
.. index:: ConfigurableDatasetRequest

ConfigurableDatasetRequest()
----------------------------

Authorization is required for this method call.

Returns the text result of calling::

    https://{ host }/RaveWebServices/datasets/{dataset_name}(.{dataset_format})?{params}


Sends a Configurable Dataset request to RWS.  The `dataset_format` argument is optional and is only required if the
corresponding configurable dataset requires it.  The primary use case of this is as an abstract class that the user
can subclass for their particular Configurable Dataset; the implemented class could such as validation of the
requested `dataset_format` against the list of formats accepted by the configurable dataset or by overloading the
`result` method to parse the raw response content (e.g. return a pre-parsed JSON response or a `csv.reader`).
Returns a :class:`rwsobjects.RWSResponse` object:

Example::

    >>> from rwslib import RWSConnection
    >>> from rwslib.rws_requests import ConfigurableDatasetRequest
    >>> r = RWSConnection('innovate', 'username', 'password')  #Authorization REQUIRED
    >>> response = r.send_request(ConfigurableDatasetRequest('SomeRequest', dataset_format='csv', params=dict(start='2012-02-01')))
    >>> response.text
    DataPageID,DataPointID,LastUpdated
    1234,4321,2012-12-01T12:33:00
    4334,1234,2012-12-02T12:33:00
    ...


