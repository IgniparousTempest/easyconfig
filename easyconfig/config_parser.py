import os
from typing import List

from pyparsing import ParseException

from easyconfig import config_validation as validation
from easyconfig.config_dto import ConfigRecord
from easyconfig.config_grammar import grammar


def parse_config(config_directory: str, config_extension: str, stage: str):
    configs = load_config_files(config_directory, config_extension)
    config_dict = translate_config(configs, stage)
    return config_dict


def find_stage(configs: List[ConfigRecord], stage: str):
    config = None
    for conf in configs:
        if stage == conf.parent or stage == conf.name:
            config = stage
            break
    if config is None:
        raise KeyError('The stage \'{0}\' does not exist'.format(stage))
    return config


def translate_config(configs: List[ConfigRecord], stage: str):
    validation.ensure_unique_configs(configs)
    root_nodes = validation.ensure_config_node_inheritance_is_valid(configs)
    print([str(i) for i in root_nodes])

    # Find leaf config
    leaf_config = find_stage(configs, stage)

    return configs[0]


def load_config_files(config_directory: str, config_extension: str):
    configs = []

    for file in os.listdir(config_directory):
        if file.endswith(config_extension):
            file_path = os.path.join(config_directory, file)
            with open(file_path, 'r') as f:
                text = f.read()
            try:
                for conf in grammar().parseString(text, parseAll=True):
                    configs.append(conf)
            except ParseException:
                raise SyntaxError('There was a syntax error in the following config file: \'{0}\''.format(file_path))

    return configs
