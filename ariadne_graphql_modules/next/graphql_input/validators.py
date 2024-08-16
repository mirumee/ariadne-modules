from typing import Any, Dict, List, Type, cast, TYPE_CHECKING

from graphql import InputObjectTypeDefinitionNode
from ..convert_name import convert_graphql_name_to_python
from ..validators import validate_description, validate_name
from ..value import get_value_from_node, get_value_node
from ...utils import parse_definition
from .input_field import GraphQLInputField

if TYPE_CHECKING:
    from .input_type import GraphQLInput


def validate_input_type_with_schema(cls: Type["GraphQLInput"]) -> Dict[str, Any]:
    definition = cast(
        InputObjectTypeDefinitionNode,
        parse_definition(InputObjectTypeDefinitionNode, cls.__schema__),
    )

    if not isinstance(definition, InputObjectTypeDefinitionNode):
        raise ValueError(
            f"Class '{cls.__name__}' defines '__schema__' attribute "
            "with declaration for an invalid GraphQL type. "
            f"('{definition.__class__.__name__}' != "
            f"'{InputObjectTypeDefinitionNode.__name__}')"
        )

    validate_name(cls, definition)
    validate_description(cls, definition)

    if not definition.fields:
        raise ValueError(
            f"Class '{cls.__name__}' defines '__schema__' attribute "
            "with declaration for an input type without any fields. "
        )

    fields_names: List[str] = [field.name.value for field in definition.fields]
    used_out_names: List[str] = []

    out_names: Dict[str, str] = getattr(cls, "__out_names__", {}) or {}
    for field_name, out_name in out_names.items():
        if field_name not in fields_names:
            raise ValueError(
                f"Class '{cls.__name__}' defines an outname for '{field_name}' "
                "field in it's '__out_names__' attribute which is not defined "
                "in '__schema__'."
            )

        if out_name in used_out_names:
            raise ValueError(
                f"Class '{cls.__name__}' defines multiple fields with an outname "
                f"'{out_name}' in it's '__out_names__' attribute."
            )

        used_out_names.append(out_name)

    return get_input_type_with_schema_kwargs(cls, definition, out_names)


def get_input_type_with_schema_kwargs(
    cls: Type["GraphQLInput"],
    definition: InputObjectTypeDefinitionNode,
    out_names: Dict[str, str],
) -> Dict[str, Any]:
    kwargs: Dict[str, Any] = {}
    for field in definition.fields:
        try:
            python_name = out_names[field.name.value]
        except KeyError:
            python_name = convert_graphql_name_to_python(field.name.value)

        attr_default_value = getattr(cls, python_name, None)
        if attr_default_value is not None and not callable(attr_default_value):
            default_value = attr_default_value
        elif field.default_value:
            default_value = get_value_from_node(field.default_value)
        else:
            default_value = None

        kwargs[python_name] = default_value

    return kwargs


def validate_input_type(cls: Type["GraphQLInput"]) -> Dict[str, Any]:
    if cls.__out_names__:
        raise ValueError(
            f"Class '{cls.__name__}' defines '__out_names__' attribute. "
            "This is not supported for types not defining '__schema__'."
        )

    return get_input_type_kwargs(cls)


def get_input_type_kwargs(cls: Type["GraphQLInput"]) -> Dict[str, Any]:
    kwargs: Dict[str, Any] = {}

    for attr_name in cls.__annotations__:
        if attr_name.startswith("__"):
            continue

        attr_value = getattr(cls, attr_name, None)
        if isinstance(attr_value, GraphQLInputField):
            validate_field_default_value(cls, attr_name, attr_value.default_value)
            kwargs[attr_name] = attr_value.default_value
        elif not callable(attr_value):
            validate_field_default_value(cls, attr_name, attr_value)
            kwargs[attr_name] = attr_value

    return kwargs


def validate_field_default_value(
    cls: Type["GraphQLInput"], field_name: str, default_value: Any
):
    if default_value is None:
        return

    try:
        get_value_node(default_value)
    except TypeError as e:
        raise TypeError(
            f"Class '{cls.__name__}' defines default value "
            f"for the '{field_name}' field that can't be "
            "represented in GraphQL schema."
        ) from e
