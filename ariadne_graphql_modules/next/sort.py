from typing import Dict, List, Optional, Union, cast

from graphql import (
    DirectiveNode,
    DocumentNode,
    InputObjectTypeDefinitionNode,
    InterfaceTypeDefinitionNode,
    ListTypeNode,
    NonNullTypeNode,
    ObjectTypeDefinitionNode,
    ScalarTypeDefinitionNode,
    TypeDefinitionNode,
    TypeNode,
)

from .roots import ROOTS_NAMES


def sort_schema_document(document: DocumentNode) -> DocumentNode:
    unsorted_nodes: Dict[str, TypeDefinitionNode] = {}
    sorted_nodes: List[TypeDefinitionNode] = []

    for node in document.definitions:
        cast_node = cast(TypeDefinitionNode, node)
        unsorted_nodes[cast_node.name.value] = cast_node

    # Start schema from directives and scalars
    sorted_nodes += get_sorted_directives(unsorted_nodes)
    sorted_nodes += get_sorted_scalars(unsorted_nodes)

    # Next, include Query, Mutation and Subscription branches
    for root in ROOTS_NAMES:
        sorted_nodes += get_sorted_type(root, unsorted_nodes)

    # Finally include unused types
    sorted_nodes += list(unsorted_nodes.values())

    return DocumentNode(definitions=tuple(sorted_nodes))


def get_sorted_directives(
    unsorted_nodes: Dict[str, TypeDefinitionNode]
) -> List[DirectiveNode]:
    directives: List[DirectiveNode] = []
    for name, model in tuple(unsorted_nodes.items()):
        if isinstance(model, DirectiveNode):
            directives.append(unsorted_nodes.pop(name))

    return sorted(directives, key=lambda m: m.name.value)


def get_sorted_scalars(
    unsorted_nodes: Dict[str, TypeDefinitionNode]
) -> List[ScalarTypeDefinitionNode]:
    scalars: List[ScalarTypeDefinitionNode] = []
    for name, model in tuple(unsorted_nodes.items()):
        if isinstance(model, ScalarTypeDefinitionNode):
            scalars.append(unsorted_nodes.pop(name))

    return sorted(scalars, key=lambda m: m.name.value)


def get_sorted_type(
    root: str,
    unsorted_nodes: Dict[str, TypeDefinitionNode],
) -> List[TypeDefinitionNode]:
    sorted_nodes: List[TypeDefinitionNode] = []
    if root not in unsorted_nodes:
        return sorted_nodes

    root_node = unsorted_nodes.pop(root)
    sorted_nodes.append(root_node)

    if isinstance(root_node, (ObjectTypeDefinitionNode, InterfaceTypeDefinitionNode)):
        sorted_nodes += get_sorted_object_dependencies(root_node, unsorted_nodes)
    elif isinstance(root_node, InputObjectTypeDefinitionNode):
        pass

    return sorted_nodes


def get_sorted_object_dependencies(
    root_node: Union[ObjectTypeDefinitionNode, InterfaceTypeDefinitionNode],
    unsorted_nodes: Dict[str, TypeDefinitionNode],
) -> List[TypeDefinitionNode]:
    sorted_nodes: List[TypeDefinitionNode] = []

    if root_node.interfaces:
        for interface in root_node.interfaces:
            interface_name = interface.name.value
            interface_node = unsorted_nodes.pop(interface_name, None)
            if interface_node:
                sorted_nodes.append(interface_node)
                sorted_nodes += get_sorted_object_dependencies(
                    interface_node, unsorted_nodes
                )

    for field in root_node.fields:
        if field.arguments:
            for argument in field.arguments:
                argument_type = unwrap_type_name(argument.type)
                sorted_nodes += get_sorted_type(argument_type, unsorted_nodes)

        field_type = unwrap_type_name(field.type)
        sorted_nodes += get_sorted_type(field_type, unsorted_nodes)

    return sorted_nodes


def get_sorted_input_dependencies(
    root_node: InputObjectTypeDefinitionNode,
    unsorted_nodes: Dict[str, TypeDefinitionNode],
) -> List[TypeDefinitionNode]:
    sorted_nodes: List[TypeDefinitionNode] = []

    for field in root_node.fields:
        field_type = unwrap_type_name(field.type)
        sorted_nodes += get_sorted_type(field_type, unsorted_nodes)

    return sorted_nodes


def unwrap_type_name(type_node: TypeNode) -> str:
    if isinstance(type_node, (ListTypeNode, NonNullTypeNode)):
        return unwrap_type_name(type_node.type)

    return type_node.name.value
