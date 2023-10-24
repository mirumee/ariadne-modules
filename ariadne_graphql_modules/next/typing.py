from enum import Enum
from importlib import import_module
from inspect import isclass
from types import UnionType
from typing import (
    Annotated,
    Any,
    ForwardRef,
    Optional,
    Type,
    Union,
    get_args,
    get_origin,
)

from graphql import (
    ListTypeNode,
    NameNode,
    NamedTypeNode,
    NonNullTypeNode,
    TypeNode,
)

from .base import GraphQLMetadata, GraphQLType
from .deferredtype import DeferredTypeData
from .idtype import GraphQLID


def get_type_node(
    metadata: GraphQLMetadata,
    type_hint: Any,
    parent_type: Optional[GraphQLType] = None,
) -> TypeNode:
    if is_nullable(type_hint):
        nullable = True
        type_hint = unwrap_type(type_hint)
    else:
        nullable = False

    type_node = None
    if is_list(type_hint):
        list_item_type_hint = unwrap_type(type_hint)
        type_node = ListTypeNode(
            type=get_type_node(metadata, list_item_type_hint, parent_type=parent_type)
        )
    elif type_hint == str:
        type_node = NamedTypeNode(name=NameNode(value="String"))
    elif type_hint == int:
        type_node = NamedTypeNode(name=NameNode(value="Int"))
    elif type_hint == float:
        type_node = NamedTypeNode(name=NameNode(value="Float"))
    elif type_hint == bool:
        type_node = NamedTypeNode(name=NameNode(value="Boolean"))
    elif get_origin(type_hint) is Annotated:
        forward_ref, type_meta = get_args(type_hint)
        if not type_meta or not isinstance(type_meta, DeferredTypeData):
            raise ValueError(
                f"Can't create a GraphQL return type for '{type_hint}'. "
                "Second argument of 'Annotated' is expected to be a return "
                "value from the 'deferred()' utility."
            )

        deferred_type = get_deferred_type(type_hint, forward_ref, type_meta)
        type_node = NamedTypeNode(
            name=NameNode(value=metadata.get_graphql_name(deferred_type)),
        )
    elif isinstance(type_hint, ForwardRef):
        type_name = type_hint.__forward_arg__
        if not parent_type or parent_type.__name__ != type_name:
            ...

        type_node = NamedTypeNode(
            name=NameNode(value=metadata.get_graphql_name(parent_type)),
        )
    elif isclass(type_hint):
        if issubclass(type_hint, GraphQLID):
            type_node = NamedTypeNode(name=NameNode(value="ID"))
        elif issubclass(type_hint, (GraphQLType, Enum)):
            type_node = NamedTypeNode(
                name=NameNode(value=metadata.get_graphql_name(type_hint)),
            )

    if not type_node:
        raise ValueError(f"Can't create a GraphQL return type for '{type_hint}'.")

    if nullable:
        return type_node

    return NonNullTypeNode(type=type_node)


def is_list(type_hint: Any) -> bool:
    return get_origin(type_hint) == list


def is_nullable(type_hint: Any) -> bool:
    origin = get_origin(type_hint)
    if origin in (UnionType, Union):
        return type(None) in get_args(type_hint)

    return False


def unwrap_type(type_hint: Any) -> Any:
    args = list(get_args(type_hint))
    if type(None) in args:
        args.remove(type(None))
    if len(args) != 1:
        raise ValueError(
            f"Type {type_hint} is a wrapper type for multiple other "
            "types and can't be unwrapped."
        )
    return args[0]


def get_deferred_type(
    type_hint: Any, forward_ref: ForwardRef, deferred_type: DeferredTypeData
) -> Optional[Union[GraphQLType, Enum]]:
    type_name = forward_ref.__forward_arg__
    module = import_module(deferred_type.path)
    graphql_type = getattr(module, type_name)

    if not isclass(graphql_type) or not issubclass(graphql_type, (GraphQLType, Enum)):
        raise ValueError(f"Can't create a GraphQL return type for '{type_hint}'.")

    return graphql_type


def get_graphql_type(annotation: Any) -> Optional[Union[Type[GraphQLType], Type[Enum]]]:
    """Utility that extracts GraphQL type from type annotation"""
    if is_nullable(annotation) or is_list(annotation):
        return get_graphql_type(unwrap_type(annotation))

    if not isclass(annotation):
        return None

    if issubclass(annotation, (GraphQLType, Enum)):
        return annotation

    return None
