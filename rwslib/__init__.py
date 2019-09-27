# -*- coding: utf-8 -*-

__title__ = "rwslib"
__author__ = "Ian Sparks (isparks@mdsol.com)"
__version__ = "1.2.4"
__license__ = "MIT"
__copyright__ = "Copyright 2017 Medidata Solutions Inc"


import requests

from .rws_requests import RWSRequest, make_url
from .rwsobjects import RWSException, RWSError, RWSErrorResponse

import time

# -------------------------------------------------------------------------------------------------------
# Classes


class AuthorizationException(Exception):
    """Raised if a request requires authorization but no authorization header is provided"""

    pass


class RWSConnection(object):
    """A connection to RWS"""

    def __init__(
        self,
        domain,
        username=None,
        password=None,
        auth=None,
        virtual_dir="RaveWebServices",
    ):
        """
        Create a connection to Rave

        :param str domain: Rave URL Name
        :param str username: Rave User Login
        :param str password: Rave User password
        :param str auth: Authentication tuple (usually something like `(username, password)`
        :param str virtual_dir: Name of the Rave Web Services prefix (usually `RaveWebServices`, but can be customised)

        .. note::
            If the `domain` does not start with http then it is assumed to be the name of the Medidata
            url and https:// will be added as a prefix and .mdsol.com will be added as a postfix.

            * innovate => https://innovate.mdsol.com
            * http://mytest => http:/mytest

        """

        if domain.lower().startswith("http"):
            self.domain = domain
        else:
            self.domain = "https://%s.mdsol.com" % domain

        self.auth = None
        if auth is not None:
            self.auth = auth
        elif username is not None and password is not None:
            # Make a basic auth
            self.auth = (username, password)

        self.base_url = make_url(self.domain, virtual_dir)

        # Keep track of results of last request so users can get if they need.
        self.last_result = None

        # Time taken to process last request
        self.request_time = None

    def send_request(self, request_object, timeout=None, retries=1, **kwargs):
        """Send request to RWS endpoint. The request object passed provides the URL endpoint and the HTTP method.
           Takes the text response from RWS and allows the request object to modify it for return. This allows the request
           object to return text, an XML document object, a CSV file or anything else that can be generated from the text
           response from RWS.
           A timeout, in seconds, can be optionally passed into send_request.
        """
        if not isinstance(request_object, RWSRequest):
            raise ValueError("Request object must be a subclass of RWSRequest")

        # Construct a URL from the object and make a call
        full_url = make_url(self.base_url, request_object.url_path())
        if request_object.requires_authorization:
            kwargs["auth"] = self.auth
            # TODO: Look at different connect and read timeouts?
            kwargs["timeout"] = timeout
            kwargs.update(request_object.args())

        # Explicit use of requests library here. Could alter in future to inject library to use in case
        # requests not available.

        # Get a session that allows us to customize HTTP requests
        session = requests.Session()

        # Mount a custom adapter that retries failed connections for HTTP and HTTPS requests.
        for scheme in ["http://", "https://"]:
            session.mount(scheme, requests.adapters.HTTPAdapter(max_retries=retries))

        action = {"GET": session.get, "POST": session.post}[request_object.method]

        start_time = time.time()

        try:
            r = action(full_url, **kwargs)  # type: requests.models.Response
        except (
            requests.exceptions.ConnectTimeout,
            requests.exceptions.ReadTimeout,
        ) as exc:
            if isinstance(exc, (requests.exceptions.ConnectTimeout,)):
                raise RWSException(
                    "Server Connection Timeout",
                    "Connection timeout for {}".format(full_url),
                )
            elif isinstance(exc, (requests.exceptions.ReadTimeout,)):
                raise RWSException(
                    "Server Read Timeout", "Read timeout for {}".format(full_url)
                )

        self.request_time = time.time() - start_time
        self.last_result = r  # see also r.elapsed for timedelta object.

        if r.status_code in [400, 404]:
            # Is it a RWS response?
            if r.text.startswith("<Response"):
                error = RWSErrorResponse(r.text)
                raise RWSException(error.errordescription, error)
            elif "<html" in r.text:
                raise RWSException("IIS Error", r.text)
            else:
                error = RWSError(r.text)
            raise RWSException(error.errordescription, error)

        elif r.status_code == 500:
            raise RWSException("Server Error (500)", r.text)

        elif r.status_code == 401:
            # Either you didn't supply auth header and it was required OR your credentials were wrong
            # RWS handles each differently

            # You didn't supply auth (text response from RWS)
            if r.text == "Authorization Header not provided":
                raise AuthorizationException(r.text)

            if "<h2>HTTP Error 401.0 - Unauthorized</h2>" in r.text:
                raise RWSException("Unauthorized.", r.text)

            # Check if the content_type is text/xml.  Use startswith
            # in case the charset is also specified:
            #  content-type: text/xml; charset=utf-8
            if r.headers.get("content-type").startswith("text/xml"):
                # XML response
                if r.text.startswith("<Response"):
                    error = RWSErrorResponse(r.text)
                elif "ODM" in r.text:
                    error = RWSError(r.text)
            else:
                # There was some problem with your credentials (XML response from RWS)
                error = RWSErrorResponse(r.text)
            raise RWSException(error.errordescription, error)

        # Catch all.
        if r.status_code != 200:
            if "<" in r.text:
                # XML like
                if r.text.strip().startswith("<Response"):
                    error = RWSErrorResponse(r.text)
                elif "ODM" in r.text:
                    error = RWSError(r.text)
                else:
                    # IIS error page as an example
                    raise RWSException(
                        "Unexpected Status Code ({0.status_code})".format(r), r.text
                    )
            else:
                # not XML like, better to be safe than blow up
                # example response: 'HTTP 503 Service Temporarily Unavailable'
                raise RWSException(
                    "Unexpected Status Code ({0.status_code})".format(r), r.text
                )
            raise RWSException(error.errordescription, error)

        return request_object.result(r)
