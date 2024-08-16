from typing import Type, cast, TYPE_CHECKING

from graphql import UnionTypeDefinitionNode


from ..validators import validate_description, validate_name
from ...utils import parse_definition

if TYPE_CHECKING:
    from .union_type import GraphQLUnion


def validate_union_type(cls: Type["GraphQLUnion"]) -> None:
    types = getattr(cls, "__types__", None)
    if not types:
        raise ValueError(
            f"Class '{cls.__name__}' is missing a '__types__' attribute "
            "with list of types belonging to a union."
        )


def validate_union_type_with_schema(cls: Type["GraphQLUnion"]) -> None:
    definition = cast(
        UnionTypeDefinitionNode,
        parse_definition(UnionTypeDefinitionNode, cls.__schema__),
    )

    if not isinstance(definition, UnionTypeDefinitionNode):
        raise ValueError(
            f"Class '{cls.__name__}' defines a '__schema__' attribute "
            "with declaration for an invalid GraphQL type. "
            f"('{definition.__class__.__name__}' != "
            f"'{UnionTypeDefinitionNode.__name__}')"
        )

    validate_name(cls, definition)
    validate_description(cls, definition)

    schema_type_names = {
        type_node.name.value
        for type_node in definition.types  # pylint: disable=no-member
    }

    class_type_names = {t.__get_graphql_name__() for t in cls.__types__}
    if not class_type_names.issubset(schema_type_names):
        missing_in_schema = sorted(class_type_names - schema_type_names)
        missing_in_schema_str = "', '".join(missing_in_schema)
        raise ValueError(
            f"Types '{missing_in_schema_str}' are in '__types__' but not in '__schema__'."
        )

    if not schema_type_names.issubset(class_type_names):
        missing_in_types = sorted(schema_type_names - class_type_names)
        missing_in_types_str = "', '".join(missing_in_types)
        raise ValueError(
            f"Types '{missing_in_types_str}' are in '__schema__' but not in '__types__'."
        )
