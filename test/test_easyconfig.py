import unittest

from easyconfig.easyconfig import EasyConfig

test_config_base_directory = "test_config/"


class BuildtargetTests(unittest.TestCase):
    def test_easyconfig_reads_primitives_in_a_base_config(self):
        config = EasyConfig("Base", test_config_base_directory + "test_primitives/")

        self.assertEqual(config.get("string"), "Cray String")
        self.assertEqual(config.get("true"), True)
        self.assertEqual(config.get("false"), False)
        self.assertEqual(config.get("none"), None)
        self.assertEqual(config.get("list"), [-1, 0.02, True, "lol", None])
        self.assertEqual(config.get("integer"), 0)
        self.assertEqual(config.get("float"), 1.1)
        self.assertEqual(config.get("negative integer"), -1)
        self.assertEqual(config.get("negative float"), -0.1)

    def test_easyconfig_reads_nested_primitives_in_a_base_config(self):
        config = EasyConfig("Base", test_config_base_directory + "test_nested/")

        self.assertEqual(config.get("level0"), "level0")
        self.assertEqual(config.get("level1.nested0"), "nested0")
        self.assertEqual(config.get("level1.nested1.deepNested0"), "deepNested0")

    def test_easyconfig_reads_inherited_values_in_an_extended_config(self):
        config = EasyConfig("Beta", test_config_base_directory + "test_extended/")

        self.assertEqual(config.get("level0"), "level0")
        self.assertEqual(config.get("level1.nested0"), "nested0")
        self.assertEqual(config.get("level1.nested1.deepNested0"), "deepNested0")

    def test_easyconfig_reads_child_only_values_in_an_extended_config(self):
        config = EasyConfig("Beta", test_config_base_directory + "test_extended/")

        self.assertEqual(config.get("level1.childOnlyValue"), "childOnlyValue")

    # # # # # # # # # # # # # # # #
    #
    # Errors
    #
    # # # # # # # # # # # # # # # #

    def test_easyconfig_fails_on_missing_parent_config(self):
        expected_error_message = "\"The parent stage 'Base.Africa' referenced from 'Base.Africa.Beta' does not exist\""

        with self.assertRaises(KeyError) as cm:
            config = EasyConfig("BetaAfrica", test_config_base_directory + "test_missing_parent/")

        self.assertEqual(str(cm.exception), expected_error_message)

    def test_easyconfig_fails_on_a_missing_key(self):
        expected_error_message = "\"Key 'nonExistentKey' doesn't exist in dictionary\""

        config = EasyConfig("Base", test_config_base_directory + "test_primitives/")

        with self.assertRaises(KeyError) as cm:
            config.get("nonExistentKey")

        self.assertEqual(str(cm.exception), expected_error_message)


if __name__ == '__main__':
    unittest.main()
