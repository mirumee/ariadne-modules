from typing import TYPE_CHECKING, Type

from graphql import ScalarTypeDefinitionNode

from ..validators import validate_description, validate_name

from ...utils import parse_definition

if TYPE_CHECKING:
    from .scalar_type import GraphQLScalar


def validate_scalar_type_with_schema(cls: Type["GraphQLScalar"]):
    definition = parse_definition(cls.__name__, cls.__schema__)

    if not isinstance(definition, ScalarTypeDefinitionNode):
        raise ValueError(
            f"Class '{cls.__name__}' defines '__schema__' attribute "
            "with declaration for an invalid GraphQL type. "
            f"('{definition.__class__.__name__}' != "
            f"'{ScalarTypeDefinitionNode.__name__}')"
        )

    validate_name(cls, definition)
    validate_description(cls, definition)
