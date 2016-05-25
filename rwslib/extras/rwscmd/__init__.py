# -*- coding: utf-8 -*-
__author__ = 'anewbigging'

import unittest


def all_tests():
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite.addTests(loader.discover('rwscmd.tests'))
    return suite