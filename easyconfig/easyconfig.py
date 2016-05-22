import glob
import os
from collections import namedtuple
from typing import List

# noinspection PyProtectedMember
from pip._vendor.pyparsing import dblQuotedString, removeQuotes, Suppress, Combine, Optional, Word, nums, Forward, \
    Keyword, replaceWith, Group, ZeroOrMore, alphas, Dict, alphanums, ParseResults


# noinspection PyPep8Naming
def EasyConfig(stage: str, config_directory: str = 'configuration/', file_extension: str = '.config') -> namedtuple:
    """
    Converts the text based config file(s) into a Python accessible object. The creation of the config object is not
    instant, so consider creating the config object only once.

    :param stage: The stage for which the configuration must be generated, this can either be the full hierarchy path or
     just the alias. It is a good design practice to use the alias rather than the full path, as this allows the
     hierarchy of the config to be changed without changing the code.
    :param config_directory: The directory where the config files are stored, the path is relative to the project
     directory.
    :param file_extension: The file extension that config file use, to use all files in the directory use '*'.
    :return: The complied config object.
    """
    _config = _read_config_files(config_directory, file_extension)
    _alias_realm_mapping = _get_alias_to_fully_qualified_realm_path_mapping(_config)
    _config = _generate_absolute_dict(_config)
    _full_realm_name = stage if stage not in _alias_realm_mapping else _alias_realm_mapping[stage]

    if _full_realm_name in _config:
        return _convert(_config[_full_realm_name])
    else:
        raise KeyError("The realm '%s' was not found in the config" % stage)


class Config(object):
    """
    Object to store each node in a config definition.
    """

    def as_dict(self):
        """
        Generates a nested Python dictionary of the class. As this is probably an infrequent use case, I have not stored
         the dictionary in the class.
        :return: Nested Python dictionary representation of class
        """
        d = {}
        for k, v in self.__dict__.items():
            if isinstance(v, Config):
                d[k] = v.as_dict()
            else:
                d[k] = v
        return d


def _convert(dictionary: dict):
    for key, value in dictionary.items():
        if isinstance(value, dict):
            dictionary[key] = _convert(value)
    c = Config()
    c.__dict__ = dictionary
    return c


def _read_config_files(config_path: str, file_extension: str):
    config_definition = ""

    abs_path = os.path.abspath(os.path.curdir + '/' + config_path)
    for filename in glob.glob(os.path.join(abs_path, '*' + file_extension)):
        with open(filename, 'r') as f:
            config_definition += f.read() + '\n'

    return parse_config(config_definition)


# # # # # # # # # # # # # # # #
#
# Semantic functions
#
# # # # # # # # # # # # # # # #


def _generate_absolute_dict(configs) -> dict:
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
                # TODO: I can't figure out why the fick fack fuck this returns the quotation marks on either side of the
                #  string
                raise KeyError("The parent stage '{}' referenced from '{}' does not exist"
                               .format(parent_realm_path, config_def[0]))

        d[config_def[0]] = _convert_to_dictionary_inner(config_def, ref_d)
    return d


def _convert_to_dictionary_inner(config: ParseResults, ref_d: dict) -> dict:
    d = {}
    if _does_extends_parent(config):
        d = ref_d.copy()
    for k, v in config.items():
        if isinstance(v, ParseResults):
            d[k] = _convert_to_dictionary_inner(v, ref_d[k] if k in ref_d else {})
        else:
            d[k] = v
    return d


def _get_alias_to_fully_qualified_realm_path_mapping(configs: List[ParseResults]) -> dict:
    d = {}
    for config in configs:
        fqdn, alias = config[0], config[1]
        d[alias] = fqdn
    return d


def _does_extends_parent(config):
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


def parse_config(text: str):
    return grammar().parseString(text, parseAll=True)


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

    config_key = Suppress('"') + Word(alphas, alphanums + '_') + Suppress('"')

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
