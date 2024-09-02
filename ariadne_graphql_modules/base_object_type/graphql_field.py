from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from ariadne.types import Resolver, Subscriber
from graphql import FieldDefinitionNode, NamedTypeNode


@dataclass(frozen=True)
class GraphQLObjectFieldArg:
    name: Optional[str]
    out_name: Optional[str]
    field_type: Optional[Any]
    description: Optional[str] = None
    default_value: Optional[Any] = None


@dataclass(frozen=True)
class GraphQLObjectData:
    fields: Dict[str, "GraphQLObjectField"]
    interfaces: List[NamedTypeNode]


@dataclass
class GraphQLClassData:
    type_aliases: Dict[str, str] = field(default_factory=dict)
    fields_ast: Dict[str, FieldDefinitionNode] = field(default_factory=dict)
    resolvers: Dict[str, "Resolver"] = field(default_factory=dict)
    aliases: Dict[str, str] = field(default_factory=dict)
    out_names: Dict[str, Dict[str, str]] = field(default_factory=dict)


@dataclass(frozen=True)
class GraphQLObjectResolver:
    resolver: Resolver
    field: str
    description: Optional[str] = None
    args: Optional[Dict[str, GraphQLObjectFieldArg]] = None
    field_type: Optional[Any] = None


@dataclass(frozen=True)
class GraphQLObjectSource:
    subscriber: Subscriber
    field: str
    description: Optional[str] = None
    args: Optional[Dict[str, GraphQLObjectFieldArg]] = None
    field_type: Optional[Any] = None


@dataclass
class GraphQLFieldData:
    fields_types: Dict[str, str] = field(default_factory=dict)
    fields_names: Dict[str, str] = field(default_factory=dict)
    fields_descriptions: Dict[str, str] = field(default_factory=dict)
    fields_args: Dict[str, Dict[str, GraphQLObjectFieldArg]] = field(
        default_factory=dict
    )
    fields_resolvers: Dict[str, Resolver] = field(default_factory=dict)
    fields_subscribers: Dict[str, Subscriber] = field(default_factory=dict)
    fields_defaults: Dict[str, Any] = field(default_factory=dict)
    fields_order: List[str] = field(default_factory=list)
    type_hints: Dict[str, Any] = field(default_factory=dict)
    aliases: Dict[str, str] = field(default_factory=dict)
    aliases_targets: List[str] = field(default_factory=list)


class GraphQLObjectField:
    def __init__(
        self,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        field_type: Optional[Any] = None,
        args: Optional[Dict[str, GraphQLObjectFieldArg]] = None,
        resolver: Optional[Resolver] = None,
        subscriber: Optional[Subscriber] = None,
        default_value: Optional[Any] = None,
    ):
        self.name = name
        self.description = description
        self.field_type = field_type
        self.args = args
        self.resolver = resolver
        self.subscriber = subscriber
        self.default_value = default_value

    def __call__(self, resolver: Resolver):
        """Makes GraphQLObjectField instances work as decorators."""
        self.resolver = resolver
        if not self.field_type:
            self.field_type = get_field_type_from_resolver(resolver)
        return self


def object_field(
    resolver: Optional[Resolver] = None,
    *,
    args: Optional[Dict[str, GraphQLObjectFieldArg]] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    graphql_type: Optional[Any] = None,
    default_value: Optional[Any] = None,
) -> GraphQLObjectField:
    if isinstance(resolver, staticmethod):
        resolver = resolver.__func__
    field_type: Any = graphql_type
    if not graphql_type and resolver:
        field_type = get_field_type_from_resolver(resolver)
    return GraphQLObjectField(
        name=name,
        description=description,
        field_type=field_type,
        args=args,
        resolver=resolver,
        default_value=default_value,
    )


def get_field_type_from_resolver(resolver: Resolver) -> Any:
    if isinstance(resolver, staticmethod):
        resolver = resolver.__func__
    return resolver.__annotations__.get("return")


def get_field_type_from_subscriber(subscriber: Subscriber) -> Any:
    if isinstance(subscriber, staticmethod):
        subscriber = subscriber.__func__
    return subscriber.__annotations__.get("return")


def object_resolver(
    field: str,
    graphql_type: Optional[Any] = None,
    args: Optional[Dict[str, GraphQLObjectFieldArg]] = None,
    description: Optional[str] = None,
):
    def object_resolver_factory(f: Resolver) -> GraphQLObjectResolver:
        if isinstance(f, staticmethod):
            f = f.__func__
        return GraphQLObjectResolver(
            args=args,
            description=description,
            resolver=f,
            field=field,
            field_type=graphql_type or get_field_type_from_resolver(f),
        )

    return object_resolver_factory


def object_subscriber(
    field: str,
    graphql_type: Optional[Any] = None,
    args: Optional[Dict[str, GraphQLObjectFieldArg]] = None,
    description: Optional[str] = None,
):
    def object_subscriber_factory(f: Subscriber) -> GraphQLObjectSource:
        if isinstance(f, staticmethod):
            f = f.__func__
        return GraphQLObjectSource(
            args=args,
            description=description,
            subscriber=f,
            field=field,
            field_type=graphql_type or get_field_type_from_subscriber(f),
        )

    return object_subscriber_factory
