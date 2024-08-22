from typing import Any, Dict, List, Optional, Tuple, cast

from ariadne.types import Resolver
from graphql import (
    FieldDefinitionNode,
    InterfaceTypeDefinitionNode,
    NameNode,
    NamedTypeNode,
)

from ..base_object_type import (
    GraphQLFieldData,
    GraphQLBaseObject,
    GraphQLObjectData,
    validate_object_type_with_schema,
    validate_object_type_without_schema,
)
from ..types import GraphQLClassType

from ..utils import parse_definition
from ..base import GraphQLMetadata
from ..description import get_description_node
from ..object_type import GraphQLObject
from .models import GraphQLInterfaceModel


class GraphQLInterface(GraphQLBaseObject):
    __valid_type__ = InterfaceTypeDefinitionNode
    __graphql_type__ = GraphQLClassType.INTERFACE
    __abstract__ = True
    __description__: Optional[str] = None

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        if cls.__dict__.get("__abstract__"):
            return

        cls.__abstract__ = False

        if cls.__dict__.get("__schema__"):
            valid_type = getattr(cls, "__valid_type__", InterfaceTypeDefinitionNode)
            cls.__kwargs__ = validate_object_type_with_schema(cls, valid_type)
        else:
            cls.__kwargs__ = validate_object_type_without_schema(cls)

    @classmethod
    def __get_graphql_model_with_schema__(cls) -> "GraphQLInterfaceModel":
        definition = cast(
            InterfaceTypeDefinitionNode,
            parse_definition(InterfaceTypeDefinitionNode, cls.__schema__),
        )

        resolvers: Dict[str, Resolver] = {}
        fields: Tuple[FieldDefinitionNode, ...] = tuple()
        fields, resolvers = cls._create_fields_and_resolvers_with_schema(
            definition.fields
        )

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
            out_names={},
        )

    @classmethod
    def __get_graphql_model_without_schema__(
        cls, metadata: GraphQLMetadata, name: str
    ) -> "GraphQLInterfaceModel":
        type_data = cls.get_graphql_object_data(metadata)
        type_aliases = getattr(cls, "__aliases__", None) or {}

        fields_ast: List[FieldDefinitionNode] = []
        resolvers: Dict[str, Resolver] = {}
        aliases: Dict[str, str] = {}
        out_names: Dict[str, Dict[str, str]] = {}

        fields_ast, resolvers, aliases, out_names = cls._process_graphql_fields(
            metadata, type_data, type_aliases
        )

        interfaces_ast: List[NamedTypeNode] = []
        for interface_name in type_data.interfaces:
            interfaces_ast.append(NamedTypeNode(name=NameNode(value=interface_name)))

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

    @staticmethod
    def resolve_type(obj: Any, *_) -> str:
        if isinstance(obj, GraphQLObject):
            return obj.__get_graphql_name__()

        raise ValueError(
            f"Cannot resolve GraphQL type {obj} for object of type '{type(obj).__name__}'."
        )

    @classmethod
    def _collect_inherited_objects(cls):
        return [
            inherited_obj
            for inherited_obj in cls.__mro__[1:]
            if getattr(inherited_obj, "__graphql_type__", None)
            == GraphQLClassType.INTERFACE
            and not getattr(inherited_obj, "__abstract__", True)
        ]

    @classmethod
    def create_graphql_object_data_without_schema(cls) -> GraphQLObjectData:
        fields_data = GraphQLFieldData()
        inherited_objects = list(reversed(cls._collect_inherited_objects()))

        for inherited_obj in inherited_objects:
            fields_data.type_hints.update(inherited_obj.__annotations__)
            fields_data.aliases.update(getattr(inherited_obj, "__aliases__", {}))

        cls._process_type_hints_and_aliases(fields_data)
        for inherited_obj in inherited_objects:
            cls._process_class_attributes(inherited_obj, fields_data)
        cls._process_class_attributes(cls, fields_data)

        return GraphQLObjectData(
            fields=cls._build_fields(fields_data=fields_data),
            interfaces=[],
        )
