# -*- coding: utf-8 -*-

__title__ = 'rwslib'
__author__ = 'Ian Sparks (isparks@mdsol.com)'
__version__ = '1.0.0'
__license__ = 'MIT'
__copyright__ = 'Copyright 2013 Medidata Solutions Inc'



import requests
from urllib import urlencode

from rws_requests import RWSRequest, make_url
from rwsobjects import RWSException, RWSError, RWSErrorResponse


#-------------------------------------------------------------------------------------------------------
# Classes
#
class AuthorizationException(Exception):
    """Raised if a request requires authorization but no authorization header is provided"""
    pass


class RWSConnection(object):
    """A connection to RWS"""

    def __init__(self, domain, username=None, password=None):
        """Create a connection to Rave

          If the domain does not start with http then it is assumed to be the name of the medidata
          url and https:// will be added as a prefix and .mdsol.com will be added as a postfix.

          e.g.

          innovate      = https://innovate.mdsol.com
          http://mytest = http:/mytest

        """

        if domain.lower().startswith('http'):
            self.domain = domain
        else:
            self.domain = 'https://%s.mdsol.com' % domain

        self.username = username
        self.password = password

        self.base_url = self.domain + '/RaveWebServices'

        #Keep track of results of last request so users can get if they need.
        self.last_result = None


    def get_auth(self):
        """Get authorization headers"""
        return (self.username, self.password,)


    def send_request(self, request_object):
        """Send request to RWS endpoint. The request object passed provides the URL endpoint and the HTTP method.
           Takes the text response from RWS and allows the request object to modify it for return. This allows the request
           object to return text, an XML document object, a CSV file or anything else that can be generated from the text
           response from RWS.
        """
        if not isinstance(request_object, RWSRequest):
            raise ValueError("Request object must be a subclass of RWSRequest")

        #Construct a URL from the object and make a call
        full_url = make_url(self.base_url, request_object.url_path())
        kwargs = {}
        if request_object.requires_authorization:
            kwargs['auth'] = self.get_auth()
            kwargs.update(request_object.args())


        #Explicit use of requests library here. Could alter in future to inject library to use in case
        #requests not available.
        action = {"GET": requests.get,
                  "POST": requests.post}[request_object.method]

        r = action(full_url, **kwargs)
        self.last_result = r

        if r.status_code in [400, 404]:
            #Is it a RWS response?
            if r.text.startswith('<Response'):
                error = RWSErrorResponse(r.text)
                raise RWSException(error.errordescription, error)
            elif '<html' in r.text:
                raise RWSException("IIS Error", r.text)
            else:
                error = RWSError(r.text)
            raise RWSException(error.errordescription, error)

        elif r.status_code == 401:
            #Either you didn't supply auth header and it was required OR your credentials were wrong
            #RWS handles each differently

            #You didn't supply auth (text response from RWS)
            if r.text == 'Authorization Header not provided':
                raise AuthorizationException(r.text)

            if '<h2>HTTP Error 401.0 - Unauthorized</h2>' in r.text:
                raise RWSException("Unauthorized.", r.text)

            #There was some problem with your credentials (XML response from RWS)
            error = RWSErrorResponse(r.text)
            raise RWSException(error.errordescription, error)

        #Catch all.
        if r.status_code != 200:
            error = RWSError(r.text)
            raise RWSException(error.errordescription, error)

        return request_object.result(r)
