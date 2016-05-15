import glob
import os
from typing import List, Dict

from pip._vendor.pyparsing import dblQuotedString, removeQuotes, Suppress, Combine, Optional, Word, nums, Forward, \
    Keyword, replaceWith, Group, ZeroOrMore, alphas


class EasyConfig(object):
    def __init__(self, stage, config_path, file_extension='.config'):
        self.stage = stage()
        self._config = self._read_config_files(config_path, file_extension)

    @staticmethod
    def _read_config_files(config_path, file_extension):
        grammar_definition = grammar()
        config_definition = ""

        abs_path = os.path.abspath(os.path.curdir + '/' + config_path)
        for filename in glob.glob(os.path.join(abs_path, '*' + file_extension)):
            with open(filename, 'r') as f:
                config_definition += f.read() + '\n'

        parsed_string = grammar_definition.parseString(config_definition, True)
        preprocessed_dictionary = generate_config_definition(parsed_string)
        return generate_absolute_dict(preprocessed_dictionary)

    def get(self, key: str):
        pass

    def __str__(self):
        return "To be implemented"


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


class Override(object):
    pass


class Redirect(object):
    def __init__(self, to_where):
        self.to_where = to_where


# # # # # # # # # # # # # # # #
#
# Config Results
#
# # # # # # # # # # # # # # # #


class ConfigPair(object):
    def __init__(self, key, config_data):
        self.key = key
        self.config_data = config_data

    def __call__(self, *args, **kwargs):
        return self.key, self.config_data


class Config(object):
    def __init__(self):
        self.config_pairs = []

    def add_config(self, config_pair: ConfigPair):
        self.config_pairs.append(config_pair)

    def pretty_print(self):
        s = ""
        for pair in self.config_pairs:
            s += "= %s =\n" % pair.key
            s += pretty_print(pair.config_data)
        return s


# # # # # # # # # # # # # # # #
#
# Semantic functions
#
# # # # # # # # # # # # # # # #


def generate_config_definition(definition: List) -> List[Config]:
    configs = []
    for d in definition:
        c = Config()
        realm_path = d[0]
        try:
            redirect_path = Redirect(d["redirect"])
            c.add_config(ConfigPair(realm_path, redirect_path))
        except KeyError:
            config = generate_dict(d[1])
            c.add_config(ConfigPair(realm_path, config))
        configs.append(c)
    return configs


def generate_dict(d: {}, is_override=False):
    new = {}
    for k in d:
        try:
            v = k["primitive"]
        except KeyError:
            try:
                v = generate_dict(k["nested"])
            except KeyError:
                v = generate_dict(k["override"][0], True)
        new[k["key"]] = v
        if is_override:
            new[Override] = None
    return new


def generate_absolute_dict(configs: List[Config]):
    d = {}
    for config in configs:
        print(config.config_pairs)
        for k, v in config.config_pairs:
            print(k)
            if isinstance(v, Redirect):
                d[k] = generate_absolute_dict_redirect(configs, v)
            else:
                d[k] = v
    return d


def generate_absolute_dict_redirect(configs: List[Config], redirect: Redirect):
    for c in configs:
        if redirect.to_where in c:
            return c[redirect.to_where]
    raise KeyError("The config contains no stage called '%s'" % redirect.to_where)


def pretty_print(d: dict, indent=1):
    offset = indent * '  '
    s = "{\n"
    if isinstance(d, Redirect):
        return "-> " + d.to_where + '\n'
    for k, v in d.items():
        s += offset
        if k == Override:
            s += "Overrides parent config" + '\n'
            continue
        s += '"{}": '.format(k)
        if isinstance(v, dict):
            s += pretty_print(v, indent + 1)
        else:
            s += str(v)
        s += '\n'
    return s + offset[:-2] + '}'


test = """
Beta -> Base.Beta

Base = {
    "key6" : {
        "nested0" : "base data",
        "nested1" : "base data",
        "nested2" : "base data"
    }
}

Base.Beta = {
    "key0" : "Jacob Zuma",
    "key1" : True,
    "key2" : False,
    "key3" : None,
    "key4" : [-1, 0.02, True, "lol"],
    "key5" : 1,
    "key6" :+ {
        "nested0" : "beta data",
        "nested1" : 2.1
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


# # # # # # # # # # # # # # # #
#
# Grammar
#
# # # # # # # # # # # # # # # #


# noinspection PyPep8Naming
def grammar():
    primitive = Forward()

    ALIAS = Keyword("->")
    TRUE = Keyword("True").setParseAction(replaceWith(True))
    FALSE = Keyword("False").setParseAction(replaceWith(False))
    BOOLEAN = (TRUE | FALSE)
    NULL = Keyword("None").setParseAction(replaceWith(None))
    STRING = dblQuotedString.setParseAction(removeQuotes)
    NUMBER = Combine(Optional('-') + ('0' | Word('123456789', nums)) + Optional('.' + Word(nums))).addParseAction(
        convert_numbers)
    LIST = Suppress('[') + Group(Optional(primitive) + ZeroOrMore(Suppress(',') + primitive)).addParseAction(
        convert_list) + Suppress(']')

    primitive << (STRING | NUMBER | BOOLEAN | NULL | LIST).setResultsName("primitive")

    config_key = STRING.setResultsName("key")

    config_block = Forward()
    override_block = Suppress('+') + config_block
    config_line = Group(config_key + Suppress(':') + (
        primitive | config_block.setResultsName("nested") | override_block.setResultsName("override")))
    config_lines = Group(config_line + ZeroOrMore(Suppress(',') + config_line))

    config_block << Suppress('{') + Optional(config_lines, default=[]) + Suppress('}')

    realm_name = Word(alphas)
    app_path = Combine(realm_name + ZeroOrMore('.' + realm_name))

    config_definition = Suppress('=') + config_block
    config_alias = Suppress(ALIAS) + app_path.setResultsName("redirect")

    config_group = Group(app_path + (config_definition | config_alias))

    expression = ZeroOrMore(config_group)
    return expression


if __name__ == "__main__":
    print(grammar().parseString(test))
    configs = generate_config_definition(grammar().parseString(test))

    for c in configs:
        print(c.pretty_print(), '\n')

    print(generate_absolute_dict(configs))
