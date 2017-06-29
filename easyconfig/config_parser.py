import os
from typing import List, Dict, Any, Tuple

from pyparsing import ParseException

from easyconfig import config_validation as validation
from easyconfig.config_dto import ConfigRecord, ConfigNode
from easyconfig.config_grammar import grammar


def parse_config(config_directory: str, config_extension: str, stage: str):
    configs = load_config_files(config_directory, config_extension)
    config_dict = translate_config(configs, stage)
    return config_dict


# TODO: This could be made more efficient if we only construct the tree we need, probably will only help in edge cases?
def config_records_to_config_trees(configs: List[ConfigRecord]) -> Tuple[List[ConfigNode], Dict[str, ConfigNode]]:
    """Converts a flat list of config records into a list of config trees. With each node in the tree in its proper 
    inheritance order. 
    
    :param configs: The parsed configuration files.
    :return: The config trees.
    """
    lookup: Dict[str, ConfigNode] = {conf.name: ConfigNode(conf) for conf in configs}
    root_nodes = []

    for conf in configs:
        if conf.name in lookup:
            current_node = lookup[conf.name]
            current_node.record = conf
        else:
            current_node = ConfigNode(conf)

        if conf.name == conf.parent:
            root_nodes.append(current_node)
        else:
            if conf.parent not in lookup:
                parent_node = ConfigNode()
                lookup[conf.parent] = parent_node
            else:
                parent_node = lookup[conf.parent]
            parent_node.children.append(current_node)
            current_node.parent = parent_node
    return root_nodes, lookup


def construct_stage_configuration_from_tree(node_lookup: Dict[str, ConfigNode], stage: str) -> Dict[str, Any]:
    """Constructs a single dict for the desired stage. 
    
    :param node_lookup: 
    :param stage: 
    :return: 
    """
    inheritance_path = []
    conf_node = node_lookup[stage]
    while True:
        inheritance_path = [conf_node.name] + inheritance_path
        if node_lookup[conf_node.name].parent is None:
            break
        conf_node = node_lookup[conf_node.name].parent

    stage_config = {}
    for parent in inheritance_path:
        for key in node_lookup[parent].record.data.keys():
            stage_config[key] = node_lookup[parent].record.data[key]
    return stage_config


def translate_config(configs: List[ConfigRecord], stage: str) -> Dict[str, Any]:
    validation.ensure_config_stage_exists(configs, stage)
    validation.ensure_unique_configs(configs)

    root_nodes, node_lookup = config_records_to_config_trees(configs)

    validation.ensure_config_node_inheritance_is_valid(root_nodes)

    # Find leaf config
    stage_config = construct_stage_configuration_from_tree(node_lookup, stage)

    return stage_config


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
