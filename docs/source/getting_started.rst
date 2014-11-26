Getting started
***************

Note that for any API calls that require authentication (anything useful) you will need access to a Rave environment.
Medidata runs a program for integration access to this system, *Developer Central*.
`Apply for access <https://www.mdsol.com/en/who-we-are/clients-partners/developer-central/>`_

Installation
------------

We strongly recommend working within a virtual environment with
`Virtualenv <http://virtualenv.readthedocs.org/en/latest/virtualenv.html/>`_.

Install with pip::

    $ pip install rwslib

Or directly from github with::

    $ pip install git+https://github.com/mdsol/rwslib.git

This will also install all required dependencies. Note that on Windows, lxml requires a binary installation.

Creating a connection to RWS
----------------------------

Before you can do any work with rwslib you must create a connection to a Rave instance. This is done
through the RWSConnection object::

    >>> from rwslib import RWSConnection
    >>> rws = RWSConnection('innovate', 'my_username','my_password')

Note that the first parameter to the RWSConnection is the name of the url you wish to connect to. A url
that does not start with "http" is assumed to be the sub-domain of mdsol.com. In the example above "innovate"
is treated as ``https://innovate.mdsol.com.``

If you wish to override this behaviour, supply a base URL that includes http or https at the start of
the url::

    >>> rws = RWSConnection('http://192.168.1.99', 'my_username','my_password')

It is important to understand that an RWSConnection is not a persistent connection to Rave, it is simply
a convenience class for making calls to RWS endpoints.

Making an RWS request
---------------------

Once you have an RWSConnection, you can use it to send messages to Rave and receive results back.

rwslib provides a set of request classes. To make a request, create an instance of that request type and pass it to the
RWSConnection ``send_request`` method::

    >>> from rwslib import RWSConnection
    >>> rws = RWSConnection('innovate', 'my_username','my_password')
    >>> from rwslib.rws_requests import VersionRequest
    >>> rws.send_request(VersionRequest())
    1.8.0

The result you get back from send_request will depend on the request type since Request objects have the chance to
process the text values returned from Rave. ``VersionRequest()`` returns a string value but other request types may
return objects or collections (python lists) of objects.

All Request classes are descendants of the ``RWSRequest`` class. The API is designed this way so that new or custom
requests can be easily added to the library. This also allows for easier versioning of requests and also subclassing of
existing request types. For instance, ``VersionRequest()`` could be subclassed to return major, minor and patch-level values
as a tuple of integers rather than as a string. This allows you to make specialized request classes for your integration.

rwslib provides several sets of syamdard request types arranged into python units:

* ``rws_requests.py`` contains the RWSRequest class and standard requests like ``VersionRequest()``
* ``rws_cv_requests.py`` contains requests related to Rave Clinical Views and BioStat Gateway data extracts for Comments and Protocol Violations
* ``odm_adapter_requests.py`` contains requests related to the ODM Adapter datasets added in Rave 2013.3.0


Authentication
--------------

Most requests require authentication. There are some that do not, ``VersionRequest()`` is one of those that does not
require authentication so this is also valid::

    >>> from rwslib import RWSConnection
    >>> from rwslib.rws_requests import VersionRequest
    >>> rws = RWSConnection('https://innovate.mdsol.com')

    >>> #Get the rave version from rws
    >>> rws.send_request(VersionRequest())
    1.8.0

Generally you will want to provide credentials to authenticate with Rave.


Timeouts
--------

By default rwslib will not timeout.   A timeout limit, in seconds, can be set on send_request,
after which a Timeout exception will be thrown:

    >>> from rwslib import RWSConnection
    >>> rws = RWSConnection('innovate', 'my_username','my_password')
    >>> #Get the rave version from rws
    >>> rws.send_request(VersionRequest(),timeout=1)

In practice the timeout should be set to a value greater than any expected valid response time,
which will vary depending upon the request types and volumes of data sent or received.

This timeout setting only applies to rwslib and does not alter timeouts in RWS itself or any other component in the
network such as load balancers, etc.



Getting more information from last_result
-----------------------------------------

Each time ``RWSConnection`` sends a request and receives results it keeps the result of the RWS call in it's
``last_result`` attribute. This is very useful for debugging RWS calls since it allows you to find out what headers
were sent, what URL was called etc.

    >>> from rwslib import RWSConnection
    >>> from rwslib.rws_requests import VersionRequest
    >>> rws = RWSConnection('innovate')
    >>> #Get the rave version from rws
    >>> rws.send_request(VersionRequest())
    1.8.0
    >>> rws.last_result.url
    https://innovate.mdsol.com/RaveWebServices/version
    >>> rws.last_result.status_code
    200
    >>> rws.last_result.headers['content-type']
    text/plain; charset=utf-8
    >>> rws.last_result.text
    1.8.0

``last_result`` is a `Requests <http://docs.python-requests.org/>`_ object. Please see that library for more
information on all the properties that can be returned there.

Having access to ``last_result`` means that rwslib never hides it's workings from you. rwslib is intended to
be a helper library to get your own integrations up and running, it tries not to hide implementation
details from you.

Getting the elapsed time of the request
---------------------------------------

Each time ``RWSConnection`` sends a request and receives results it keeps the elapsed time, in seconds, of the RWS call
in it's ``request_time`` attribute.

    >>> from rwslib import RWSConnection
    >>> from rwslib.rws_requests import VersionRequest
    >>> rws = RWSConnection('innovate')
    >>> #Get the rave version from rws
    >>> rws.send_request(VersionRequest())
    1.8.0
    >>> #Get the elapsed time in seconds to process the previous request
    >>> rws.request_time
    0.760736942291

Error Handling
--------------

RWS returns a variety of error results depending on the type of request. rwslib packages these error types into

:class:`rwsobjects.RWSException` exceptions which have an ``rws_error`` property. The rws_error property is populated with
a different object type depending on the error type.

Where RWS returns an XML error response, rwslib will parse the error and return it in an :class:`rwsobjects.RWSError` or
:class:`rwsobjects.RWSErrorResponse` object.

``RWSError`` instances have an
``errordescription`` attribute while ``RWSErrorResponse`` have an ``errordescription`` and a ``reasoncode``.

``RWSError`` is used to parse ODM-formatted return messages like::

    <?xml version="1.0" encoding="utf-8"?>
    <ODM xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata"
         FileType="Snapshot"
         CreationDateTime="2013-04-08T10:28:49.578-00:00"
         FileOID="4d13722a-ceb6-4419-a917-b6ad5d0bc30e"
         ODMVersion="1.3"
         mdsol:ErrorDescription="Incorrect login and password combination. [RWS00008]"
         xmlns="http://www.cdisc.org/ns/odm/v1.3" />


``RWSErrorResponse`` parses simple XML return messages like::

     <Response
        ReferenceNumber="0b47fe86-542f-4070-9e7d-16396a5ef08a"
        InboundODMFileOID="Not Supplied"
        IsTransactionSuccessful="0"
        ReasonCode="RWS00092"
        ErrorClientResponseMessage="CRF version not found">
        </Response>

``RWSException`` also has a standard ``message`` attribute which the error description content from the RWS error is
copied into. The purpose of this scheme is to make rwslib raise a standard exception type that surfaces the error
message from the source RWS response but which also provides full access to the content of the original RWS error message.


