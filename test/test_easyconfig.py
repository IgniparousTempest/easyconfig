import unittest

from easyconfig.easyconfig import EasyConfig

test_config_base_directory = "test_config/"


class BuildtargetTests(unittest.TestCase):
    def test_easyconfig_reads_a_base_config(self):
        config = EasyConfig(test_config_base_directory + "test_base/")
        self.assertEqual(1, 1)


if __name__ == '__main__':
    unittest.main()
