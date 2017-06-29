from pyparsing import Forward, Keyword, replaceWith, quotedString, removeQuotes, Combine, Optional, Word, nums, \
    Suppress, Group, ZeroOrMore, Dict, alphas

from easyconfig.config_dto import ConfigRecord

# # # # # # # # # # # # # # # #
#
# Grammar
#
# # # # # # # # # # # # # # # #


# noinspection PyPep8Naming
def grammar():
    primitive = Forward()

    EXTENDS = Keyword("extends")

    TRUE = Keyword("True").setParseAction(replaceWith(True))
    FALSE = Keyword("False").setParseAction(replaceWith(False))
    BOOLEAN = (TRUE | FALSE)
    NULL = Keyword("None").setParseAction(replaceWith(None))
    STRING = quotedString.setParseAction(removeQuotes)
    NUMBER = Combine(Optional('-') + ('0' | Word('123456789', nums)) + Optional('.' + Word(nums))).addParseAction(
        convert_numbers)
    LIST = Suppress('[') + Group(Optional(primitive) + ZeroOrMore(Suppress(',') + primitive)).addParseAction(
        convert_list) + Suppress(']')

    primitive << (STRING | NUMBER | BOOLEAN | NULL | LIST)

    config_key = STRING  # Word(alphas, alphanums + '_')

    config_block = Forward()
    config_line = Group(config_key + Suppress(':') + (primitive | config_block))
    config_lines = Dict(config_line + ZeroOrMore(Suppress(',') + config_line)).setParseAction(convert_dictionary)

    config_block << Suppress('{') + Optional(config_lines, default=[]) + Suppress('}')

    realm_name = Word(alphas)

    config_definition = Suppress(':') + config_block
    extends = Suppress(EXTENDS) + realm_name

    config_group = Group(realm_name + Optional(extends, default=None) + config_definition).setParseAction(
        convert_config_record)

    expression = ZeroOrMore(config_group)
    return expression


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


def convert_dictionary(s, l, toks):
    return {k: v for k, v in toks.asDict().items()}


def convert_config_record(s, l, toks):
    toks = convert_list(s, l, toks[0])
    print(toks)
    return ConfigRecord(toks[0], toks[1], toks[2])
