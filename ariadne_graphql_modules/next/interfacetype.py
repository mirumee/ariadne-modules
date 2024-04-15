from dataclasses import dataclass
from enum import Enum
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Type,
    Union,
    cast,
    Sequence,
    NoReturn,
)

from ariadne import InterfaceType
from ariadne.types import Resolver
from graphql import (
    FieldDefinitionNode,
    GraphQLField,
    GraphQLObjectType,
    GraphQLSchema,
    NameNode,
    NamedTypeNode,
    InterfaceTypeDefinitionNode,
)

from .metadata import get_graphql_object_data
from .objectmixin import GraphQLModelHelpersMixin

from ..utils import parse_definition
from .base import GraphQLMetadata, GraphQLModel, GraphQLType
from .description import get_description_node
from .typing import get_graphql_type
from .validators import validate_description, validate_name


class GraphQLInterface(GraphQLType, GraphQLModelHelpersMixin):
    __types__: Sequence[Type[GraphQLType]]
    __implements__: Optional[Iterable[Union[Type[GraphQLType], Type[Enum]]]]

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        if cls.__dict__.get("__abstract__"):
            return

        cls.__abstract__ = False

        if cls.__dict__.get("__schema__"):
            validate_interface_type_with_schema(cls)
        else:
            validate_interface_type(cls)

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
    ) -> "GraphQLInterfaceModel":
        definition = cast(
            InterfaceTypeDefinitionNode,
            parse_definition(InterfaceTypeDefinitionNode, cls.__schema__),
        )
        resolvers: Dict[str, Resolver] = cls.collect_resolvers_with_schema()
        out_names: Dict[str, Dict[str, str]] = {}
        fields: List[FieldDefinitionNode] = cls.gather_fields_with_schema(definition)

        return GraphQLInterfaceModel(
            name=definition.name.value,
            ast_type=InterfaceTypeDefinitionNode,
            ast=InterfaceTypeDefinitionNode(
                name=NameNode(value=definition.name.value),
                fields=tuple(fields),
                interfaces=definition.interfaces,
            ),
            resolve_type=cls.resolve_type,
            resolvers=resolvers,
            aliases=getattr(cls, "__aliases__", {}),
            out_names=out_names,
        )

    @classmethod
    def __get_graphql_model_without_schema__(
        cls, metadata: GraphQLMetadata, name: str
    ) -> "GraphQLInterfaceModel":
        type_data = get_graphql_object_data(metadata, cls)

        fields_ast: List[FieldDefinitionNode] = cls.gather_fields_without_schema(
            metadata
        )
        interfaces_ast: List[NamedTypeNode] = cls.gather_interfaces_without_schema(
            type_data
        )
        resolvers: Dict[str, Resolver] = cls.collect_resolvers_without_schema(type_data)
        aliases: Dict[str, str] = cls.collect_aliases(type_data)
        out_names: Dict[str, Dict[str, str]] = cls.collect_out_names(type_data)

        return GraphQLInterfaceModel(
            name=name,
            ast_type=InterfaceTypeDefinitionNode,
            ast=InterfaceTypeDefinitionNode(
                name=NameNode(value=name),
                description=get_description_node(
                    getattr(cls, "__description__", None),
                ),
                fields=tuple(fields_ast),
                interfaces=tuple(interfaces_ast),
            ),
            resolve_type=cls.resolve_type,
            resolvers=resolvers,
            aliases=aliases,
            out_names=out_names,
        )

    @classmethod
    def __get_graphql_types__(
        cls, metadata: "GraphQLMetadata"
    ) -> Iterable["GraphQLType"]:
        """Returns iterable with GraphQL types associated with this type"""
        if getattr(cls, "__schema__", None):
            return cls.__get_graphql_types_with_schema__(metadata)

        return cls.__get_graphql_types_without_schema__(metadata)

    @classmethod
    def __get_graphql_types_with_schema__(
        cls, metadata: "GraphQLMetadata"
    ) -> Iterable["GraphQLType"]:
        types: List[GraphQLType] = [cls]
        types.extend(getattr(cls, "__requires__", []))
        return types

    @classmethod
    def __get_graphql_types_without_schema__(
        cls, metadata: "GraphQLMetadata"
    ) -> Iterable["GraphQLType"]:
        types: List[GraphQLType] = [cls]
        type_data = get_graphql_object_data(metadata, cls)

        for field in type_data.fields.values():
            field_type = get_graphql_type(field.type)
            if field_type and field_type not in types:
                types.append(field_type)

            if field.args:
                for field_arg in field.args.values():
                    field_arg_type = get_graphql_type(field_arg.type)
                    if field_arg_type and field_arg_type not in types:
                        types.append(field_arg_type)

        return types

    @staticmethod
    def resolve_type(obj: Any, *args) -> str:
        if isinstance(obj, GraphQLInterface):
            return obj.__get_graphql_name__()

        raise ValueError(
            f"Cannot resolve GraphQL type {obj} for object of type '{type(obj).__name__}'."
        )


def validate_interface_type(cls: Type[GraphQLInterface]) -> NoReturn:
    pass


def validate_interface_type_with_schema(cls: Type[GraphQLInterface]) -> NoReturn:
    definition = cast(
        InterfaceTypeDefinitionNode,
        parse_definition(InterfaceTypeDefinitionNode, cls.__schema__),
    )

    if not isinstance(definition, InterfaceTypeDefinitionNode):
        raise ValueError(
            f"Class '{cls.__name__}' defines a '__schema__' attribute "
            "with declaration for an invalid GraphQL type. "
            f"('{definition.__class__.__name__}' != "
            f"'{InterfaceTypeDefinitionNode.__name__}')"
        )

    validate_name(cls, definition)
    validate_description(cls, definition)


@dataclass(frozen=True)
class GraphQLInterfaceModel(GraphQLModel):
    resolvers: Dict[str, Resolver]
    resolve_type: Callable[[Any], Any]
    out_names: Dict[str, Dict[str, str]]
    aliases: Dict[str, str]

    def bind_to_schema(self, schema: GraphQLSchema):
        bindable = InterfaceType(self.name, self.resolve_type)
        for field, resolver in self.resolvers.items():
            bindable.set_field(field, resolver)
        for alias, target in self.aliases.items():
            bindable.set_alias(alias, target)

        bindable.bind_to_schema(schema)

        graphql_type = cast(GraphQLObjectType, schema.get_type(self.name))
        for field_name, field_out_names in self.out_names.items():
            graphql_field = cast(GraphQLField, graphql_type.fields[field_name])
            for arg_name, out_name in field_out_names.items():
                graphql_field.args[arg_name].out_name = out_name
