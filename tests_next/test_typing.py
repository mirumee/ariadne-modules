from enum import Enum
import sys
from typing import TYPE_CHECKING, Annotated, List, Optional, Union

from graphql import ListTypeNode, NameNode, NamedTypeNode, NonNullTypeNode
import pytest

from ariadne_graphql_modules.next import GraphQLObject, deferred, graphql_enum
from ariadne_graphql_modules.next.typing import get_graphql_type, get_type_node

if TYPE_CHECKING:
    from .types import ForwardEnum, ForwardScalar


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


def test_get_graphql_type_from_python_builtin_type_returns_none(metadata):
    assert get_graphql_type(Optional[str]) is None
    assert get_graphql_type(Union[int, None]) is None
    assert get_graphql_type(Optional[bool]) is None


@pytest.mark.skipif(
    sys.version_info >= (3, 9) and sys.version_info < (3, 10),
    reason="Skip test for Python 3.9",
)
def test_get_graphql_type_from_python_builtin_type_returns_none_pipe_union(metadata):
    assert get_graphql_type(float | None) is None


def test_get_graphql_type_from_graphql_type_subclass_returns_type(metadata):
    class UserType(GraphQLObject): ...

    assert get_graphql_type(UserType) == UserType
    assert get_graphql_type(Optional[UserType]) == UserType
    assert get_graphql_type(List[UserType]) == UserType
    assert get_graphql_type(Optional[List[Optional[UserType]]]) == UserType


def test_get_graphql_type_from_enum_returns_type(metadata):
    class UserLevel(Enum):
        GUEST = 0
        MEMBER = 1
        MODERATOR = 2
        ADMINISTRATOR = 3

    assert get_graphql_type(UserLevel) == UserLevel
    assert get_graphql_type(Optional[UserLevel]) == UserLevel
    assert get_graphql_type(List[UserLevel]) == UserLevel
    assert get_graphql_type(Optional[List[Optional[UserLevel]]]) == UserLevel


def test_get_graphql_type_node_from_python_builtin_type(metadata):
    assert_named_type(get_type_node(metadata, Optional[str]), "String")
    assert_named_type(get_type_node(metadata, Union[int, None]), "Int")
    assert_named_type(get_type_node(metadata, Optional[bool]), "Boolean")


@pytest.mark.skipif(
    sys.version_info >= (3, 9) and sys.version_info < (3, 10),
    reason="Skip test for Python 3.9",
)
def test_get_graphql_type_node_from_python_builtin_type_pipe_union(metadata):
    assert_named_type(get_type_node(metadata, float | None), "Float")


def test_get_non_null_graphql_type_node_from_python_builtin_type(metadata):
    assert_non_null_type(get_type_node(metadata, str), "String")
    assert_non_null_type(get_type_node(metadata, int), "Int")
    assert_non_null_type(get_type_node(metadata, float), "Float")
    assert_non_null_type(get_type_node(metadata, bool), "Boolean")


def test_get_graphql_type_node_from_graphql_type(metadata):
    class UserType(GraphQLObject): ...

    assert_non_null_type(get_type_node(metadata, UserType), "User")
    assert_named_type(get_type_node(metadata, Optional[UserType]), "User")


def test_get_graphql_list_type_node_from_python_builtin_type(metadata):
    assert_list_type(get_type_node(metadata, Optional[List[str]]), "String")
    assert_list_type(get_type_node(metadata, Union[List[int], None]), "Int")

    assert_list_type(get_type_node(metadata, Optional[List[bool]]), "Boolean")


@pytest.mark.skipif(
    sys.version_info >= (3, 9) and sys.version_info < (3, 10),
    reason="Skip test for Python 3.9",
)
def test_get_graphql_list_type_node_from_python_builtin_type_pipe_union(metadata):
    assert_list_type(get_type_node(metadata, List[float] | None), "Float")


def test_get_non_null_graphql_list_type_node_from_python_builtin_type(metadata):
    assert_non_null_list_type(get_type_node(metadata, List[str]), "String")
    assert_non_null_list_type(get_type_node(metadata, List[int]), "Int")
    assert_non_null_list_type(get_type_node(metadata, List[float]), "Float")
    assert_non_null_list_type(get_type_node(metadata, List[bool]), "Boolean")


def test_get_graphql_type_node_from_annotated_type(metadata):
    class MockType(GraphQLObject):
        field: Annotated["ForwardScalar", deferred("tests_next.types")]

    assert_non_null_type(
        get_type_node(metadata, MockType.__annotations__["field"]), "Forward"
    )


def test_get_graphql_type_node_from_annotated_type_with_relative_path(metadata):
    class MockType(GraphQLObject):
        field: Annotated["ForwardScalar", deferred(".types")]

    assert_non_null_type(
        get_type_node(metadata, MockType.__annotations__["field"]), "Forward"
    )


def test_get_graphql_type_node_from_nullable_annotated_type(metadata):
    class MockType(GraphQLObject):
        field: Optional[Annotated["ForwardScalar", deferred("tests_next.types")]]

    assert_named_type(
        get_type_node(metadata, MockType.__annotations__["field"]), "Forward"
    )


def test_get_graphql_type_node_from_annotated_enum(metadata):
    class MockType(GraphQLObject):
        field: Annotated["ForwardEnum", deferred("tests_next.types")]

    assert_non_null_type(
        get_type_node(metadata, MockType.__annotations__["field"]), "ForwardEnum"
    )


def test_get_graphql_type_node_from_enum_type(metadata):
    class UserLevel(Enum):
        GUEST = 0
        MEMBER = 1
        MODERATOR = 2
        ADMINISTRATOR = 3

    assert_non_null_type(get_type_node(metadata, UserLevel), "UserLevel")
    assert_named_type(get_type_node(metadata, Optional[UserLevel]), "UserLevel")


def test_get_graphql_type_node_from_annotated_enum_type(metadata):
    @graphql_enum(name="SeverityEnum")
    class SeverityLevel(Enum):
        LOW = 0
        MEDIUM = 1
        HIGH = 2

    assert_non_null_type(get_type_node(metadata, SeverityLevel), "SeverityEnum")
    assert_named_type(get_type_node(metadata, Optional[SeverityLevel]), "SeverityEnum")
