from typing import Dict, Any

from easyconfig.config_parser import parse_config


class EasyConfig(object):
    def __init__(self, stage: str = None, config_directory: str = 'config/', config_file_extension: str = '.conf'):
        self._stage = stage
        self._config_directory = config_directory
        self._config_file_extension = config_file_extension
        self._config_attributes = _ConfigAttributes()

    def __getitem__(self, item: str) -> Any:
        try:
            return self._config_attributes[item]
        except KeyError as e:
            error_msg = 'Configuration for {} was not found in the \'{}\' stage'.format(str(e), self._stage)
            raise KeyError(error_msg)


class _ConfigAttributes(object):
    def __init__(self):
        self._attributes: Dict[str, Any] = {}

    def __getitem__(self, item: str) -> Any:
        return self._attributes[item]

if __name__ == '__main__':
    import os
    path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.abspath(os.path.join(path, '..', 'tests', 'testing_config', 'base_only'))
    print(parse_config(path, '.conf', 'Base'))
