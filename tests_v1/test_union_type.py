from dataclasses import dataclass

import pytest
from ariadne import SchemaDirectiveVisitor
from graphql import GraphQLError, graphql_sync

from ariadne_graphql_modules.v1 import (
    DirectiveType,
    ObjectType,
    UnionType,
    make_executable_schema,
)


def test_union_type_raises_attribute_error_when_defined_without_schema(data_regression):
    with pytest.raises(AttributeError) as err:
        # pylint: disable=unused-variable
        class ExampleUnion(UnionType):
            pass

    data_regression.check(str(err.value))


def test_union_type_raises_error_when_defined_with_invalid_schema_type(data_regression):
    with pytest.raises(TypeError) as err:
        # pylint: disable=unused-variable
        class ExampleUnion(UnionType):
            __schema__ = True

    data_regression.check(str(err.value))


def test_union_type_raises_error_when_defined_with_invalid_schema_str(data_regression):
    with pytest.raises(GraphQLError) as err:
        # pylint: disable=unused-variable
        class ExampleUnion(UnionType):
            __schema__ = "unien Example = A | B"

    data_regression.check(str(err.value))


def test_union_type_raises_error_when_defined_with_invalid_graphql_type_schema(
    data_regression,
):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class ExampleUnion(UnionType):
            __schema__ = "scalar DateTime"

    data_regression.check(str(err.value))


def test_union_type_raises_error_when_defined_with_multiple_types_schema(
    data_regression,
):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class ExampleUnion(UnionType):
            __schema__ = """
            union A = C | D

            union B = C | D
            """

    data_regression.check(str(err.value))


@dataclass
class User:
    id: int
    name: str


@dataclass
class Comment:
    id: int
    message: str


class UserType(ObjectType):
    __schema__ = """
    type User {
        id: ID!
        name: String!
    }
    """


class CommentType(ObjectType):
    __schema__ = """
    type Comment {
        id: ID!
        message: String!
    }
    """


class ResultUnion(UnionType):
    __schema__ = "union Result = Comment | User"
    __requires__ = [CommentType, UserType]

    @staticmethod
    def resolve_type(instance, *_):
        if isinstance(instance, Comment):
            return "Comment"

        if isinstance(instance, User):
            return "User"

        return None


class QueryType(ObjectType):
    __schema__ = """
    type Query {
        results: [Result!]!
    }
    """
    __requires__ = [ResultUnion]

    @staticmethod
    def resolve_results(*_):
        return [
            User(id=1, name="Alice"),
            Comment(id=1, message="Hello world!"),
        ]


schema = make_executable_schema(QueryType, UserType, CommentType)


def test_union_type_extracts_graphql_name():
    class ExampleUnion(UnionType):
        __schema__ = "union Example = User | Comment"
        __requires__ = [UserType, CommentType]

    assert ExampleUnion.graphql_name == "Example"


def test_union_type_raises_error_when_defined_without_member_type_dependency(
    data_regression,
):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class ExampleUnion(UnionType):
            __schema__ = "union Example = User | Comment"
            __requires__ = [UserType]

    data_regression.check(str(err.value))


def test_interface_type_binds_type_resolver():
    query = """
    query {
        results {
            ... on User {
                __typename
                id
                name
            }
            ... on Comment {
                __typename
                id
                message
            }
        }
    }
    """

    result = graphql_sync(schema, query)
    assert result.data == {
        "results": [
            {
                "__typename": "User",
                "id": "1",
                "name": "Alice",
            },
            {
                "__typename": "Comment",
                "id": "1",
                "message": "Hello world!",
            },
        ],
    }


def test_union_type_can_be_extended_with_new_types():
    # pylint: disable=unused-variable
    class ExampleUnion(UnionType):
        __schema__ = "union Result = User | Comment"
        __requires__ = [UserType, CommentType]

    class ThreadType(ObjectType):
        __schema__ = """
        type Thread {
            id: ID!
            title: String!
        }
        """

    class ExtendExampleUnion(UnionType):
        __schema__ = "union Result = Thread"
        __requires__ = [ExampleUnion, ThreadType]


def test_union_type_can_be_extended_with_directive():
    # pylint: disable=unused-variable
    class ExampleDirective(DirectiveType):
        __schema__ = "directive @example on UNION"
        __visitor__ = SchemaDirectiveVisitor

    class ExampleUnion(UnionType):
        __schema__ = "union Result = User | Comment"
        __requires__ = [UserType, CommentType]

    class ExtendExampleUnion(UnionType):
        __schema__ = """
        extend union Result @example
        """
        __requires__ = [ExampleUnion, ExampleDirective]


def test_union_type_raises_error_when_defined_without_extended_dependency(
    data_regression,
):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class ExtendExampleUnion(UnionType):
            __schema__ = "extend union Result = User"
            __requires__ = [UserType]

    data_regression.check(str(err.value))


def test_union_type_raises_error_when_extended_dependency_is_wrong_type(
    data_regression,
):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class ExampleType(ObjectType):
            __schema__ = """
            type Example {
                id: ID!
            }
            """

        class ExtendExampleUnion(UnionType):
            __schema__ = "extend union Example = User"
            __requires__ = [ExampleType, UserType]

    data_regression.check(str(err.value))
