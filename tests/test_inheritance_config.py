import os
import unittest

from easyconfig import EasyConfig


class MyTestCase(unittest.TestCase):
    def test_easyconfig_loads_base_config_correctly_from_inheritable_configs(self):
        path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.abspath(os.path.join(path, 'testing_config', 'inheritance'))
        config = EasyConfig("Base", path)

        expected_dict = {
            'database_url': 'localhost:8001',
            'database_name': 'CoolDb',
            'username': 'user',
            'password': 'pass'
        }

        self.assertDictEqual(config.as_dict(), expected_dict)

    def test_easyconfig_loads_inherited_config_correctly_from_inheritable_configs(self):
        path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.abspath(os.path.join(path, 'testing_config', 'inheritance'))
        config = EasyConfig("Africa", path)

        expected_dict = {
            'database_url': 'mysql://mysql.example.com/',
            'database_name': 'AfricaDb',
            'username': 'user',
            'password': 'password'
        }

        self.assertDictEqual(config.as_dict(), expected_dict)

    def test_easyconfig_loads_sub_inherited_config_correctly_from_inheritable_configs(self):
        path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.abspath(os.path.join(path, 'testing_config', 'inheritance'))
        config = EasyConfig("SouthAfrica", path)

        expected_dict = {
            'database_url': 'mysql://mysql.example.com/',
            'database_name': 'SuidAfrika',
            'username': 'user',
            'password': 'wagwoord'
        }

        self.assertDictEqual(config.as_dict(), expected_dict)


if __name__ == '__main__':
    unittest.main()
