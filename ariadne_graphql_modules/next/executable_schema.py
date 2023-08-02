from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Type, Union

from ariadne import SchemaBindable, SchemaDirectiveVisitor, SchemaNameConverter
from graphql import (
    DocumentNode,
    GraphQLSchema,
    assert_valid_schema,
    build_ast_schema,
)

from .base import GraphQLModel, GraphQLType

SchemaType = Union[
    str,
    Enum,
    SchemaBindable,
    Type[GraphQLType],
]


def make_executable_schema(
    *types: Union[SchemaType, List[SchemaType]],
    directives: Optional[Dict[str, Type[SchemaDirectiveVisitor]]] = None,
    convert_names_case: Union[bool, SchemaNameConverter] = False,
) -> GraphQLSchema:
    type_defs: List[str] = find_type_defs(types)
    types_list: List[SchemaType] = flatten_types(types)

    assert_types_unique(types_list)
    assert_types_not_abstract(types_list)

    # TODO:
    # Convert unique types list to models/bindables list
    # Deal with deferred types

    schema_models: List[GraphQLModel] = [
        type_def.__get_graphql_model__() for type_def in types_list
    ]

    document_node = DocumentNode(
        definitions=tuple(schema_model.ast for schema_model in schema_models),
    )
    
    schema = build_ast_schema(document_node)
    assert_valid_schema(schema)

    for schema_model in schema_models:
        schema_model.bind_to_schema(schema)

    return schema


def find_type_defs(types: Sequence[SchemaType]) -> List[str]:
    type_defs: List[str] = []

    for type_def in types:
        if isinstance(type_def, str):
            type_defs.append(type_def)
        elif isinstance(type_def, list):
            type_defs += find_type_defs(type_def)

    return type_defs


def flatten_types(types: Sequence[Union[SchemaType, List[SchemaType]]]) -> List[Union[Enum, SchemaBindable, GraphQLModel]]:
    flat_schema_types_list: List[SchemaType] = flatten_schema_types(types)

    types_list: List[Union[Enum, SchemaBindable, GraphQLModel]] = []
    for type_def in flat_schema_types_list:
        if issubclass(type_def, GraphQLType):
            type_name = type_def.__name__

            if getattr(type_def, "__abstract__", None):
                raise ValueError(
                    f"Type '{type_name}' is an abstract type and can't be used "
                    "for schema creation."
                )

            types_list.append(type_def)

        if isinstance(type_def, list):
            types_list += find_type_defs(type_def)

    return types_list


def flatten_schema_types(
    types: Sequence[Union[SchemaType, List[SchemaType]]],
    dedupe: bool = True,
) -> List[SchemaType]:
    flat_list: List[SchemaType] = []

    for type_def in types:
        if isinstance(type_def, list):
            flat_list += flatten_schema_types(type_def, dedupe=False)
        elif issubclass(type_def, GraphQLType):
            flat_list += type_def.__get_graphql_types__()
        elif get_graphql_type_name(type_def):
            flat_list.append(type_def)

    if not dedupe:
        return flat_list

    unique_list: List[SchemaType] = []
    for type_def in flat_list:
        if type_def not in unique_list:
            unique_list.append(type_def)

    return unique_list


def get_graphql_type_name(type_def: SchemaType) -> Optional[str]:
    if issubclass(type_def, Enum):
        return type_def.__name__

    if issubclass(type_def, GraphQLModel):
        return type_def.__get_graphql_name__()

    return None


def assert_types_unique(type_defs: List[SchemaType]):
    types_names: Dict[str, Any] = {}
    for type_def in type_defs:
        type_name = get_graphql_type_name(type_def)
        if type_name in types_names:
            raise ValueError(
                f"Types '{type_def.__name__}' and '{types_names[type_name]}' both define "
                f"GraphQL type with name '{type_name}'."
            )
        
        types_names[type_name] = type_def


def assert_types_not_abstract(type_defs: List[SchemaType]):
    for type_def in type_defs:
        if issubclass(type_def, GraphQLType) and getattr(type_def, "__abstract__", None):
            raise ValueError(
                f"Type '{type_def.__name__}' is an abstract type and can't be used "
                "for schema creation."
            )