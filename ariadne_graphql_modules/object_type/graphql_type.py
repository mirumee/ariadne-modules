from typing import (
    Dict,
    Optional,
    Tuple,
    cast,
)

from ariadne.types import Resolver
from graphql import (
    FieldDefinitionNode,
    NameNode,
    NamedTypeNode,
    ObjectTypeDefinitionNode,
)

from ariadne_graphql_modules.base_object_type.graphql_field import GraphQLClassData
from ariadne_graphql_modules.base_object_type.validators import (
    validate_object_type_with_schema,
    validate_object_type_without_schema,
)

from ..types import GraphQLClassType

from ..base_object_type import (
    GraphQLFieldData,
    GraphQLBaseObject,
    GraphQLObjectData,
)
from .models import GraphQLObjectModel


from ..utils import parse_definition
from ..base import GraphQLMetadata, GraphQLModel
from ..description import get_description_node


class GraphQLObject(GraphQLBaseObject):
    __graphql_type__ = GraphQLClassType.OBJECT
    __abstract__ = True
    __description__: Optional[str] = None
    __schema__: Optional[str] = None
    __graphql_name__: Optional[str] = None

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        if cls.__dict__.get("__abstract__"):
            return

        cls.__abstract__ = False

        if cls.__dict__.get("__schema__"):
            cls.__kwargs__ = validate_object_type_with_schema(
                cls, ObjectTypeDefinitionNode
            )
        else:
            cls.__kwargs__ = validate_object_type_without_schema(cls)

    @classmethod
    def __get_graphql_model_with_schema__(cls) -> "GraphQLModel":
        definition = cast(
            ObjectTypeDefinitionNode,
            parse_definition(ObjectTypeDefinitionNode, cls.__schema__),
        )

        resolvers: Dict[str, Resolver] = {}
        fields: Tuple[FieldDefinitionNode, ...] = tuple()
        fields, resolvers = cls._create_fields_and_resolvers_with_schema(
            definition.fields
        )

        return GraphQLObjectModel(
            name=definition.name.value,
            ast_type=ObjectTypeDefinitionNode,
            ast=ObjectTypeDefinitionNode(
                name=NameNode(value=definition.name.value),
                fields=tuple(fields),
                interfaces=definition.interfaces,
            ),
            resolvers=resolvers,
            aliases=getattr(cls, "__aliases__", {}),
            out_names={},
        )

    @classmethod
    def __get_graphql_model_without_schema__(
        cls, metadata: GraphQLMetadata, name: str
    ) -> "GraphQLModel":
        type_data = cls.get_graphql_object_data(metadata)
        type_aliases = getattr(cls, "__aliases__", {})

        object_model_data = GraphQLClassData()
        cls._process_graphql_fields(
            metadata, type_data, type_aliases, object_model_data
        )

        return GraphQLObjectModel(
            name=name,
            ast_type=ObjectTypeDefinitionNode,
            ast=ObjectTypeDefinitionNode(
                name=NameNode(value=name),
                description=get_description_node(
                    getattr(cls, "__description__", None),
                ),
                fields=tuple(object_model_data.fields_ast.values()),
                interfaces=tuple(type_data.interfaces),
            ),
            resolvers=object_model_data.resolvers,
            aliases=object_model_data.aliases,
            out_names=object_model_data.out_names,
        )

    @classmethod
    def _collect_inherited_objects(cls):
        return [
            inherited_obj
            for inherited_obj in cls.__mro__[1:]
            if getattr(inherited_obj, "__graphql_type__", None)
            in (GraphQLClassType.INTERFACE, GraphQLClassType.OBJECT)
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
            interfaces=[
                NamedTypeNode(name=NameNode(value=interface.__name__))
                for interface in inherited_objects
                if getattr(interface, "__graphql_type__", None)
                == GraphQLClassType.INTERFACE
            ],
        )
