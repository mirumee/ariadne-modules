from dataclasses import dataclass
from typing import Any, Callable, Dict, Generic, Optional, Type, TypeVar, cast

from ariadne import ScalarType as ScalarTypeBindable
from graphql import (
    GraphQLSchema,
    NameNode,
    ScalarTypeDefinitionNode,
    ValueNode,
    value_from_ast_untyped,
)

from ..utils import parse_definition
from .base import GraphQLMetadata, GraphQLModel, GraphQLType
from .description import get_description_node
from .validators import validate_description, validate_name

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


@dataclass(frozen=True)
class GraphQLScalarModel(GraphQLModel):
    serialize: Callable[[Any], Any]
    parse_value: Callable[[Any], Any]
    parse_literal: Callable[[ValueNode, Optional[Dict[str, Any]]], Any]

    def bind_to_schema(self, schema: GraphQLSchema):
        bindable = ScalarTypeBindable(
            self.name,
            serializer=self.serialize,
            value_parser=self.parse_value,
            literal_parser=self.parse_literal,
        )

        bindable.bind_to_schema(schema)


def validate_scalar_type_with_schema(cls: Type[GraphQLScalar]):
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
