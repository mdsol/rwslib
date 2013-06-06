Getting started
***************

A quick primer on working with RWSLib



Creating a connection to RWS
----------------------------

Before you can do any work with rwslib you must create a connection to a Rave instance. This is done
through the RWSConnection object::

    >>> from rwslib import RWSConnection
    >>> rws = RWSConnection('https://innovate.mdsol.com', 'my_username','my_password')

    >>> #Get the rave version from rws
    >>> rws.version()
    1.8.0

It is important to understand that an RWSConnection is not a persistent connection to Rave, it is simply
a convenience class for making calls to RWS endpoints.

Note that most of the methods of RWSConnection require authentication. There are some that do not, version()
happens to be one of them so this is also valid::

    >>> from rwslib import RWSConnection
    >>> rws = RWSConnection('https://innovate.mdsol.com')

    >>> #Get the rave version from rws
    >>> rws.version()
    1.8.0

Generally you will want to provide credentials to log into Rave.

Getting more information from last_result
-----------------------------------------

Each time you use a method of RWSConnection to make an RWS call and receive results, RWSConnection
keeps the result of the RWS call in it's last_result attribute. This is very useful for debugging
RWS calls since it allows you to find out what headers were sent, what URL was called etc.

    >>> from rwslib import RWSConnection
    >>> rws = RWSConnection('https://innovate.mdsol.com')

    >>> #Get the rave version from rws
    >>> rws.version()
    1.8.0
    >>> rws.last_result.url
    https://innovate.mdsol.com/RaveWebServices/version
    >>> rws.last_result.status_code
    200
    >>> rave.last_result.headers['content-type']
    text/plain; charset=utf-8
    >>> rave.last_result.text
    1.8.0

last_result is a `Requests <http://docs.python-requests.org/>`_ object. Please see that library for more
information on all the properties that can be returned there.

Having access to last_result means that rwslib never hides it's workings from you. rwslib is intended to
be a helper library to get your own integrations up and running, it tries not to hide implementation
details from you.








