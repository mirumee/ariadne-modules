from decimal import Decimal
from enum import Enum

import pytest
from graphql import (
    BooleanValueNode,
    ConstListValueNode,
    ConstObjectValueNode,
    EnumValueNode,
    FloatValueNode,
    IntValueNode,
    NullValueNode,
    StringValueNode,
    print_ast,
)

from ariadne_graphql_modules import get_value_from_node, get_value_node


def test_get_false_value():
    node = get_value_node(False)
    assert isinstance(node, BooleanValueNode)
    assert print_ast(node) == "false"


def test_get_true_value():
    node = get_value_node(True)
    assert isinstance(node, BooleanValueNode)
    assert print_ast(node) == "true"


class PlainEnum(Enum):
    VALUE = "ok"


class IntEnum(int, Enum):
    VALUE = 21


class StrEnum(str, Enum):
    VALUE = "val"


def test_get_enum_value():
    node = get_value_node(PlainEnum.VALUE)
    assert isinstance(node, EnumValueNode)
    assert print_ast(node) == "VALUE"


def test_get_int_enum_value():
    node = get_value_node(IntEnum.VALUE)
    assert isinstance(node, EnumValueNode)
    assert print_ast(node) == "VALUE"


def test_get_str_enum_value():
    node = get_value_node(StrEnum.VALUE)
    assert isinstance(node, EnumValueNode)
    assert print_ast(node) == "VALUE"


def test_get_float_value():
    node = get_value_node(2.5)
    assert isinstance(node, FloatValueNode)
    assert print_ast(node) == "2.5"


def test_get_decimal_value():
    node = get_value_node(Decimal("2.33"))
    assert isinstance(node, FloatValueNode)
    assert print_ast(node) == "2.33"


def test_get_int_value():
    node = get_value_node(42)
    assert isinstance(node, IntValueNode)
    assert print_ast(node) == "42"


def test_get_str_value():
    node = get_value_node("Hello")
    assert isinstance(node, StringValueNode)
    assert print_ast(node) == '"Hello"'


def test_get_str_block_value():
    node = get_value_node("Hello\nWorld!")
    assert isinstance(node, StringValueNode)
    assert print_ast(node) == '"""\nHello\nWorld!\n"""'


def test_get_none_value():
    node = get_value_node(None)
    assert isinstance(node, NullValueNode)
    assert print_ast(node) == "null"


def test_get_list_value():
    node = get_value_node([1, 3, None])
    assert isinstance(node, ConstListValueNode)
    assert print_ast(node) == "[1, 3, null]"


def test_get_tuple_value():
    node = get_value_node((1, 3, None))
    assert isinstance(node, ConstListValueNode)
    assert print_ast(node) == "[1, 3, null]"


def test_get_dict_value():
    node = get_value_node({"a": 1, "c": 3, "d": None})
    assert isinstance(node, ConstObjectValueNode)
    assert print_ast(node) == "{a: 1, c: 3, d: null}"


def test_type_error_is_raised_for_unsupported_python_value():
    class CustomType:
        pass

    with pytest.raises(TypeError) as exc_info:
        get_value_node(CustomType())

    error_message = str(exc_info.value)
    assert error_message.startswith("Python value '<tests.")
    assert error_message.endswith(">' can't be represented as a GraphQL value node.")


def test_get_false_value_from_node():
    value = get_value_from_node(BooleanValueNode(value=False))
    assert value is False


def test_get_true_value_from_node():
    value = get_value_from_node(BooleanValueNode(value=True))
    assert value is True


def test_get_enum_value_from_node():
    value = get_value_from_node(EnumValueNode(value="USER"))
    assert value == "USER"


def test_get_float_value_from_node():
    value = get_value_from_node(FloatValueNode(value="2.5"))
    assert value == Decimal("2.5")


def test_get_int_value_from_node():
    value = get_value_from_node(IntValueNode(value="42"))
    assert value == 42


def test_get_str_value_from_node():
    value = get_value_from_node(StringValueNode(value="Hello"))
    assert value == "Hello"


def test_get_str_value_from_block_node():
    value = get_value_from_node(StringValueNode(value="Hello", block=True))
    assert value == "Hello"
