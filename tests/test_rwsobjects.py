__author__ = 'isparks'

import unittest
import rwsobjects
import httpretty

class TestParseEnvironment(unittest.TestCase):
    """Test for extraction of environment"""
    def test_simple(self):
        env = rwsobjects.getEnvironmentFromNameAndProtocol('TEST (DEV)', 'TEST')
        self.assertEqual(env, 'DEV')

    def test_braces_in_name(self):
        env = rwsobjects.getEnvironmentFromNameAndProtocol('TEST (1) (ZZZ)', 'TEST (1)')
        self.assertEqual(env, 'ZZZ')

    def test_single_right_brace_in_name(self):
        env = rwsobjects.getEnvironmentFromNameAndProtocol('TEST :) (PROD)', 'TEST :)')
        self.assertEqual(env, 'PROD')

    def test_single_left_brace_in_name(self):
        env = rwsobjects.getEnvironmentFromNameAndProtocol('TEST :( (PROD)', 'TEST :(')
        self.assertEqual(env, 'PROD')


    def test_braces_tight_spaces(self):
        env = rwsobjects.getEnvironmentFromNameAndProtocol('TEST(99)(AUX)', 'TEST(99)')
        self.assertEqual(env, 'AUX')

    def test_no_env(self):
        """Note. This is probably not wanted behaviour but I am documenting here!
           What this is saying is that the study name is TEST(99) and there is no
           environment supplied.
        """
        env = rwsobjects.getEnvironmentFromNameAndProtocol('TEST(99)', 'TEST(99)')
        self.assertEqual(env, '')


if __name__ == '__main__':
    unittest.main()
