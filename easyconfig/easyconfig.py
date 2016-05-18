import glob
import os
from typing import List

from functools import reduce
from pip._vendor.pyparsing import dblQuotedString, removeQuotes, Suppress, Combine, Optional, Word, nums, Forward, \
    Keyword, replaceWith, Group, ZeroOrMore, alphas, Dict, alphanums, ParseResults


class EasyConfig(object):
    def __init__(self, stage, config_path, file_extension='.config'):
        self.stage = stage
        self._config = self._read_config_files(config_path, file_extension)
        self._alias_realm_mapping = get_alias_to_fully_qualified_realm_path_mapping(self._config)
        self._config = generate_absolute_dict(self._config)
        self._full_realm_name = stage if stage not in self._alias_realm_mapping else self._alias_realm_mapping[stage]

        if self.stage not in self._alias_realm_mapping and self.stage not in self._config:
            raise KeyError("The realm '%s' was not found in the config" % self.stage)

    @staticmethod
    def _read_config_files(config_path, file_extension):
        grammar_definition = grammar()
        config_definition = ""

        abs_path = os.path.abspath(os.path.curdir + '/' + config_path)
        for filename in glob.glob(os.path.join(abs_path, '*' + file_extension)):
            with open(filename, 'r') as f:
                config_definition += f.read() + '\n'

        return grammar_definition.parseString(config_definition)

    def get(self, key: str):
        # Make sure the key is of the right format. # TODO: Better solution maybe?
        if not Combine(Word(alphanums + ' ') + ZeroOrMore('.' + Word(alphanums + ' '))).parseString(key)[0] == key:
            raise ValueError("The key '%s' was not of the format name.name etc..." % key)

        return self._get_value_from_dict(self._config, self._full_realm_name, key)

    @classmethod
    def _get_value_from_dict(cls, dictionary, fully_qualified_realm, key):
        the_d = dictionary[fully_qualified_realm]
        try:
            return reduce(lambda d, k: d[k], key.split('.'), the_d)
        except KeyError:
            raise KeyError("Key '{}' doesn't exist in dictionary".format(key))

    def __str__(self):
        return str(self._config)


# # # # # # # # # # # # # # # #
#
# Semantic functions
#
# # # # # # # # # # # # # # # #


def generate_absolute_dict(configs) -> dict:
    d = {}

    # Sort the dictionary on full realm path so we can do a single pass
    ordered_configs = sorted(configs, key=lambda x: x[0])

    for config_def in ordered_configs:
        parent_realm_path = '.'.join(config_def[0].split('.')[:-1])
        ref_d = {}

        if parent_realm_path != '':
            try:
                ref_d = d[parent_realm_path].copy()
            except KeyError:
                raise KeyError("The parent stage '{}' referenced from '{}' does not exist"
                               .format(parent_realm_path, config_def[0]))

        d[config_def[0]] = convert_to_dictionary_inner(config_def, ref_d)
    return d


def convert_to_dictionary_inner(config: ParseResults, ref_d):
    d = {}
    if does_extends_parent(config):
        d = ref_d.copy()
    for k, v in config.items():
        if isinstance(v, ParseResults):
            d[k] = convert_to_dictionary_inner(v, ref_d[k] if k in ref_d else {})
        else:
            d[k] = v
    return d


def get_alias_to_fully_qualified_realm_path_mapping(configs: List[ParseResults]) -> dict:
    d = {}
    for config in configs:
        fqdn, alias = config[0], config[1]
        d[alias] = fqdn
    return d


def does_extends_parent(config):
    try:
        return config[0] == ExtendsParent or config[1] == ExtendsParent or config[2] == ExtendsParent
    except IndexError:
        return False


# # # # # # # # # # # # # # # #
#
# Parsing functions
#
# # # # # # # # # # # # # # # #


def convert_numbers(s, l, toks):
    n = toks[0]
    try:
        return int(n)
    except ValueError:
        return float(n)


def convert_list(s, l, toks):
    return toks.asList()


# # # # # # # # # # # # # # # #
#
# Helper Tokens
#
# # # # # # # # # # # # # # # #


class ExtendsParent(object):
    pass


# # # # # # # # # # # # # # # #
#
# printing functions
#
# # # # # # # # # # # # # # # #


def pretty_print(d: ParseResults, indent_size=2):
    s = ""

    def pretty_print_block(d: ParseResults, indent_depth=1):
        offset = (indent_size * indent_depth) * ' '
        offset_less1 = offset[:-indent_size]

        s = offset_less1 + '{\n'

        if d[0] == ExtendsParent:
            s += offset + "Extends parent class\n"
        for k, v in d.items():
            if isinstance(v, ParseResults):
                v = pretty_print_block(v, indent_depth + 1)
            s += '{}"{}": {}\n'.format(offset, k, v)

        s += offset_less1 + '}\n'
        return s

    s += " = = = \n"
    s += "Fully qualified path : " + d[0] + '\n'
    s += "Alias : " + ("None" if d[1] == "" else d[1]) + '\n'
    s += pretty_print_block(d)

    return s


def pretty_print_dict(d: dict, indent_size=2):
    s = ""

    def pretty_print_block(d: dict, indent_depth=1):
        offset = (indent_size * indent_depth) * ' '
        offset_less1 = offset[:-indent_size]

        s = offset_less1 + '{\n'

        for k, v in d.items():
            if isinstance(v, dict):
                v = pretty_print_block(v, indent_depth + 1)
            s += '{}"{}": {},\n'.format(offset, k, v)

        s += offset_less1 + '}'
        return s

    s += pretty_print_block(d)

    return s


# # # # # # # # # # # # # # # #
#
# Grammar
#
# # # # # # # # # # # # # # # #


# noinspection PyPep8Naming
def grammar():
    primitive = Forward()

    ALIAS = Keyword("->")
    EXTENDS = Keyword('+').setParseAction(replaceWith(ExtendsParent))

    TRUE = Keyword("True").setParseAction(replaceWith(True))
    FALSE = Keyword("False").setParseAction(replaceWith(False))
    BOOLEAN = (TRUE | FALSE)
    NULL = Keyword("None").setParseAction(replaceWith(None))
    STRING = dblQuotedString.setParseAction(removeQuotes)
    NUMBER = Combine(Optional('-') + ('0' | Word('123456789', nums)) + Optional('.' + Word(nums))).addParseAction(
        convert_numbers)
    LIST = Suppress('[') + Group(Optional(primitive) + ZeroOrMore(Suppress(',') + primitive)).addParseAction(
        convert_list) + Suppress(']')

    primitive << (STRING | NUMBER | BOOLEAN | NULL | LIST)

    config_key = Suppress('"') + Word(alphanums + ' ') + Suppress('"')

    config_block = Forward()
    override_block = EXTENDS + config_block
    config_line = Group(config_key + Suppress(':') + (primitive | config_block | override_block))
    config_lines = Dict(config_line + ZeroOrMore(Suppress(',') + config_line))

    config_block << Suppress('{') + Optional(config_lines, default=[]) + Suppress('}')

    realm_name = Word(alphas)
    fully_qualified_realm = Combine(realm_name + ZeroOrMore('.' + realm_name))

    config_definition = Suppress(':') + (config_block | override_block)
    alias = Suppress(ALIAS) + realm_name

    config_group = Group(fully_qualified_realm + Optional(alias, default='') + config_definition)

    expression = ZeroOrMore(config_group)
    return expression


if __name__ == "__main__":
    test = """
Base : {
    "key6" : {
        "nested0" : "base data",
        "nested1" : "base data",
        "nested2" : "base data"
    },
    "key7" : {
        "nested0" : "base data",
        "nested1" : "base data"
    },
    "key99" : 1
}

Base.Beta -> Beta :+ {
    "key0" : "Jacob Zuma",
    "key1" : True,
    "key2" : False,
    "key3" : None,
    "key4" : [-1, 0.02, True, "lol"],
    "key5" : 1,
    "key6" :+ {
        "nested0" : "beta data",
        "nested1" : 2.1,
        "nested3" : 1
    },
    "key7" : {
        "nested0" : 1,
        "nested1" : 2.1,
        "nested2" : [1, True, "Pen Island"],
        "nested3" : {
        }
    }
}
"""

    print(grammar().parseString(test))
    print(type(grammar().parseString(test)), '\n')
    for config_declaration in grammar().parseString(test):
        print(pretty_print(config_declaration))
        print("fqdn:", config_declaration[0])
        print("alias:", config_declaration[1])
        print("key6.nested0:", config_declaration["key6"]["nested0"])
        try:
            print("key7.nested3:", type(config_declaration["key7"]["nested3"]))
        except KeyError:
            pass
        if "key4" in config_declaration:
            print(config_declaration["key4"])
            print(type(config_declaration["key4"]))
        if isinstance(config_declaration["key6"][0], ExtendsParent):
            print("Extends")

    print('\n', '\n', '\n')
    print(pretty_print_dict(generate_absolute_dict(grammar().parseString(test))))
