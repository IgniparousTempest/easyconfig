import collections
from typing import List, Dict

from easyconfig.config_dto import ConfigRecord, ConfigNode


def ensure_unique_configs(configs: List[ConfigRecord]):
    """Ensures that there are no co configs have the same name.

    :param configs:
    :return:
    :raise:
    """
    config_keys = []
    for conf in configs:
        config_keys.append(conf.name)
    # Ensure there are no duplicate config keys
    key_count = collections.Counter(config_keys).most_common(1)
    if key_count[0][1] > 1:
        raise SyntaxError('The config key \'{0}\' has {1} duplicate{2}.'.format(key_count[0][0], key_count[0][1] - 1,
                                                                                '' if key_count[0][1] == 2 else 's'))
    return True


def ensure_config_node_inheritance_is_valid(configs: List[ConfigRecord]):
    # See: https://stackoverflow.com/a/29942118/1705337
    lookup: Dict[str, ConfigNode] = {conf.name: ConfigNode(conf) for conf in configs}
    root_nodes = []

    for conf in configs:
        if conf.name in lookup:
            current_node = lookup[conf.name]
            current_node.parent = conf
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
    return root_nodes
