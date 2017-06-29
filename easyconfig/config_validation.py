import collections
from typing import List

from easyconfig.config_dto import ConfigRecord, ConfigNode


def ensure_config_stage_exists(configs: List[ConfigRecord], stage: str):
    for conf in configs:
        if conf.name == stage:
            return True
    raise KeyError('The stage \'{0}\' does not exist'.format(stage))


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


# TODO: Implement this.
def ensure_config_node_inheritance_is_valid(config_trees: List[ConfigNode]):
    pass
