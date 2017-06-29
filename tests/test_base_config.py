import unittest

from easyconfig import EasyConfig


class BaseConfigTests(unittest.TestCase):
    def test_easyconfig_raises_key_error_in_a_base_config(self):
        config = EasyConfig("Base")

        with self.assertRaises(KeyError) as e:
            # noinspection PyStatementEffect
            config['does not exist']

        expected_error_message = "\"Configuration for 'does not exist' was not found in the 'Base' stage\""
        self.assertEqual(str(e.exception), expected_error_message)

if __name__ == '__main__':
    unittest.main()
