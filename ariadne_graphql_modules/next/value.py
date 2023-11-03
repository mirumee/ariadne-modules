from decimal import Decimal
from enum import Enum
from typing import Any, Iterable, Mapping

from graphql import (
    BooleanValueNode,
    ConstListValueNode,
    ConstObjectFieldNode,
    ConstObjectValueNode,
    ConstValueNode,
    EnumValueNode,
    FloatValueNode,
    IntValueNode,
    ListValueNode,
    NameNode,
    NullValueNode,
    ObjectValueNode,
    StringValueNode,
)


def get_value_node(value: Any):
    if value is False or value is True:
        return BooleanValueNode(value=value)

    if isinstance(value, Enum):
        return EnumValueNode(value=value.name)

    if isinstance(value, (float, Decimal)):
        return FloatValueNode(value=str(value))

    if isinstance(value, int):
        return IntValueNode(value=str(value))

    if value is None:
        return NullValueNode()

    if isinstance(value, str):
        return StringValueNode(value=value, block="\n" in value)

    if isinstance(value, Mapping):
        return ConstObjectValueNode(
            fields=tuple(
                ConstObjectFieldNode(
                    name=NameNode(value=str(name)), value=get_value_node(val)
                )
                for name, val in value.items()
            ),
        )

    if isinstance(value, Iterable):
        return ConstListValueNode(
            values=tuple(get_value_node(val) for val in value),
        )

    raise TypeError(
        f"Python value '{repr(value)}' can't be represented as a GraphQL value node."
    )


def get_value_from_node(node: ConstValueNode) -> Any:
    if isinstance(node, BooleanValueNode):
        return node.value

    if isinstance(node, EnumValueNode):
        return node.value

    if isinstance(node, FloatValueNode):
        return Decimal(node.value)

    if isinstance(node, IntValueNode):
        return int(node.value)

    if isinstance(node, NullValueNode):
        return None

    if isinstance(node, StringValueNode):
        return node.value

    if isinstance(node, (ConstObjectValueNode, ObjectValueNode)):
        return {field.name.value: get_value_from_node(field) for field in node.fields}

    if isinstance(node, ListValueNode):
        return [get_value_from_node(value) for value in node.values]

    raise TypeError(
        f"GraphQL node '{repr(node)}' can't be represented as a Python value."
    )
