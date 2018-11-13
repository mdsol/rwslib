# -*- coding: utf-8 -*-
import unittest
from rwslib.extras.audit_event.main import ODMAdapter
from rwslib import RWSConnection


class TestEventer(object):

    def __init__(self):
        self.count = 0

    def NoMatchHere(self, context):
        self.count += 1

    def default(self, context):
        pass


class ODMAdapterTaseCase(unittest.TestCase):

    def setUp(self):
        pass

    def test_classes(self):
        test_eventer = TestEventer()
        conn = RWSConnection('innovate', "FAKE_USER", "FAKE_PASS")
        ODMAdapter(conn, "Mediflex", "Dev", test_eventer)
