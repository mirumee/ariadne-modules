from dataclasses import dataclass, replace
from inspect import signature
from typing import Any, Dict, Optional

from ariadne.types import Resolver

from .convert_name import convert_python_name_to_graphql
from .field import GraphQLObjectFieldArg


@dataclass(frozen=True)
class GraphQLObjectResolver:
    resolver: Resolver
    field: str
    description: Optional[str] = None
    args: Optional[Dict[str, dict]] = None
    type: Optional[Any] = None


def get_field_args_from_resolver(
    resolver: Resolver,
) -> Dict[str, GraphQLObjectFieldArg]:
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
            type=type_hints.get(param_name),
            default_value=param_default,
        )

    return field_args


def update_field_args_options(
    field_args: Dict[str, GraphQLObjectFieldArg],
    args_options: Optional[Dict[str, dict]],
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
        if arg_options.get("name"):
            args_update["name"] = arg_options["name"]
        if arg_options.get("description"):
            args_update["description"] = arg_options["description"]
        if arg_options.get("default_value") is not None:
            args_update["default_value"] = arg_options["default_value"]
        if arg_options.get("type"):
            args_update["type"] = arg_options["type"]

        if args_update:
            updated_args[arg_name] = replace(field_args[arg_name], **args_update)
        else:
            updated_args[arg_name] = field_args[arg_name]

    return updated_args
