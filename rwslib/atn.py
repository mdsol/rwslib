__author__ = 'anewbigging'


from rwslib import RWSConnection
from rwslib.rws_requests import *
from rwslib.rws_requests.odm_adapter import *
from rwslib.rws_requests.biostats_gateway import *

if __name__ == '__main__':


    from _settings import accounts

    acc = accounts['innovate']
    rave = RWSConnection('innovate', acc['username'], acc['password'],timeout=1)

    print rave.send_request(ClinicalStudiesRequest())
    print rave.request_time

    try:
        audits = rave.send_request(AuditRecordsRequest('Mediflex','Dev',startid=1,per_page=30000))
        print rave.last_result.headers["link"]
        print rave.request_time
    except:
        raise
