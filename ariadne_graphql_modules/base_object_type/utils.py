from dataclasses import replace
from inspect import signature
from typing import TYPE_CHECKING, Dict, Optional, Tuple, Type

from ariadne.types import Resolver, Subscriber
from graphql import FieldDefinitionNode, InputValueDefinitionNode, NameNode

from ..base import GraphQLMetadata
from ..convert_name import convert_python_name_to_graphql
from ..description import get_description_node
from ..typing import get_type_node
from ..value import get_value_node
from .graphql_field import GraphQLObjectField, GraphQLObjectFieldArg

if TYPE_CHECKING:
    from .graphql_type import GraphQLBaseObject


def get_field_node_from_obj_field(
    parent_type: Type["GraphQLBaseObject"],
    metadata: GraphQLMetadata,
    field: GraphQLObjectField,
) -> FieldDefinitionNode:
    return FieldDefinitionNode(
        description=get_description_node(field.description),
        name=NameNode(value=field.name),
        type=get_type_node(metadata, field.field_type, parent_type),
        arguments=get_field_args_nodes_from_obj_field_args(metadata, field.args),
    )


def get_field_args_from_resolver(
    resolver: Resolver,
) -> Dict[str, GraphQLObjectFieldArg]:
    if isinstance(resolver, staticmethod):
        resolver = resolver.__func__
    resolver_signature = signature(resolver)
    type_hints = resolver.__annotations__
    type_hints.pop("return", None)

    field_args: Dict[str, GraphQLObjectFieldArg] = {}
    field_args_start = 0

    # Fist pass: (arg, *_, something, something) or (arg, *, something, something):
    for i, param in enumerate(resolver_signature.parameters.values()):
        param_repr = str(param)
        if param_repr.startswith("*") and not param_repr.startswith("**"):
            field_args_start = i + 1
            break
    else:
        if len(resolver_signature.parameters) < 2:
            raise TypeError(
                f"Resolver function '{resolver_signature}' should accept at least "
                "'obj' and 'info' positional arguments."
            )

        field_args_start = 2

    args_parameters = tuple(resolver_signature.parameters.items())[field_args_start:]
    if not args_parameters:
        return field_args

    for param_name, param in args_parameters:
        if param.default != param.empty:
            param_default = param.default
        else:
            param_default = None

        field_args[param_name] = GraphQLObjectFieldArg(
            name=convert_python_name_to_graphql(param_name),
            out_name=param_name,
            field_type=type_hints.get(param_name),
            default_value=param_default,
        )

    return field_args


def get_field_args_from_subscriber(
    subscriber: Subscriber,
) -> Dict[str, GraphQLObjectFieldArg]:
    subscriber_signature = signature(subscriber)
    type_hints = subscriber.__annotations__
    type_hints.pop("return", None)

    field_args: Dict[str, GraphQLObjectFieldArg] = {}
    field_args_start = 0

    # Fist pass: (arg, *_, something, something) or (arg, *, something, something):
    for i, param in enumerate(subscriber_signature.parameters.values()):
        param_repr = str(param)
        if param_repr.startswith("*") and not param_repr.startswith("**"):
            field_args_start = i + 1
            break
    else:
        if len(subscriber_signature.parameters) < 2:
            raise TypeError(
                f"Subscriber function '{subscriber_signature}' should accept at least "
                "'obj' and 'info' positional arguments."
            )

        field_args_start = 2

    args_parameters = tuple(subscriber_signature.parameters.items())[field_args_start:]
    if not args_parameters:
        return field_args

    for param_name, param in args_parameters:
        if param.default != param.empty:
            param_default = param.default
        else:
            param_default = None

        field_args[param_name] = GraphQLObjectFieldArg(
            name=convert_python_name_to_graphql(param_name),
            out_name=param_name,
            field_type=type_hints.get(param_name),
            default_value=param_default,
        )

    return field_args


def get_field_args_out_names(
    field_args: Dict[str, GraphQLObjectFieldArg],
) -> Dict[str, str]:
    out_names: Dict[str, str] = {}
    for field_arg in field_args.values():
        if field_arg.name and field_arg.out_name:
            out_names[field_arg.name] = field_arg.out_name
    return out_names


def get_field_arg_node_from_obj_field_arg(
    metadata: GraphQLMetadata,
    field_arg: GraphQLObjectFieldArg,
) -> InputValueDefinitionNode:
    if field_arg.default_value is not None:
        default_value = get_value_node(field_arg.default_value)
    else:
        default_value = None

    return InputValueDefinitionNode(
        description=get_description_node(field_arg.description),
        name=NameNode(value=field_arg.name),
        type=get_type_node(metadata, field_arg.field_type),
        default_value=default_value,
    )


def get_field_args_nodes_from_obj_field_args(
    metadata: GraphQLMetadata,
    field_args: Optional[Dict[str, GraphQLObjectFieldArg]],
) -> Optional[Tuple[InputValueDefinitionNode, ...]]:
    if not field_args:
        return None

    return tuple(
        get_field_arg_node_from_obj_field_arg(metadata, field_arg)
        for field_arg in field_args.values()
    )


def update_field_args_options(
    field_args: Dict[str, GraphQLObjectFieldArg],
    args_options: Optional[Dict[str, GraphQLObjectFieldArg]],
) -> Dict[str, GraphQLObjectFieldArg]:
    if not args_options:
        return field_args

    updated_args: Dict[str, GraphQLObjectFieldArg] = {}
    for arg_name in field_args:
        arg_options = args_options.get(arg_name)
        if not arg_options:
            updated_args[arg_name] = field_args[arg_name]
            continue
        args_update = {}
        if arg_options.name:
            args_update["name"] = arg_options.name
        if arg_options.description:
            args_update["description"] = arg_options.description
        if arg_options.default_value is not None:
            args_update["default_value"] = arg_options.default_value
        if arg_options.field_type:
            args_update["field_type"] = arg_options.field_type

        if args_update:
            updated_args[arg_name] = replace(field_args[arg_name], **args_update)
        else:
            updated_args[arg_name] = field_args[arg_name]

    return updated_args
