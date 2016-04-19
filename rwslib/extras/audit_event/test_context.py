# -*- coding: utf-8 -*-
import unittest
from rwslib.extras.audit_event.context import ContextBase


class ContextBaseTaseCase(unittest.TestCase):

    def setUp(self):
        pass

    def test_repr(self):
        assert ContextBase().__repr__(), ''
