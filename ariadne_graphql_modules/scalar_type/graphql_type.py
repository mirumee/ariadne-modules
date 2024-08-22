from typing import Any, Dict, Generic, Optional, TypeVar, cast

from graphql import (
    NameNode,
    ScalarTypeDefinitionNode,
    ValueNode,
    value_from_ast_untyped,
)

from ..description import get_description_node
from .models import GraphQLScalarModel

from ..utils import parse_definition

from .validators import validate_scalar_type_with_schema

from ..base import GraphQLMetadata, GraphQLModel, GraphQLType


T = TypeVar("T")


class GraphQLScalar(GraphQLType, Generic[T]):
    __abstract__: bool = True
    __schema__: Optional[str]

    wrapped_value: T

    def __init__(self, value: T):
        self.wrapped_value = value

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        if cls.__dict__.get("__abstract__"):
            return

        cls.__abstract__ = False

        if cls.__dict__.get("__schema__"):
            validate_scalar_type_with_schema(cls)

    @classmethod
    def __get_graphql_model__(cls, metadata: GraphQLMetadata) -> "GraphQLModel":
        name = cls.__get_graphql_name__()

        if getattr(cls, "__schema__", None):
            return cls.__get_graphql_model_with_schema__()

        return cls.__get_graphql_model_without_schema__(name)

    @classmethod
    def __get_graphql_model_with_schema__(cls) -> "GraphQLModel":
        definition = cast(
            ScalarTypeDefinitionNode,
            parse_definition(ScalarTypeDefinitionNode, cls.__schema__),
        )

        return GraphQLScalarModel(
            name=definition.name.value,
            ast_type=ScalarTypeDefinitionNode,
            ast=definition,
            serialize=cls.serialize,
            parse_value=cls.parse_value,
            parse_literal=cls.parse_literal,
        )

    @classmethod
    def __get_graphql_model_without_schema__(cls, name: str) -> "GraphQLModel":
        return GraphQLScalarModel(
            name=name,
            ast_type=ScalarTypeDefinitionNode,
            ast=ScalarTypeDefinitionNode(
                name=NameNode(value=name),
                description=get_description_node(
                    getattr(cls, "__description__", None),
                ),
            ),
            serialize=cls.serialize,
            parse_value=cls.parse_value,
            parse_literal=cls.parse_literal,
        )

    @classmethod
    def serialize(cls, value: Any) -> Any:
        if isinstance(value, cls):
            return value.unwrap()

        return value

    @classmethod
    def parse_value(cls, value: Any) -> Any:
        return value

    @classmethod
    def parse_literal(
        cls, node: ValueNode, variables: Optional[Dict[str, Any]] = None
    ) -> Any:
        return cls.parse_value(value_from_ast_untyped(node, variables))

    def unwrap(self) -> T:
        return self.wrapped_value
