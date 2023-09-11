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
from .base import GraphQLModel, GraphQLType
from .validators import validate_description, validate_name

T = TypeVar("T")


class GraphQLScalar(GraphQLType, Generic[T]):
    __abstract__: bool = True

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
    def __get_graphql_model__(cls) -> "GraphQLModel":
        name = cls.__get_graphql_name__()

        if getattr(cls, "__schema__", None):
            return cls.__get_graphql_model_with_schema__(name)

        return cls.__get_graphql_model_without_schema__(name)

    @classmethod
    def __get_graphql_model_with_schema__(cls, name: str) -> "GraphQLModel":
        definition = cast(
            ScalarTypeDefinitionNode,
            parse_definition(ScalarTypeDefinitionNode, cls.__schema__),
        )

        return GraphQScalarModel(
            name=definition.name.value,
            ast=definition,
            serialize=cls.serialize,
            parse_value=cls.parse_value,
            parse_literal=cls.parse_literal,
        )

    @classmethod
    def __get_graphql_model_without_schema__(cls, name: str) -> "GraphQLModel":
        return GraphQScalarModel(
            name=name,
            ast=ScalarTypeDefinitionNode(
                name=NameNode(value=name),
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


class GraphQScalarModel(GraphQLModel):
    ast_type = ScalarTypeDefinitionNode

    def __init__(
        self,
        name: str,
        ast: ScalarTypeDefinitionNode,
        serialize: Callable[[Any], Any],
        parse_value: Callable[[Any], Any],
        parse_literal: Callable[[ValueNode, Optional[Dict[str, Any]]], Any],
    ):
        self.name = name
        self.ast = ast
        self.serialize = serialize
        self.parse_value = parse_value
        self.parse_literal = parse_literal

    def bind_to_schema(self, schema: GraphQLSchema):
        bindable = ScalarTypeBindable(
            self.name,
            serializer=self.serialize,
            value_parser=self.parse_value,
            literal_parser=self.parse_literal,
        )

        bindable.bind_to_schema(schema)
