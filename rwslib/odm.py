__author__ = 'andrew'

from rwslib import RWSConnection
from rwslib.rws_requests import *
from rwslib.rws_requests.odm_adapter import *
from rwslib.rws_requests.biostats_gateway import *

if __name__ == '__main__':

    from _settings import accounts

    acc = accounts['innovate']
    rave = RWSConnection('innovate', acc['username'], acc['password'])

    print(rave.send_request(VersionRequest()))

    audits = rave.send_request(AuditRecordsRequest('Mediflex','Dev',startid=4000000,per_page=10000))
    print rave.next_link # Get headers, next and last entries?
    #print audits
    while rave.next_link <> None:
        rave.next(AuditRecordsRequest('Mediflex','Dev'))
        print(rave.next_link)