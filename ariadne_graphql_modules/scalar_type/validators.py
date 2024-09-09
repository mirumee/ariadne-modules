from typing import TYPE_CHECKING

from graphql import ScalarTypeDefinitionNode

from ariadne_graphql_modules.utils import parse_definition
from ariadne_graphql_modules.validators import validate_description, validate_name

if TYPE_CHECKING:
    from ariadne_graphql_modules.scalar_type.graphql_type import GraphQLScalar


def validate_scalar_type_with_schema(cls: type["GraphQLScalar"]):
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
