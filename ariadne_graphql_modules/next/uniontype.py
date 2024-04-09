from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    Iterable,
    NoReturn,
    Sequence,
    Type,
    cast,
)

from ariadne import UnionType
from graphql import (
    GraphQLSchema,
    NameNode,
    NamedTypeNode,
    UnionTypeDefinitionNode,
)

from ..utils import parse_definition
from .base import GraphQLMetadata, GraphQLModel, GraphQLType
from .description import get_description_node
from .objecttype import GraphQLObject
from .validators import validate_description, validate_name


class GraphQLUnion(GraphQLType):
    __types__: Sequence[Type[GraphQLType]]

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
            return cls.__get_graphql_model_with_schema__(metadata, name)

        return cls.__get_graphql_model_without_schema__(metadata, name)

    @classmethod
    def __get_graphql_model_with_schema__(
        cls, metadata: GraphQLMetadata, name: str
    ) -> "GraphQLModel":
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
    def __get_graphql_model_without_schema__(
        cls, metadata: GraphQLMetadata, name: str
    ) -> "GraphQLModel":
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
        cls, metadata: "GraphQLMetadata"
    ) -> Iterable["GraphQLType"]:
        """Returns iterable with GraphQL types associated with this type"""
        return [cls] + cls.__types__

    @staticmethod
    def resolve_type(obj: Any, *args) -> str:
        if isinstance(obj, GraphQLObject):
            return obj.__get_graphql_name__()

        raise ValueError(
            f"Cannot resolve GraphQL type {obj} for object of type '{type(obj).__name__}'."
        )


def validate_union_type(cls: Type[GraphQLUnion]) -> NoReturn:
    types = getattr(cls, "__types__", None)
    if not types:
        raise ValueError(
            f"Class '{cls.__name__}' is missing a '__types__' attribute "
            "with list of types belonging to a union."
        )


def validate_union_type_with_schema(cls: Type[GraphQLUnion]) -> NoReturn:
    definition = cast(
        UnionTypeDefinitionNode,
        parse_definition(UnionTypeDefinitionNode, cls.__schema__),
    )

    if not isinstance(definition, UnionTypeDefinitionNode):
        raise ValueError(
            f"Class '{cls.__name__}' defines a '__schema__' attribute "
            "with declaration for an invalid GraphQL type. "
            f"('{definition.__class__.__name__}' != "
            f"'{UnionTypeDefinitionNode.__name__}')"
        )

    validate_name(cls, definition)
    validate_description(cls, definition)

    schema_type_names = {type_node.name.value for type_node in definition.types}

    class_type_names = {t.__get_graphql_name__() for t in cls.__types__}
    if not class_type_names.issubset(schema_type_names):
        missing_in_schema = class_type_names - schema_type_names
        raise ValueError(
            f"Types {missing_in_schema} are defined in __types__ but not present in the __schema__."
        )

    if not schema_type_names.issubset(class_type_names):
        missing_in_types = schema_type_names - class_type_names
        raise ValueError(
            f"Types {missing_in_types} are present in the __schema__ but not defined in __types__."
        )


@dataclass(frozen=True)
class GraphQLUnionModel(GraphQLModel):
    resolve_type: Callable[[Any], Any]

    def bind_to_schema(self, schema: GraphQLSchema):
        bindable = UnionType(self.name, self.resolve_type)
        bindable.bind_to_schema(schema)
