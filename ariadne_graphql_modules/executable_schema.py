from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Type, Union

from ariadne import (
    SchemaBindable,
    SchemaDirectiveVisitor,
    SchemaNameConverter,
    convert_schema_names,
    repair_schema_default_enum_values,
    validate_schema_default_enum_values,
)
from graphql import (
    DocumentNode,
    GraphQLSchema,
    assert_valid_schema,
    build_ast_schema,
    parse,
    concat_ast,
)

from .base import GraphQLMetadata, GraphQLModel, GraphQLType
from .roots import ROOTS_NAMES, merge_root_nodes
from .sort import sort_schema_document

SchemaType = Union[str, Enum, SchemaBindable, Type[GraphQLType], Type[Enum]]


def make_executable_schema(
    *types: SchemaType,
    directives: Optional[Dict[str, Type[SchemaDirectiveVisitor]]] = None,
    convert_names_case: Union[bool, SchemaNameConverter] = False,
    merge_roots: bool = True,
) -> GraphQLSchema:
    metadata = GraphQLMetadata()
    type_defs: List[str] = find_type_defs(types)
    types_list: List[SchemaType] = flatten_types(types, metadata)

    assert_types_unique(types_list, merge_roots)
    assert_types_not_abstract(types_list)

    schema_bindables: List[Union[SchemaBindable, GraphQLModel]] = []
    for type_def in types_list:
        if isinstance(type_def, SchemaBindable):
            schema_bindables.append(type_def)
        elif isinstance(type_def, type) and issubclass(type_def, (GraphQLType, Enum)):
            schema_bindables.append(metadata.get_graphql_model(type_def))

    schema_models: List[GraphQLModel] = [
        type_def for type_def in schema_bindables if isinstance(type_def, GraphQLModel)
    ]

    models_document: Optional[DocumentNode] = None
    type_defs_document: Optional[DocumentNode] = None

    if schema_models:
        models_document = DocumentNode(
            definitions=tuple(schema_model.ast for schema_model in schema_models),
        )

    if type_defs:
        type_defs_document = parse("\n".join(type_defs))

    if models_document and type_defs_document:
        document_node = concat_ast((models_document, type_defs_document))
    elif models_document:
        document_node = models_document
    elif type_defs_document:
        document_node = type_defs_document
    else:
        raise ValueError(
            "'make_executable_schema' was called without any GraphQL types."
        )

    if merge_roots:
        document_node = merge_root_nodes(document_node)

    document_node = sort_schema_document(document_node)
    schema = build_ast_schema(document_node)

    if directives:
        SchemaDirectiveVisitor.visit_schema_directives(schema, directives)

    assert_valid_schema(schema)
    validate_schema_default_enum_values(schema)
    repair_schema_default_enum_values(schema)

    for schema_bindable in schema_bindables:
        schema_bindable.bind_to_schema(schema)

    if convert_names_case:
        convert_schema_names(
            schema,
            convert_names_case if callable(convert_names_case) else None,
        )

    return schema


def find_type_defs(types: Sequence[SchemaType]) -> List[str]:
    type_defs: List[str] = []

    for type_def in types:
        if isinstance(type_def, str):
            type_defs.append(type_def)
        elif isinstance(type_def, list):
            type_defs += find_type_defs(type_def)

    return type_defs


def flatten_types(
    types: Sequence[SchemaType],
    metadata: GraphQLMetadata,
) -> List[SchemaType]:
    flat_schema_types_list: List[SchemaType] = flatten_schema_types(
        types, metadata, dedupe=True
    )

    types_list: List[SchemaType] = []
    for type_def in flat_schema_types_list:
        if isinstance(type_def, SchemaBindable):
            types_list.append(type_def)

        elif isinstance(type_def, type) and issubclass(type_def, GraphQLType):
            type_name = type_def.__name__

            if getattr(type_def, "__abstract__", None):
                raise ValueError(
                    f"Type '{type_name}' is an abstract type and can't be used "
                    "for schema creation."
                )

            types_list.append(type_def)

        elif isinstance(type_def, type) and issubclass(type_def, Enum):
            types_list.append(type_def)

        elif isinstance(type_def, list):
            types_list += find_type_defs(type_def)

    return types_list


def flatten_schema_types(
    types: Sequence[Union[SchemaType, List[SchemaType]]],
    metadata: GraphQLMetadata,
    dedupe: bool,
) -> List[SchemaType]:
    flat_list: List[SchemaType] = []
    checked_types: List[Type[GraphQLType]] = []

    for type_def in types:
        if isinstance(type_def, str):
            continue
        if isinstance(type_def, list):
            flat_list += flatten_schema_types(type_def, metadata, dedupe=False)
        elif isinstance(type_def, SchemaBindable):
            flat_list.append(type_def)
        elif isinstance(type_def, type) and issubclass(type_def, Enum):
            flat_list.append(type_def)
        elif isinstance(type_def, type) and issubclass(type_def, GraphQLType):
            add_graphql_type_to_flat_list(flat_list, checked_types, type_def, metadata)
        elif get_graphql_type_name(type_def):
            flat_list.append(type_def)

    if not dedupe:
        return flat_list

    unique_list: List[SchemaType] = []
    for type_def in flat_list:
        if type_def not in unique_list:
            unique_list.append(type_def)

    return unique_list


def add_graphql_type_to_flat_list(
    flat_list: List[SchemaType],
    checked_types: List[Type[GraphQLType]],
    type_def: Type[GraphQLType],
    metadata: GraphQLMetadata,
) -> None:
    if type_def in checked_types:
        return

    checked_types.append(type_def)

    for child_type in type_def.__get_graphql_types__(metadata):
        flat_list.append(child_type)

        if issubclass(child_type, GraphQLType):
            add_graphql_type_to_flat_list(
                flat_list, checked_types, child_type, metadata
            )


def get_graphql_type_name(type_def: SchemaType) -> Optional[str]:
    if isinstance(type_def, SchemaBindable):
        return None

    if isinstance(type_def, type) and issubclass(type_def, Enum):
        return type_def.__name__

    if isinstance(type_def, type) and issubclass(type_def, GraphQLType):
        return type_def.__get_graphql_name__()

    return None


def assert_types_unique(type_defs: List[SchemaType], merge_roots: bool):
    types_names: Dict[str, Any] = {}
    for type_def in type_defs:
        type_name = get_graphql_type_name(type_def)
        if not type_name:
            continue

        if merge_roots and type_name in ROOTS_NAMES:
            continue

        if type_name in types_names:
            type_def_name = getattr(type_def, "__name__") or type_def
            raise ValueError(
                f"Types '{type_def_name}' and '{types_names[type_name]}' both define "
                f"GraphQL type with name '{type_name}'."
            )

        types_names[type_name] = type_def


def assert_types_not_abstract(type_defs: List[SchemaType]):
    for type_def in type_defs:
        if isinstance(type_def, SchemaBindable):
            continue

        if (
            isinstance(type_def, type)
            and issubclass(type_def, GraphQLType)
            and getattr(type_def, "__abstract__", None)
        ):
            raise ValueError(
                f"Type '{type_def.__name__}' is an abstract type and can't be used "
                "for schema creation."
            )
