"""
This is for my personal reference and should not be used
"""

import ast
import json
from collections import defaultdict
from functools import reduce
from typing import List

from pip._vendor.pyparsing import Group, Word, MatchFirst, ZeroOrMore, OneOrMore, Optional, Or, alphas, alphanums, \
    nums, Regex

config_file = """AWSSupportCaseEventService#Beta : @AWSSupportCaseEventService#Base.Beta

AWSSupportCaseEventService#Base.Beta : {
  "caseNotificationHandlerSQS" :+ {
    "queueName" : "AWSSupportCaseEventQueue",
    "iamUserMaterialSet" : "aws.kumo.support.case.event.iam.beta"
  },
  "caseNotificationHandlerRDS" : {
    "databaseUrl" : "aws-support-case-event-service-database-cluster-1.cluster-ctqvjdwybpi4.us-east-1.rds.amazonaws.com",
    "databaseName" : "awsSupportCaseEventServiceDatabase",
    "iamUserMaterialSet" : "aws.kumo.support.case.event.rds.beta"
  }
}"""

config_file_basic = """AWSSupportCaseEventService#Beta : @AWSSupportCaseEventService#Base.Beta

AWSSupportCaseEventService#Base.Beta : {
  "caseNotificationHandlerSQS" : {
  },
  "caseNotificationHandlerRDS" : {
  }
}"""

config_file_service_name0 = """AWSSupportCaseEventService#Beta : @AWSSupportCaseEventService#Base.Beta"""
config_file_service_name1 = """AWSSupportCaseEventService#Base.Beta : @AWSSupportCaseEventService#Base.Beta"""
config_file_service_name2 = """AWSSupportCaseEventService#Beta : @AWSSupportCaseEventService#Base.Beta

AWSSupportCaseEventService#Gamma : @AWSSupportCaseEventService#Base.Gamma

AWSSupportCaseEventService#Base.Beta : {
   "name" : 1
}"""
config_file_service_name3 = """
AWSSupportCaseEventService#Base.Beta : {
   "name" : 1.1
}"""
config_file_service_name4 = """
AWSSupportCaseEventService#Base.Beta : {
   "name1" : 1,
   "name2" : 2,
   "name3" : 3
}"""
ast.literal_eval()

class EasyConfig(object):
    def __init__(self):
        self.config_extension = ".config"
        self.config_directory = "config/"

    def get(self, key, application, stage, region=None):
        # Ensure no illegal characters are present
        assert application.count('.') == 0
        assert stage.count('.') == 0
        assert region.count('.') == 0
        pass


def parse(string_to_parse):
    service_name = Word(alphas)
    realm_path_element = Word(alphas)
    realm_path = Group(realm_path_element + ZeroOrMore('.' + realm_path_element))
    service_name_and_realm_extension = service_name + '#' + realm_path

    integer = Word(nums)
    floating = Regex(r'\d+\.\d+')
    boolean = MatchFirst(["True", "False"])
    string = Regex(r'"[a-zA-Z]+"')

    config_key = Regex(r'"[a-zA-Z]+"')
    config_value = Or([integer, floating, boolean, string])
    config_block = Group('{' + '}')
    config_line = Group(config_key + ':' + MatchFirst([config_block, config_value]))
    config_lines = config_line + ZeroOrMore(',' + config_line)

    alias = '@' + service_name_and_realm_extension

    config_definition = Group('{' + Optional(config_lines) + '}')

    config_expression = Group(service_name_and_realm_extension + ':' + MatchFirst([alias, config_definition]))

    expression = OneOrMore(config_expression)

    return expression.parseString(string_to_parse)


def get_from_dict(data_dict, map_list):
    return reduce(lambda d, k: d[k], map_list, data_dict)


def set_in_dict(data_dict, map_list, value):
    get_from_dict(data_dict, map_list[:-1])[map_list[-1]] = value


def pretty(d):
    return json.dumps(d, sort_keys=True, indent=2)


def tree():
    return defaultdict(tree)


def tree_to_dict(root):
    def inner(key_list):
        d = {}
        for k, v in get_from_dict(root, key_list).items():
            if type(v) != defaultdict:
                d[k] = v
            else:
                d[k] = inner(key_list + [k])
        return d

    return inner([])


def semantic_of_realm_path(parsed_realm: List[str]):
    return list(filter(lambda a: a != '.', parsed_realm))


def semantic_of_service_name_and_realm_extension(parsed_string: List[str]):
    service_name, _, realm_path = parsed_string[:3]
    realm_path = semantic_of_realm_path(realm_path)
    return [service_name] + realm_path


def semantic_of_alias(parsed_string: List[str]):
    service_name, _, realm_path = parsed_string[:3]
    realm_path = semantic_of_realm_path(realm_path)
    return [service_name] + realm_path


def semantic_of_config_value(parsed_string: str):
    if parsed_string[0] == '"':
        return parsed_string[1:-1]
    elif parsed_string == "True":
        return True
    elif parsed_string == "False":
        return False
    elif parsed_string.count('.') == 1:
        return float(parsed_string)
    else:
        return int(parsed_string)


def semantic_of_config_line(parsed_string: List):
    key, _, value = parsed_string[:3]
    key = key[1:-1]

    if type(value) == list:
        value = semantic_of_config_block(value)
    else:
        value = semantic_of_config_value(value)

    return key, value


def semantic_of_config_block(parsed_string: List):
    parsed_string = parsed_string[1:-1]
    d = {}
    for line in parsed_string:
        k, v = semantic_of_config_line(line)
        d[k] = v
    return d


def semantics(parsed_string):
    parsed_dictionary = tree()

    for config_symbols in parsed_string:
        parsed_service_name_and_realm_path = config_symbols[:3]
        config_symbols = config_symbols[3:]
        service_name_and_realm_path = semantic_of_service_name_and_realm_extension(parsed_service_name_and_realm_path)

        _, sym = config_symbols[:2]
        config_symbols = config_symbols[2:]
        if sym == '@':
            parsed_alias = config_symbols[:3]
            alias = semantic_of_alias(parsed_alias)
            set_in_dict(parsed_dictionary, service_name_and_realm_path, {'@': alias})
        elif sym == '+':
            pass
        else:
            d = semantic_of_config_block(sym)
            set_in_dict(parsed_dictionary, service_name_and_realm_path, d)

    return tree_to_dict(parsed_dictionary)


if __name__ == "__main__":
    files = [config_file_service_name0, config_file_service_name1, config_file_service_name2, config_file_service_name3, config_file_service_name4]
    for s in files:
        print("\n\n\n")

        print(parse(s))
        print(pretty(semantics(parse(s))))
