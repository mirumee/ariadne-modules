from typing import Any, Type

from .base import GraphQLType


def validate_name(cls: Type[GraphQLType], definition: Any):
    graphql_name = getattr(cls, "__graphql_name__", None)

    if graphql_name and definition.name.value != graphql_name:
        raise ValueError(
            f"Class '{cls.__name__}' defines both '__graphql_name__' and "
            f"'__schema__' attributes, but names in those don't match. "
            f"('{graphql_name}' != '{definition.name.value}')"
        )

    setattr(cls, "__graphql_name__", definition.name.value)


def validate_description(cls: Type[GraphQLType], definition: Any):
    if getattr(cls, "__description__", None) and definition.description:
        raise ValueError(
            f"Class '{cls.__name__}' defines description in both "
            "'__description__' and '__schema__' attributes."
        )
