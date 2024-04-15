from dataclasses import dataclass
from typing import Any, Dict, Optional

from ariadne.types import Resolver


@dataclass
class GraphQLObjectFieldArg:
    name: str
    out_name: str
    type: Any
    description: Optional[str] = None
    default_value: Optional[Any] = None


class GraphQLObjectField:
    name: Optional[str]
    description: Optional[str]
    type: Optional[Any]
    args: Optional[Dict[str, dict]]
    resolver: Optional[Resolver]
    default_value: Optional[Any]

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        type: Optional[Any] = None,
        args: Optional[Dict[str, dict]] = None,
        resolver: Optional[Resolver] = None,
        default_value: Optional[Any] = None,
    ):
        self.name = name
        self.description = description
        self.type = type
        self.args = args
        self.resolver = resolver
        self.default_value = default_value

    def __call__(self, resolver: Resolver):
        """Makes GraphQLObjectField instances work as decorators."""
        self.resolver = resolver
        if not self.type:
            self.type = get_field_type_from_resolver(resolver)
        return self


def get_field_type_from_resolver(resolver: Resolver) -> Any:
    return resolver.__annotations__.get("return")
