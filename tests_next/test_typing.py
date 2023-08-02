from typing import List, Optional, Union

from graphql import ListTypeNode, NameNode, NamedTypeNode, NonNullTypeNode

from ariadne_graphql_modules.next import GraphQLObject
from ariadne_graphql_modules.next.typing import get_type_node


def assert_non_null_type(type_node, name: str):
    assert isinstance(type_node, NonNullTypeNode)
    assert_named_type(type_node.type, name)


def assert_non_null_list_type(type_node, name: str):
    assert isinstance(type_node, NonNullTypeNode)
    assert isinstance(type_node.type, ListTypeNode)
    assert isinstance(type_node.type.type, NonNullTypeNode)
    assert_named_type(type_node.type.type.type, name)


def assert_list_type(type_node, name: str):
    assert isinstance(type_node, ListTypeNode)
    assert isinstance(type_node.type, NonNullTypeNode)
    assert_named_type(type_node.type.type, name)


def assert_named_type(type_node, name: str):
    assert isinstance(type_node, NamedTypeNode)
    assert isinstance(type_node.name, NameNode)
    assert type_node.name.value == name


def test_get_graphql_type_node_from_python_builtin_type():
    assert_named_type(get_type_node(Optional[str]), "String")
    assert_named_type(get_type_node(Union[int, None]), "Int")
    assert_named_type(get_type_node(float | None), "Float")
    assert_named_type(get_type_node(Optional[bool]), "Boolean")


def test_get_non_null_graphql_type_node_from_python_builtin_type():
    assert_non_null_type(get_type_node(str), "String")
    assert_non_null_type(get_type_node(int), "Int")
    assert_non_null_type(get_type_node(float), "Float")
    assert_non_null_type(get_type_node(bool), "Boolean")


def test_get_graphql_type_node_from_graphql_type():
    class UserType(GraphQLObject):
        ...

    assert_non_null_type(get_type_node(UserType), "User")
    assert_named_type(get_type_node(Optional[UserType]), "User")


def test_get_graphql_list_type_node_from_python_builtin_type():
    assert_list_type(get_type_node(Optional[List[str]]), "String")
    assert_list_type(get_type_node(Union[List[int], None]), "Int")
    assert_list_type(get_type_node(List[float] | None), "Float")
    assert_list_type(get_type_node(Optional[List[bool]]), "Boolean")


def test_get_non_null_graphql_list_type_node_from_python_builtin_type():
    assert_non_null_list_type(get_type_node(List[str]), "String")
    assert_non_null_list_type(get_type_node(List[int]), "Int")
    assert_non_null_list_type(get_type_node(List[float]), "Float")
    assert_non_null_list_type(get_type_node(List[bool]), "Boolean")
