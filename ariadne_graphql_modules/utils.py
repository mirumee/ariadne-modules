from typing import Any, Mapping

from graphql import (
    DefinitionNode,
    GraphQLResolveInfo,
    ListTypeNode,
    NonNullTypeNode,
    TypeNode,
    parse,
)


def parse_definition(type_name: Any, schema: Any) -> DefinitionNode:
    if not isinstance(schema, str):
        raise TypeError(
            f"{type_name} class was defined with __schema__ of invalid type: "
            f"{type(schema).__name__}"
        )

    definitions = parse(schema).definitions

    if len(definitions) > 1:
        definitions_types = [type(definition).__name__ for definition in definitions]
        raise ValueError(
            f"{type_name} class was defined with __schema__ containing more "
            f"than one GraphQL definition (found: {', '.join(definitions_types)})"
        )

    return definitions[0]


def unwrap_type_node(field_type: TypeNode):
    if isinstance(field_type, (NonNullTypeNode, ListTypeNode)):
        return unwrap_type_node(field_type.type)
    return field_type


def create_alias_resolver(field_name: str):
    def default_aliased_field_resolver(
        source: Any, info: GraphQLResolveInfo, **args: Any
    ) -> Any:
        value = (
            source.get(field_name)
            if isinstance(source, Mapping)
            else getattr(source, field_name, None)
        )

        if callable(value):
            return value(info, **args)
        return value

    return default_aliased_field_resolver
