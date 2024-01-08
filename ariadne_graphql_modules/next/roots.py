from typing import Dict, List, Optional, cast

from graphql import (
    ConstDirectiveNode,
    DocumentNode,
    FieldDefinitionNode,
    NamedTypeNode,
    ObjectTypeDefinitionNode,
    StringValueNode,
    TypeDefinitionNode,
)

DefinitionsList = List[TypeDefinitionNode]

ROOTS_NAMES = ("Query", "Mutation", "Subscription")


def merge_root_nodes(document_node: DocumentNode) -> DocumentNode:
    roots_definitions: Dict[str, List] = {root: [] for root in ROOTS_NAMES}
    final_definitions: DefinitionsList = []

    for node in document_node.definitions:
        if not isinstance(node, TypeDefinitionNode):
            raise ValueError(
                "Only type definition nodes can be merged. "
                f"Found unsupported node: '{node}'"
            )

        if node.name.value in roots_definitions:
            roots_definitions[node.name.value].append(node)
        else:
            final_definitions.append(node)

    for definitions_to_merge in roots_definitions.values():
        if len(definitions_to_merge) > 1:
            final_definitions.append(merge_nodes(definitions_to_merge))
        elif definitions_to_merge:
            final_definitions.extend(definitions_to_merge)

    return DocumentNode(definitions=tuple(final_definitions))


def merge_nodes(nodes: List[TypeDefinitionNode]) -> ObjectTypeDefinitionNode:
    root_name = nodes[0].name.value

    description: Optional[StringValueNode] = None
    interfaces: List[NamedTypeNode] = []
    directives: List[ConstDirectiveNode] = []
    fields: Dict[str, FieldDefinitionNode] = {}

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
                other_type_source = fields[field_name][0]
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
