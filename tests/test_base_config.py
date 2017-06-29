import os
import unittest

from easyconfig import EasyConfig


class BaseConfigTests(unittest.TestCase):
    def test_easyconfig_loads_base_config_correctly(self):
        path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.abspath(os.path.join(path, 'testing_config', 'base_only'))
        config = EasyConfig("Base", path)

        expected_dict = {
            'database_url': 'localhost:8001',
            'database_name': 'CoolDb',
            'username': 'user',
            'password': 'pass',
            'connect': True,
            'data': ['a', 1, True]
        }

        self.assertDictEqual(config.as_dict(), expected_dict)

    def test_easyconfig_raises_key_error_in_a_base_config(self):
        path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.abspath(os.path.join(path, 'testing_config', 'base_only'))
        config = EasyConfig("Base", path)

        with self.assertRaises(KeyError) as e:
            # noinspection PyStatementEffect
            config['does not exist']

        expected_error_message = "\"Configuration for 'does not exist' was not found in the 'Base' stage\""
        self.assertEqual(str(e.exception), expected_error_message)

if __name__ == '__main__':
    unittest.main()
