# -*- coding: utf-8 -*-
__author__ = 'isparks'

from rwslib.rws_requests.odm_adapter import AuditRecordsRequest
from six.moves.urllib.parse import urlparse, parse_qs
from rwslib.extras.audit_event.parser import parse
import logging


class ODMAdapter(object):
    """A self-contained data fetcher and parser using a RWSConnection and an event class provided by the user"""
    def __init__(self, rws_connection, study, environment, eventer):
        self.rws_connection = rws_connection
        self.eventer = eventer
        self.study = study
        self.environment = environment
        self.start_id = 0

    def get_next_start_id(self):
        """If link for next result set has been passed, extract it and get the next set start id"""
        link = self.rws_connection.last_result.links.get("next", None)
        if link:
            link = link['url']
            p = urlparse(link)
            start_id = int(parse_qs(p.query)['startid'][0])
            return start_id

        return None

    def run(self, start_id=0, max_pages=-1, per_page=1000, **kwargs):
        page = 0
        self.start_id = start_id
        while max_pages == -1 or (page < max_pages):

            req = AuditRecordsRequest(self.study, self.environment, startid=self.start_id, per_page=per_page)
            try:
                # Get the ODM data
                odm = self.rws_connection.send_request(req, **kwargs)
                # Check if we were passed the next startid
                # Need to do this immediately because subsequent parsing might include other calls to RWS
                self.start_id = self.get_next_start_id()
                # Send it for parsing
                parse(odm, self.eventer)
                page += 1
            except Exception as e:
                logging.error(e.message)

            if not self.start_id:
                break
