from typing import (
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
    cast,
)

from ariadne import (
    SchemaBindable,
    SchemaDirectiveVisitor,
    repair_schema_default_enum_values,
    validate_schema_default_enum_values,
)
from graphql import (
    ConstDirectiveNode,
    DocumentNode,
    FieldDefinitionNode,
    GraphQLSchema,
    NamedTypeNode,
    ObjectTypeDefinitionNode,
    TypeDefinitionNode,
    assert_valid_schema,
    build_ast_schema,
    concat_ast,
    parse,
)
from graphql.language import ast

from .bases import BaseType, BindableType, DeferredType, DefinitionType
from .enum_type import EnumType

ROOT_TYPES = ["Query", "Mutation", "Subscription"]


def make_executable_schema(
    *args: Union[Type[BaseType], SchemaBindable, str],
    merge_roots: bool = True,
    extra_directives: Optional[Dict[str, Type[SchemaDirectiveVisitor]]] = None,
):
    all_types = get_all_types(args)
    extra_defs = parse_extra_sdl(args)
    extra_bindables: List[SchemaBindable] = [
        arg for arg in args if isinstance(arg, SchemaBindable)
    ]

    type_defs: List[Type[DefinitionType]] = []
    for type_ in all_types:
        if issubclass(type_, DefinitionType):
            type_defs.append(type_)

    validate_no_missing_definitions(all_types, type_defs, extra_defs)

    schema = build_schema(type_defs, extra_defs, merge_roots)

    if extra_bindables:
        for bindable in extra_bindables:
            bindable.bind_to_schema(schema)

    if extra_directives:
        SchemaDirectiveVisitor.visit_schema_directives(schema, extra_directives)

    assert_valid_schema(schema)
    validate_schema_default_enum_values(schema)
    repair_schema_default_enum_values(schema)

    add_directives_to_schema(schema, type_defs)

    return schema


def get_all_types(
    args: Sequence[Union[Type[BaseType], SchemaBindable, str]]
) -> List[Type[BaseType]]:
    all_types: List[Type[BaseType]] = []
    for arg in args:
        if isinstance(arg, (str, SchemaBindable)):
            continue  # Skip args of unsupported types

        for child_type in arg.__get_types__():
            if child_type not in all_types:
                all_types.append(child_type)
    return all_types


def parse_extra_sdl(
    args: Sequence[Union[Type[BaseType], SchemaBindable, str]]
) -> List[TypeDefinitionNode]:
    sdl_strings: List[str] = [cast(str, arg) for arg in args if isinstance(arg, str)]
    if not sdl_strings:
        return []

    extra_sdl = "\n\n".join(sdl_strings)
    return cast(
        List[TypeDefinitionNode],
        list(parse(extra_sdl).definitions),
    )


def validate_no_missing_definitions(
    all_types: List[Type[BaseType]],
    type_defs: List[Type[DefinitionType]],
    extra_defs: List[TypeDefinitionNode],
):
    deferred_names: List[str] = []
    for type_ in all_types:
        if isinstance(type_, DeferredType):
            deferred_names.append(type_.graphql_name)

    real_names = [type_.graphql_name for type_ in type_defs]
    real_names += [definition.name.value for definition in extra_defs]

    missing_names = set(deferred_names) - set(real_names)
    if missing_names:
        raise ValueError(
            "Following types are defined as deferred and are missing "
            f"from schema: {', '.join(missing_names)}"
        )


def build_schema(
    type_defs: List[Type[DefinitionType]],
    extra_defs: List[TypeDefinitionNode],
    merge_roots: bool = True,
) -> GraphQLSchema:
    schema_definitions: List[ast.DocumentNode] = []
    if merge_roots:
        schema_definitions.append(build_root_schema(type_defs, extra_defs))
        for type_ in type_defs:
            if type_.graphql_name not in ROOT_TYPES or not merge_roots:
                schema_definitions.append(parse(type_.__schema__))
        for extra_type_def in extra_defs:
            if extra_type_def.name.value not in ROOT_TYPES or not merge_roots:
                schema_definitions.append(DocumentNode(definitions=(extra_type_def,)))

    ast_document = concat_ast(schema_definitions)
    schema = build_ast_schema(ast_document)

    for type_ in type_defs:
        if issubclass(type_, BindableType):
            type_.__bind_to_schema__(schema)

    return schema


RootTypeDef = Tuple[str, DocumentNode]


def build_root_schema(
    type_defs: List[Type[DefinitionType]],
    extra_defs: List[TypeDefinitionNode],
) -> DocumentNode:
    root_types: Dict[str, List[RootTypeDef]] = {
        "Query": [],
        "Mutation": [],
        "Subscription": [],
    }

    for type_def in type_defs:
        if type_def.graphql_name in root_types:
            root_types[type_def.graphql_name].append(
                (type_def.__name__, parse(type_def.__schema__))
            )

    for extra_type_def in extra_defs:
        if extra_type_def.name.value in root_types:
            root_types[extra_type_def.name.value].append(
                ("extra_sdl", DocumentNode(definitions=(extra_type_def,)))
            )

    schema: List[DocumentNode] = []
    for root_name, root_type_defs in root_types.items():
        if len(root_type_defs) == 1:
            schema.append(root_type_defs[0][1])
        elif root_type_defs:
            schema.append(merge_root_types(root_name, root_type_defs))

    return concat_ast(schema)


def merge_root_types(root_name: str, type_defs: List[RootTypeDef]) -> DocumentNode:
    interfaces: List[NamedTypeNode] = []
    directives: List[ConstDirectiveNode] = []
    fields: Dict[str, Tuple[str, FieldDefinitionNode]] = {}

    for type_source, type_def in type_defs:
        type_definition = cast(ObjectTypeDefinitionNode, type_def.definitions[0])
        interfaces.extend(type_definition.interfaces)
        directives.extend(type_definition.directives)

        for field_def in type_definition.fields:
            field_name = field_def.name.value
            if field_name in fields:
                other_type_source = fields[field_name][0]
                raise ValueError(
                    f"Multiple {root_name} types are defining same field "
                    f"'{field_name}': {other_type_source}, {type_source}"
                )

            fields[field_name] = (type_source, field_def)

    merged_definition = ast.ObjectTypeDefinitionNode()
    merged_definition.name = ast.NameNode()
    merged_definition.name.value = root_name
    merged_definition.interfaces = tuple(interfaces)
    merged_definition.directives = tuple(directives)
    merged_definition.fields = tuple(
        fields[field_name][1] for field_name in sorted(fields)
    )

    merged_document = DocumentNode()
    merged_document.definitions = (merged_definition,)

    return merged_document


def add_directives_to_schema(
    schema: GraphQLSchema, type_defs: List[Type[DefinitionType]]
):
    directives: Dict[str, Type[SchemaDirectiveVisitor]] = {}
    for type_def in type_defs:
        visitor = getattr(type_def, "__visitor__", None)
        if visitor and issubclass(visitor, SchemaDirectiveVisitor):
            directives[type_def.graphql_name] = visitor

    if directives:
        SchemaDirectiveVisitor.visit_schema_directives(schema, directives)


def repair_default_enum_values(schema, types_list: List[Type[DefinitionType]]) -> None:
    for type_ in types_list:
        if issubclass(type_, EnumType):
            type_.__bind_to_default_values__(schema)
