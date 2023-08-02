from typing import Dict, Iterable, List, Optional, Type

from ariadne import ObjectType as ObjectTypeBindable
from ariadne.types import Resolver
from graphql import (
    FieldDefinitionNode,
    GraphQLSchema,
    NameNode,
    NamedTypeNode,
    NonNullTypeNode,
    ObjectTypeDefinitionNode,
)

from .base import GraphQLModel, GraphQLType
from .convert_name import convert_python_name_to_graphql


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

            fields_ast.append(
                FieldDefinitionNode(
                    name=NameNode(value=field.name),
                    type=NonNullTypeNode(
                        type=NamedTypeNode(
                            name=NameNode(value="String"),
                        ),
                    ),
                )
            )

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
        type: Optional[Type[GraphQLType]] = None,
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
        resolver: Optional[Resolver] = None,
    ):
        self.name = name
        self.resolver = resolver


def object_field(
    f: Optional[Resolver] = None,
    *,
    name: Optional[str] = None,
    type: Optional[Type[GraphQLType]] = None,
):
    def object_field_factory(f: Optional[Resolver]) -> GraphQLObjectField:
        return GraphQLObjectField(
            resolver=f,
            name=name or convert_python_name_to_graphql(f.__name__),
        )

    if f is not None:
        if any((name, type)):
            raise ValueError(
                "'object_field' decorator was called with function argument "
                "and the options."
            )

        return object_field_factory(f)
    
    return object_field_factory


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

