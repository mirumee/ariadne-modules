from typing import TYPE_CHECKING, Any, cast

from graphql import InputObjectTypeDefinitionNode

from ariadne_graphql_modules.convert_name import convert_graphql_name_to_python
from ariadne_graphql_modules.input_type.graphql_field import GraphQLInputField
from ariadne_graphql_modules.utils import parse_definition
from ariadne_graphql_modules.validators import validate_description, validate_name
from ariadne_graphql_modules.value import get_value_from_node, get_value_node

if TYPE_CHECKING:
    from ariadne_graphql_modules.input_type.graphql_type import GraphQLInput


def validate_input_type_with_schema(cls: type["GraphQLInput"]) -> dict[str, Any]:
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

    fields_names: list[str] = [field.name.value for field in definition.fields]
    used_out_names: list[str] = []

    out_names: dict[str, str] = getattr(cls, "__out_names__", {}) or {}
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
    cls: type["GraphQLInput"],
    definition: InputObjectTypeDefinitionNode,
    out_names: dict[str, str],
) -> dict[str, Any]:
    kwargs: dict[str, Any] = {}
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


def validate_input_type(cls: type["GraphQLInput"]) -> dict[str, Any]:
    if cls.__out_names__:
        raise ValueError(
            f"Class '{cls.__name__}' defines '__out_names__' attribute. "
            "This is not supported for types not defining '__schema__'."
        )

    return get_input_type_kwargs(cls)


def get_input_type_kwargs(cls: type["GraphQLInput"]) -> dict[str, Any]:
    kwargs: dict[str, Any] = {}

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
    cls: type["GraphQLInput"], field_name: str, default_value: Any
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
