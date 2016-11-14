# -*- coding: utf-8 -*-

__author__ = 'glow'

import unittest


def all_tests():
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite.addTests(loader.discover('rwslib.tests'))
    suite.addTests(loader.discover('rwslib.extras.audit_event'))
    suite.addTests(loader.discover('rwslib.extras'))    # Local cv tests
    return suite
