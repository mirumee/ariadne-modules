from dataclasses import dataclass

import pytest
from ariadne import SchemaDirectiveVisitor
from graphql import GraphQLError, graphql_sync

from ariadne_graphql_modules.v1 import (
    DeferredType,
    DirectiveType,
    InterfaceType,
    ObjectType,
    make_executable_schema,
)


def test_interface_type_raises_attribute_error_when_defined_without_schema(
    data_regression,
):
    with pytest.raises(AttributeError) as err:
        # pylint: disable=unused-variable
        class ExampleInterface(InterfaceType):
            pass

    data_regression.check(str(err.value))


def test_interface_type_raises_error_when_defined_with_invalid_schema_type(
    data_regression,
):
    with pytest.raises(TypeError) as err:
        # pylint: disable=unused-variable
        class ExampleInterface(InterfaceType):
            __schema__ = True

    data_regression.check(str(err.value))


def test_interface_type_raises_error_when_defined_with_invalid_schema_str(
    data_regression,
):
    with pytest.raises(GraphQLError) as err:
        # pylint: disable=unused-variable
        class ExampleInterface(InterfaceType):
            __schema__ = "interfaco Example"

    data_regression.check(str(err.value))


def test_interface_type_raises_error_when_defined_with_invalid_graphql_type_schema(
    data_regression,
):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class ExampleInterface(InterfaceType):
            __schema__ = "type Example"

    data_regression.check(str(err.value))


def test_interface_type_raises_error_when_defined_with_multiple_types_schema(
    data_regression,
):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class ExampleInterface(InterfaceType):
            __schema__ = """
            interface Example

            interface Other
            """

    data_regression.check(str(err.value))


def test_interface_type_raises_error_when_defined_without_fields(data_regression):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class ExampleInterface(InterfaceType):
            __schema__ = "interface Example"

    data_regression.check(str(err.value))


def test_interface_type_extracts_graphql_name():
    class ExampleInterface(InterfaceType):
        __schema__ = """
        interface Example {
            id: ID!
        }
        """

    assert ExampleInterface.graphql_name == "Example"


def test_interface_type_raises_error_when_defined_without_return_type_dependency(
    data_regression,
):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class ExampleInterface(InterfaceType):
            __schema__ = """
            interface Example {
                group: Group
                groups: [Group!]
            }
            """

    data_regression.check(str(err.value))


def test_interface_type_verifies_field_dependency():
    # pylint: disable=unused-variable
    class GroupType(ObjectType):
        __schema__ = """
        type Group {
            id: ID!
        }
        """

    class ExampleInterface(InterfaceType):
        __schema__ = """
        interface Example {
            group: Group
            groups: [Group!]
        }
        """
        __requires__ = [GroupType]


def test_interface_type_verifies_circural_dependency():
    # pylint: disable=unused-variable
    class ExampleInterface(InterfaceType):
        __schema__ = """
        interface Example {
            parent: Example
        }
        """


def test_interface_type_raises_error_when_defined_without_argument_type_dependency(
    data_regression,
):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class ExampleInterface(InterfaceType):
            __schema__ = """
            interface Example {
                actions(input: UserInput): [String!]!
            }
            """

    data_regression.check(str(err.value))


def test_interface_type_verifies_circular_dependency_using_deferred_type():
    # pylint: disable=unused-variable
    class ExampleInterface(InterfaceType):
        __schema__ = """
        interface Example {
            id: ID!
            users: [User]
        }
        """
        __requires__ = [DeferredType("User")]

    class UserType(ObjectType):
        __schema__ = """
        type User {
            roles: [Example]
        }
        """
        __requires__ = [ExampleInterface]


def test_interface_type_can_be_extended_with_new_fields():
    # pylint: disable=unused-variable
    class ExampleInterface(InterfaceType):
        __schema__ = """
        interface Example {
            id: ID!
        }
        """

    class ExtendExampleInterface(InterfaceType):
        __schema__ = """
        extend interface Example {
            name: String
        }
        """
        __requires__ = [ExampleInterface]


def test_interface_type_can_be_extended_with_directive():
    # pylint: disable=unused-variable
    class ExampleDirective(DirectiveType):
        __schema__ = "directive @example on INTERFACE"
        __visitor__ = SchemaDirectiveVisitor

    class ExampleInterface(InterfaceType):
        __schema__ = """
        interface Example {
            id: ID!
        }
        """

    class ExtendExampleInterface(InterfaceType):
        __schema__ = """
        extend interface Example @example
        """
        __requires__ = [ExampleInterface, ExampleDirective]


def test_interface_type_can_be_extended_with_other_interface():
    # pylint: disable=unused-variable
    class ExampleInterface(InterfaceType):
        __schema__ = """
        interface Example {
            id: ID!
        }
        """

    class OtherInterface(InterfaceType):
        __schema__ = """
        interface Other {
            depth: Int! 
        }
        """

    class ExtendExampleInterface(InterfaceType):
        __schema__ = """
        extend interface Example implements Other
        """
        __requires__ = [ExampleInterface, OtherInterface]


def test_interface_type_raises_error_when_defined_without_extended_dependency(
    data_regression,
):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class ExtendExampleInterface(ObjectType):
            __schema__ = """
            extend interface Example {
                name: String
            }
            """

    data_regression.check(str(err.value))


def test_interface_type_raises_error_when_extended_dependency_is_wrong_type(
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

        class ExampleInterface(InterfaceType):
            __schema__ = """
            extend interface Example {
                name: String
            }
            """
            __requires__ = [ExampleType]

    data_regression.check(str(err.value))


def test_interface_type_raises_error_when_defined_with_alias_for_nonexisting_field(
    data_regression,
):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class ExampleInterface(InterfaceType):
            __schema__ = """
            interface User {
                name: String
            }
            """
            __aliases__ = {
                "joinedDate": "joined_date",
            }

    data_regression.check(str(err.value))


def test_interface_type_raises_error_when_defined_with_resolver_for_nonexisting_field(
    data_regression,
):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class ExampleInterface(InterfaceType):
            __schema__ = """
            interface User {
                name: String
            }
            """

            @staticmethod
            def resolve_group(*_):
                return None

    data_regression.check(str(err.value))


@dataclass
class User:
    id: int
    name: str
    summary: str


@dataclass
class Comment:
    id: int
    message: str
    summary: str


class ResultInterface(InterfaceType):
    __schema__ = """
    interface Result {
        summary: String!
        score: Int!
    }
    """

    @staticmethod
    def resolve_type(instance, *_):
        if isinstance(instance, Comment):
            return "Comment"

        if isinstance(instance, User):
            return "User"

        return None

    @staticmethod
    def resolve_score(*_):
        return 42


class UserType(ObjectType):
    __schema__ = """
    type User implements Result {
        id: ID!
        name: String!
        summary: String!
        score: Int!
    }
    """
    __requires__ = [ResultInterface]


class CommentType(ObjectType):
    __schema__ = """
    type Comment implements Result {
        id: ID!
        message: String!
        summary: String!
        score: Int!
    }
    """
    __requires__ = [ResultInterface]

    @staticmethod
    def resolve_score(*_):
        return 16


class QueryType(ObjectType):
    __schema__ = """
    type Query {
        results: [Result!]!
    }
    """
    __requires__ = [ResultInterface]

    @staticmethod
    def resolve_results(*_):
        return [
            User(id=1, name="Alice", summary="Summary for Alice"),
            Comment(id=1, message="Hello world!", summary="Summary for comment"),
        ]


schema = make_executable_schema(QueryType, UserType, CommentType)


def test_interface_type_binds_type_resolver():
    query = """
    query {
        results {
            ... on User {
                __typename
                id
                name
                summary
            }
            ... on Comment {
                __typename
                id
                message
                summary
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
                "summary": "Summary for Alice",
            },
            {
                "__typename": "Comment",
                "id": "1",
                "message": "Hello world!",
                "summary": "Summary for comment",
            },
        ],
    }


def test_interface_type_binds_field_resolvers_to_implementing_types_fields():
    query = """
    query {
        results {
            ... on User {
                __typename
                score
            }
            ... on Comment {
                __typename
                score
            }
        }
    }
    """

    result = graphql_sync(schema, query)
    assert result.data == {
        "results": [
            {
                "__typename": "User",
                "score": 42,
            },
            {
                "__typename": "Comment",
                "score": 16,
            },
        ],
    }
