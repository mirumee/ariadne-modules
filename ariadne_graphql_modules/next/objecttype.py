from typing import Iterable, Optional, Tuple, Type

from ariadne.types import Resolver
from graphql import ObjectTypeDefinitionNode

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
        return GraphQLObjectModel(
            name=cls.__get_graphql_name__(),
            fields=tuple(
                field for field in dir(cls).values()
                if isinstance(field, GraphQLObjectField)
            )
        )


def validate_object_type(graphql_type: Type[GraphQLObject]):
    pass


def validate_object_type_with_schema(graphql_type: Type[GraphQLObject]):
    pass


class GraphQLObjectField:
    def __init__(self, *, resolver: Resolver, name: str):
        self.resolver = resolver
        self.name = str


def object_field(f: Optional[Resolver] = None, *, name: Optional[str] = None):
    def object_field_factory(f: Optional[Resolver]) -> GraphQLObjectField:
        return GraphQLObjectField(
            resolver=f,
            name=name or convert_python_name_to_graphql(f.__name__),
        )

    if f is not None:
        if name is not None:
            raise ValueError(
                "'object_field' decorator was called with both function argument "
                "and the options."
            )

        return object_field_factory(f)
    
    return object_field_factory


class GraphQLObjectModel(GraphQLModel):
    ast_type = ObjectTypeDefinitionNode
    fields: Tuple[GraphQLObjectField]
