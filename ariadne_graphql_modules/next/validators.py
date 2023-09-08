from typing import Any, Type

from .objecttype import GraphQLType


def validate_description(cls: Type[GraphQLType], definition: Any):
    if getattr(cls, "__description__", None) and definition.description:
        raise ValueError(
            f"Class '{cls.__name__}' defines description in both "
            "'__description__' and '__schema__' attributes."
        )
