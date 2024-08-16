from typing import Any, Dict, List, cast

from ariadne.types import Resolver
from graphql import (
    FieldDefinitionNode,
    InputValueDefinitionNode,
    InterfaceTypeDefinitionNode,
    NameNode,
    NamedTypeNode,
    StringValueNode,
)

from ...utils import parse_definition
from ..base import GraphQLMetadata
from ..description import get_description_node
from ..graphql_object import GraphQLObject, GraphQLObjectResolver
from ..graphql_object.object_type import get_graphql_object_data
from ..graphql_object.utils import (
    get_field_args_from_resolver,
    get_field_args_out_names,
    get_field_node_from_obj_field,
    update_field_args_options,
)
from ..value import get_value_node
from .interface_model import GraphQLInterfaceModel


class GraphQLInterface(GraphQLObject):
    __abstract__: bool = True
    __valid_type__ = InterfaceTypeDefinitionNode

    @classmethod
    def __get_graphql_model_with_schema__(cls) -> "GraphQLInterfaceModel":
        definition = cast(
            InterfaceTypeDefinitionNode,
            parse_definition(InterfaceTypeDefinitionNode, cls.__schema__),
        )

        descriptions: Dict[str, StringValueNode] = {}
        args_descriptions: Dict[str, Dict[str, StringValueNode]] = {}
        args_defaults: Dict[str, Dict[str, Any]] = {}
        resolvers: Dict[str, Resolver] = {}
        out_names: Dict[str, Dict[str, str]] = {}

        for attr_name in dir(cls):
            cls_attr = getattr(cls, attr_name)
            if isinstance(cls_attr, GraphQLObjectResolver):
                resolvers[cls_attr.field] = cls_attr.resolver
                description_node = get_description_node(cls_attr.description)
                if description_node:
                    descriptions[cls_attr.field] = description_node

                field_args = get_field_args_from_resolver(cls_attr.resolver)
                if field_args:
                    args_descriptions[cls_attr.field] = {}
                    args_defaults[cls_attr.field] = {}

                    final_args = update_field_args_options(field_args, cls_attr.args)

                    for arg_name, arg_options in final_args.items():
                        arg_description = get_description_node(arg_options.description)
                        if arg_description:
                            args_descriptions[cls_attr.field][
                                arg_name
                            ] = arg_description

                        arg_default = arg_options.default_value
                        if arg_default is not None:
                            args_defaults[cls_attr.field][arg_name] = get_value_node(
                                arg_default
                            )

        fields: List[FieldDefinitionNode] = []
        for field in definition.fields:
            field_args_descriptions = args_descriptions.get(field.name.value, {})
            field_args_defaults = args_defaults.get(field.name.value, {})

            args: List[InputValueDefinitionNode] = []
            for arg in field.arguments:
                arg_name = arg.name.value
                args.append(
                    InputValueDefinitionNode(
                        description=(
                            arg.description or field_args_descriptions.get(arg_name)
                        ),
                        name=arg.name,
                        directives=arg.directives,
                        type=arg.type,
                        default_value=(
                            arg.default_value or field_args_defaults.get(arg_name)
                        ),
                    )
                )

            fields.append(
                FieldDefinitionNode(
                    name=field.name,
                    description=(
                        field.description or descriptions.get(field.name.value)
                    ),
                    directives=field.directives,
                    arguments=tuple(args),
                    type=field.type,
                )
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
            out_names=out_names,
        )

    @classmethod
    def __get_graphql_model_without_schema__(
        cls, metadata: GraphQLMetadata, name: str
    ) -> "GraphQLInterfaceModel":
        type_data = get_graphql_object_data(metadata, cls)
        type_aliases = getattr(cls, "__aliases__", None) or {}

        fields_ast: List[FieldDefinitionNode] = []
        resolvers: Dict[str, Resolver] = {}
        aliases: Dict[str, str] = {}
        out_names: Dict[str, Dict[str, str]] = {}

        for attr_name, field in type_data.fields.items():
            fields_ast.append(get_field_node_from_obj_field(cls, metadata, field))

            if attr_name in type_aliases and field.name:
                aliases[field.name] = type_aliases[attr_name]
            elif field.name and attr_name != field.name and not field.resolver:
                aliases[field.name] = attr_name

            if field.resolver and field.name:
                resolvers[field.name] = field.resolver

            if field.args and field.name:
                out_names[field.name] = get_field_args_out_names(field.args)

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
        if isinstance(obj, GraphQLInterface):
            return obj.__get_graphql_name__()

        raise ValueError(
            f"Cannot resolve GraphQL type {obj} for object of type '{type(obj).__name__}'."
        )
