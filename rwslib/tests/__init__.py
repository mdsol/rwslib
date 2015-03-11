# -*- coding: utf-8 -*-

__author__ = 'glow'
import unittest

import test_builders
import test_rwslib
import test_rwsobjects

def all_tests():
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite.addTests(loader.loadTestsFromModule(test_builders))
    suite.addTests(loader.loadTestsFromModule(test_rwsobjects))
    suite.addTests(loader.loadTestsFromModule(test_rwslib))
    return suite
