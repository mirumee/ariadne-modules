from typing import Optional, cast

from graphql import (
    ConstDirectiveNode,
    DefinitionNode,
    DocumentNode,
    FieldDefinitionNode,
    NamedTypeNode,
    ObjectTypeDefinitionNode,
    StringValueNode,
    TypeDefinitionNode,
)

DefinitionsList = list[DefinitionNode]

ROOTS_NAMES = ("Query", "Mutation", "Subscription")


def merge_root_nodes(document_node: DocumentNode) -> DocumentNode:
    roots_definitions: dict[str, list[TypeDefinitionNode]] = {
        root: [] for root in ROOTS_NAMES
    }
    final_definitions: DefinitionsList = []

    for node in document_node.definitions:
        if (
            isinstance(node, TypeDefinitionNode)
            and node.name.value in roots_definitions
        ):
            roots_definitions[node.name.value].append(node)
        else:
            final_definitions.append(node)

    for definitions_to_merge in roots_definitions.values():
        if len(definitions_to_merge) > 1:
            final_definitions.append(merge_nodes(definitions_to_merge))
        elif definitions_to_merge:
            final_definitions.extend(definitions_to_merge)

    return DocumentNode(definitions=tuple(final_definitions))


def merge_nodes(nodes: list[TypeDefinitionNode]) -> ObjectTypeDefinitionNode:
    root_name = nodes[0].name.value

    description: Optional[StringValueNode] = None
    interfaces: list[NamedTypeNode] = []
    directives: list[ConstDirectiveNode] = []
    fields: dict[str, FieldDefinitionNode] = {}

    for node in nodes:
        node = cast(ObjectTypeDefinitionNode, node)
        if node.description:
            if description:
                raise ValueError(
                    f"Multiple {root_name} types are defining descriptions."
                )

            description = node.description

        if node.interfaces:
            interfaces.extend(node.interfaces)
        if node.directives:
            directives.extend(node.directives)

        for field_node in node.fields:
            field_name = field_node.name.value
            if field_name in fields:
                other_type_source = fields[field_name]
                raise ValueError(
                    f"Multiple {root_name} types are defining same field "
                    f"'{field_name}': {other_type_source}, {field_node}"
                )
            fields[field_name] = field_node

    return ObjectTypeDefinitionNode(
        name=nodes[0].name,
        description=description,
        interfaces=tuple(interfaces),
        directives=tuple(directives),
        fields=tuple(fields[field_name] for field_name in sorted(fields)),
    )
