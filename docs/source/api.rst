API
***

The rwslib API.

Projectnames, Studynames and Environments
------------------------------------------

rwslib uses some standard definitions for studyname, protocol names and environments. It defines them as:

* Projectname  - The name of the study without environment e.g. the Mediflex in **Mediflex** (Dev)
* Environment  - The environment within the study e.g. the Dev in Mediflex (**Dev**)
* StudyName    - The combination of projectname and environment **Mediflex (Dev)**


version()
---------

Returns the text result of calling::

    https://{{ host }}/RaveWebServices/version

Example::

    >>> from rwslib import RWSConnection
    >>> r = RWSConnection('innovate', 'username', 'password')  #Authorization optional
    >>> r.version()
    1.8.0


build_version()
---------------

Returns the text result of calling::

    https://{{ host }}/RaveWebServices/version/build

Diagnostics returns a 200 response code and the internal build number.

Example::

    >>> from rwslib import RWSConnection
    >>> r = RWSConnection('innovate', 'username', 'password')  #Authorization optional
    >>> r.build_version()
    5.6.5.12

flush_cache()
---------------

Authorization is required for this method call.

Returns the text result of calling::

    https://{{ host }}/RaveWebServices/webservice.aspx?CacheFlush


.. warning::

    Calling flush_cache unnecessarily causes RWS to re-load objects, causing additional resource utilization that
    could have a detrimental affect on Rave performance.


Flushes the RWS cache. Generally Rave and RWS manage their own caching. You should not need to use this method
in normal operation. Returns a RWSResponse object with a istransactionsuccessful attribute:

Example::

    >>> from rwslib import RWSConnection
    >>> r = RWSConnection('innovate', 'username', 'password')  #Authorization REQUIRED
    >>> response = r.flush_cache()
    >>> response.istransactionsucessful
    True
