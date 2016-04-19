# -*- coding: utf-8 -*-
import unittest
from rwslib.extras.audit_event.context import ContextBase


class ContextBaseTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def test_repr(self):
        self.assertEqual(ContextBase().__repr__(), 'ContextBase({})')
