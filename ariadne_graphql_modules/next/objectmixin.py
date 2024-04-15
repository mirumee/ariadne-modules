from typing import Dict, List, Optional
from graphql import (
    FieldDefinitionNode,
    InputValueDefinitionNode,
    NameNode,
    NamedTypeNode,
)

from .base import GraphQLMetadata
from .description import get_description_node
from .field import GraphQLObjectField, GraphQLObjectFieldArg
from .metadata import (
    GraphQLObjectData,
    get_graphql_object_data,
)
from .resolver import (
    GraphQLObjectResolver,
    get_field_args_from_resolver,
    update_field_args_options,
)
from .typing import get_type_node
from .value import get_value_node


class GraphQLModelHelpersMixin:
    @classmethod
    def gather_fields_without_schema(cls, metadata: GraphQLMetadata):
        type_data = get_graphql_object_data(metadata, cls)
        fields_ast = [
            cls.create_field_node(metadata, field)
            for field in type_data.fields.values()
        ]
        return fields_ast

    @staticmethod
    def collect_resolvers_without_schema(type_data: GraphQLObjectData):
        return {
            field.name: field.resolver
            for field in type_data.fields.values()
            if field.resolver
        }

    @staticmethod
    def collect_aliases(type_data: GraphQLObjectData):
        aliases = {}
        for field in type_data.fields.values():
            attr_name = field.name  # Placeholder for actual attribute name logic
            if attr_name != field.name:
                aliases[field.name] = attr_name
        return aliases

    @staticmethod
    def collect_out_names(type_data: GraphQLObjectData):
        out_names = {}
        for field in type_data.fields.values():
            if field.args:
                out_names[field.name] = {
                    arg.name: arg.out_name for arg in field.args.values()
                }
        return out_names

    @classmethod
    def create_field_node(cls, metadata: GraphQLMetadata, field: GraphQLObjectField):
        args_nodes = cls.get_field_args_nodes_from_obj_field_args(metadata, field.args)
        return FieldDefinitionNode(
            description=get_description_node(field.description),
            name=NameNode(value=field.name),
            type=get_type_node(metadata, field.type),
            arguments=tuple(args_nodes) if args_nodes else None,
        )

    @staticmethod
    def get_field_args_nodes_from_obj_field_args(
        metadata: GraphQLMetadata,
        field_args: Optional[Dict[str, GraphQLObjectFieldArg]],
    ):
        if not field_args:
            return []

        return [
            InputValueDefinitionNode(
                description=get_description_node(arg.description),
                name=NameNode(value=arg.name),
                type=get_type_node(metadata, arg.type),
                default_value=get_value_node(arg.default_value)
                if arg.default_value is not None
                else None,
            )
            for arg in field_args.values()
        ]

    @classmethod
    def gather_interfaces_without_schema(cls, type_data: GraphQLObjectData):
        interfaces_ast: List[NamedTypeNode] = []
        for interface_name in type_data.interfaces:
            interfaces_ast.append(NamedTypeNode(name=NameNode(value=interface_name)))
        return interfaces_ast

    @classmethod
    def gather_interfaces_with_schema(cls):
        return [interface for interface in getattr(cls, "__implements__", [])]

    @classmethod
    def gather_fields_with_schema(cls, definition):
        descriptions, args_descriptions, args_defaults = (
            cls.collect_descriptions_and_defaults()
        )

        fields = [
            cls.create_field_definition_node(
                field, descriptions, args_descriptions, args_defaults
            )
            for field in definition.fields
        ]
        return fields

    @classmethod
    def collect_resolvers_with_schema(cls):
        resolvers = {}
        for attr_name in dir(cls):
            cls_attr = getattr(cls, attr_name)
            if isinstance(cls_attr, GraphQLObjectResolver):
                resolvers[cls_attr.field] = cls_attr.resolver
        return resolvers

    @classmethod
    def collect_descriptions_and_defaults(cls):
        descriptions = {}
        args_descriptions = {}
        args_defaults = {}
        for attr_name in dir(cls):
            cls_attr = getattr(cls, attr_name)
            if isinstance(cls_attr, GraphQLObjectResolver):
                if cls_attr.description:
                    descriptions[cls_attr.field] = get_description_node(
                        cls_attr.description
                    )

                field_args = get_field_args_from_resolver(cls_attr.resolver)
                if field_args:
                    args_descriptions[cls_attr.field], args_defaults[cls_attr.field] = (
                        cls.process_field_args(field_args, cls_attr.args)
                    )

        return descriptions, args_descriptions, args_defaults

    @classmethod
    def process_field_args(cls, field_args, resolver_args):
        descriptions = {}
        defaults = {}
        final_args = update_field_args_options(field_args, resolver_args)

        for arg_name, arg_options in final_args.items():
            descriptions[arg_name] = (
                get_description_node(arg_options.description)
                if arg_options.description
                else None
            )
            defaults[arg_name] = (
                get_value_node(arg_options.default_value)
                if arg_options.default_value is not None
                else None
            )

        return descriptions, defaults

    @classmethod
    def create_field_definition_node(
        cls, field, descriptions, args_descriptions, args_defaults
    ):
        field_name = field.name.value
        field_args_descriptions = args_descriptions.get(field_name, {})
        field_args_defaults = args_defaults.get(field_name, {})

        args = [
            InputValueDefinitionNode(
                description=(
                    arg.description or field_args_descriptions.get(arg.name.value)
                ),
                name=arg.name,
                directives=arg.directives,
                type=arg.type,
                default_value=(
                    arg.default_value or field_args_defaults.get(arg.name.value)
                ),
            )
            for arg in field.arguments
        ]

        return FieldDefinitionNode(
            name=field.name,
            description=(field.description or descriptions.get(field_name)),
            directives=field.directives,
            arguments=tuple(args),
            type=field.type,
        )
