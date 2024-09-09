from collections.abc import Iterable, Sequence
from typing import Any, Optional, cast

from graphql import NamedTypeNode, NameNode, UnionTypeDefinitionNode

from ariadne_graphql_modules.base import GraphQLMetadata, GraphQLType
from ariadne_graphql_modules.base_graphql_model import GraphQLModel
from ariadne_graphql_modules.description import get_description_node
from ariadne_graphql_modules.object_type.graphql_type import GraphQLObject
from ariadne_graphql_modules.union_type.models import GraphQLUnionModel
from ariadne_graphql_modules.union_type.validators import (
    validate_union_type,
    validate_union_type_with_schema,
)
from ariadne_graphql_modules.utils import parse_definition


class GraphQLUnion(GraphQLType):
    __types__: Sequence[type[GraphQLType]]
    __schema__: Optional[str]

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        if cls.__dict__.get("__abstract__"):
            return

        cls.__abstract__ = False

        if cls.__dict__.get("__schema__"):
            validate_union_type_with_schema(cls)
        else:
            validate_union_type(cls)

    @classmethod
    def __get_graphql_model__(cls, metadata: GraphQLMetadata) -> "GraphQLModel":
        name = cls.__get_graphql_name__()
        metadata.set_graphql_name(cls, name)

        if getattr(cls, "__schema__", None):
            return cls.__get_graphql_model_with_schema__()

        return cls.__get_graphql_model_without_schema__(name)

    @classmethod
    def __get_graphql_model_with_schema__(cls) -> "GraphQLModel":
        definition = cast(
            UnionTypeDefinitionNode,
            parse_definition(UnionTypeDefinitionNode, cls.__schema__),
        )

        return GraphQLUnionModel(
            name=definition.name.value,
            ast_type=UnionTypeDefinitionNode,
            ast=definition,
            resolve_type=cls.resolve_type,
        )

    @classmethod
    def __get_graphql_model_without_schema__(cls, name: str) -> "GraphQLModel":
        return GraphQLUnionModel(
            name=name,
            ast_type=UnionTypeDefinitionNode,
            ast=UnionTypeDefinitionNode(
                name=NameNode(value=name),
                description=get_description_node(
                    getattr(cls, "__description__", None),
                ),
                types=tuple(
                    NamedTypeNode(name=NameNode(value=t.__get_graphql_name__()))
                    for t in cls.__types__
                ),
            ),
            resolve_type=cls.resolve_type,
        )

    @classmethod
    def __get_graphql_types__(
        cls, _: "GraphQLMetadata"
    ) -> Iterable[type["GraphQLType"]]:
        """Returns iterable with GraphQL types associated with this type"""
        return [cls, *cls.__types__]

    @staticmethod
    def resolve_type(obj: Any, *_) -> str:
        if isinstance(obj, GraphQLObject):
            return obj.__get_graphql_name__()

        raise ValueError(
            f"Cannot resolve GraphQL type {obj} "
            "for object of type '{type(obj).__name__}'."
        )
