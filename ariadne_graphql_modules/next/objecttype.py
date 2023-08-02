from typing import Any, Dict, Iterable, List, Optional, Type, get_origin, get_type_hints

from ariadne import ObjectType as ObjectTypeBindable
from ariadne.types import Resolver
from graphql import (
    FieldDefinitionNode,
    GraphQLSchema,
    NameNode,
    NamedTypeNode,
    NonNullTypeNode,
    ObjectTypeDefinitionNode,
    TypeNode,
)

from .base import GraphQLModel, GraphQLType
from .convert_name import convert_python_name_to_graphql
from .typing import get_type_node


class GraphQLObject(GraphQLType):
    __schema__: Optional[str]
    __requires__: Optional[Iterable[GraphQLType]]

    __abstract__: bool = True

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        if cls.__dict__.get("__abstract__"):
            return

        cls.__abstract__ = False

        if cls.__dict__.get("__schema__"):
            validate_object_type_with_schema(cls)
        else:
            validate_object_type(cls)

    @classmethod
    def __get_graphql_model__(cls) -> "GraphQLModel":
        name = cls.__get_graphql_name__()
        fields_ast: List[FieldDefinitionNode] = []
        resolvers: Dict[str, Resolver] = {}
        out_names: Dict[str, Dict[str, str]] = {}

        for field in cls.__dict__.values():
            if not isinstance(field, GraphQLObjectField):
                continue

            if field.resolver:
                resolvers[field.name] = field.resolver

            fields_ast.append(get_field_node(field))

        return GraphQLObjectModel(
            name=name,
            ast=ObjectTypeDefinitionNode(
                name=NameNode(value=name),
                fields=tuple(fields_ast),
            ),
            resolvers=resolvers,
            out_names=out_names,
        )
    
    @staticmethod
    def field(
        f: Optional[Resolver] = None,
        *,
        name: Optional[str] = None,
        type: Optional[Any] = None,
    ):
        """Shortcut for using object_field() separately"""
        return object_field(f, name=name)


def validate_object_type(graphql_type: Type[GraphQLObject]):
    pass


def validate_object_type_with_schema(graphql_type: Type[GraphQLObject]):
    pass


class GraphQLObjectField:
    def __init__(
        self,
        *,
        name: str,
        type: Any,
        resolver: Optional[Resolver] = None,
    ):
        self.name = name
        self.type = type
        self.resolver = resolver


def object_field(
    f: Optional[Resolver] = None,
    *,
    name: Optional[str] = None,
    type: Optional[Any] = None,
):
    def object_field_factory(f: Optional[Resolver]) -> GraphQLObjectField:
        field_type: Any = None
        field_name = name or convert_python_name_to_graphql(f.__name__)

        if type:
            field_type = type
        elif f:
            field_type = get_field_type_from_resolver(f)

        if field_type is None:
            raise ValueError(
                f"Unable to find return type for field '{field_name}'. Either add "
                "return type annotation on it's resolver or specify return type "
                "explicitly via 'type=...' option."
            )

        return GraphQLObjectField(
            resolver=f,
            name=field_name,
            type=field_type,
        )

    if f is not None:
        if any((name, type)):
            raise ValueError(
                "'object_field' decorator was called with function argument "
                "and the options."
            )

        return object_field_factory(f)
    
    return object_field_factory


def get_field_type_from_resolver(resolver: Resolver):
    return_hint = get_type_hints(resolver).get("return")
    if not return_hint:
        raise ValueError(
            f"Resolver function '{resolver}' is missing return type's annotation."
        )

    return return_hint


class GraphQLObjectModel(GraphQLModel):
    ast_type = ObjectTypeDefinitionNode
    resolvers: Dict[str, Resolver]
    out_names: Dict[str, Dict[str, str]]

    def __init__(
        self,
        name: str,
        ast: ObjectTypeDefinitionNode,
        resolvers: Dict[str, Resolver],
        out_names: Dict[str, Dict[str, str]],
    ):
        self.name = name
        self.ast = ast
        self.resolvers = resolvers
        self.out_names = out_names

    def bind_to_schema(self, schema: GraphQLSchema):
        bindable = ObjectTypeBindable(self.name)

        for field, resolver in self.resolvers.items():
            bindable.set_field(field, resolver)

        bindable.bind_to_schema(schema)


def get_field_node(field: GraphQLObjectField) -> FieldDefinitionNode:
    return FieldDefinitionNode(
        name=NameNode(value=field.name),
        type=get_type_node(field.type),
    )
