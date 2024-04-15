from dataclasses import dataclass
from typing import Any, Dict, List

from .base import GraphQLMetadata
from .convert_name import convert_python_name_to_graphql
from .field import GraphQLObjectField, GraphQLObjectFieldArg
from .resolver import (
    GraphQLObjectResolver,
    get_field_args_from_resolver,
    update_field_args_options,
)
from ariadne.types import Resolver


@dataclass(frozen=True)
class GraphQLObjectData:
    fields: Dict[str, GraphQLObjectField]
    interfaces: List[str]


def get_graphql_object_data(metadata: GraphQLMetadata, cls):
    try:
        return metadata.get_data(cls)
    except KeyError:
        if getattr(cls, "__schema__", None):
            raise NotImplementedError(
                "'get_graphql_object_data' is not supported for objects with '__schema__'."
            )
        else:
            return create_graphql_object_data_without_schema(cls)


def create_graphql_object_data_without_schema(
    cls,
) -> GraphQLObjectData:
    fields_types: Dict[str, str] = {}
    fields_names: Dict[str, str] = {}
    fields_descriptions: Dict[str, str] = {}
    fields_args: Dict[str, Dict[str, GraphQLObjectFieldArg]] = {}
    fields_resolvers: Dict[str, Resolver] = {}
    fields_defaults: Dict[str, Any] = {}
    fields_order: List[str] = []

    type_hints = cls.__annotations__

    aliases: Dict[str, str] = getattr(cls, "__aliases__", None) or {}
    aliases_targets: List[str] = list(aliases.values())

    interfaces: List[str] = [
        interface.__name__ for interface in getattr(cls, "__implements__", [])
    ]

    for attr_name, attr_type in type_hints.items():
        if attr_name.startswith("__"):
            continue

        if attr_name in aliases_targets:
            # Alias target is not included in schema
            # unless its explicit field
            cls_attr = getattr(cls, attr_name, None)
            if not isinstance(cls_attr, GraphQLObjectField):
                continue

        fields_order.append(attr_name)

        fields_names[attr_name] = convert_python_name_to_graphql(attr_name)
        fields_types[attr_name] = attr_type

    for attr_name in dir(cls):
        if attr_name.startswith("__"):
            continue

        cls_attr = getattr(cls, attr_name)
        if isinstance(cls_attr, GraphQLObjectField):
            if attr_name not in fields_order:
                fields_order.append(attr_name)

            fields_names[attr_name] = cls_attr.name or convert_python_name_to_graphql(
                attr_name
            )

            if cls_attr.type and attr_name not in fields_types:
                fields_types[attr_name] = cls_attr.type
            if cls_attr.description:
                fields_descriptions[attr_name] = cls_attr.description
            if cls_attr.resolver:
                fields_resolvers[attr_name] = cls_attr.resolver
                field_args = get_field_args_from_resolver(cls_attr.resolver)
                if field_args:
                    fields_args[attr_name] = update_field_args_options(
                        field_args, cls_attr.args
                    )
            if cls_attr.default_value:
                fields_defaults[attr_name] = cls_attr.default_value

        elif isinstance(cls_attr, GraphQLObjectResolver):
            if cls_attr.type and cls_attr.field not in fields_types:
                fields_types[cls_attr.field] = cls_attr.type
            if cls_attr.description:
                fields_descriptions[cls_attr.field] = cls_attr.description
            if cls_attr.resolver:
                fields_resolvers[cls_attr.field] = cls_attr.resolver
                field_args = get_field_args_from_resolver(cls_attr.resolver)
                if field_args:
                    fields_args[cls_attr.field] = update_field_args_options(
                        field_args, cls_attr.args
                    )

        elif attr_name not in aliases_targets and not callable(cls_attr):
            fields_defaults[attr_name] = cls_attr

    fields: Dict[str, "GraphQLObjectField"] = {}
    for field_name in fields_order:
        fields[field_name] = GraphQLObjectField(
            name=fields_names[field_name],
            description=fields_descriptions.get(field_name),
            type=fields_types[field_name],
            args=fields_args.get(field_name),
            resolver=fields_resolvers.get(field_name),
            default_value=fields_defaults.get(field_name),
        )

    return GraphQLObjectData(fields=fields, interfaces=interfaces)
