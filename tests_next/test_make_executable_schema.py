import pytest
from graphql import graphql_sync

from ariadne import QueryType
from ariadne_graphql_modules.next import GraphQLObject, make_executable_schema


def test_executable_schema_from_vanilla_schema_definition(assert_schema_equals):
    query_type = QueryType()
    query_type.set_field("message", lambda *_: "Hello world!")

    schema = make_executable_schema(
        """
        type Query {
          message: String!
        }
        """,
        query_type
    )

    assert_schema_equals(
        schema,
        """
        type Query {
          message: String!
        }
        """,
    )

    result = graphql_sync(schema, '{ message }')

    assert not result.errors
    assert result.data == {"message": "Hello world!"}


def test_executable_schema_from_combined_vanilla_and_new_schema_definition(assert_schema_equals):
    class UserType(GraphQLObject):
        name: str
        email: str

    query_type = QueryType()
    query_type.set_field(
        "user", lambda *_: UserType(name="Bob", email="test@example.com")
    )

    schema = make_executable_schema(
        """
        type Query {
          user: User!
        }
        """,
        query_type,
        UserType,
    )

    assert_schema_equals(
        schema,
        """
        type Query {
          user: User!
        }

        type User {
          name: String!
          email: String!
        }
        """,
    )

    result = graphql_sync(schema, '{ user { name email } }')

    assert not result.errors
    assert result.data == {
        "user": {"name": "Bob", "email": "test@example.com"},
    }


def test_executable_schema_with_merged_roots(assert_schema_equals):
    class FirstRoot(GraphQLObject):
        __graphql_name__ = "Query"

        name: str
        surname: str

    class SecondRoot(GraphQLObject):
        __graphql_name__ = "Query"

        message: str

    class ThirdRoot(GraphQLObject):
        __graphql_name__ = "Query"

        score: int

    schema = make_executable_schema(FirstRoot, SecondRoot, ThirdRoot)

    assert_schema_equals(
        schema,
        """
        type Query {
          message: String!
          name: String!
          score: Int!
          surname: String!
        }
        """,
    )


def test_executable_schema_with_merged_object_and_vanilla_roots(assert_schema_equals):
    class FirstRoot(GraphQLObject):
        __graphql_name__ = "Query"

        name: str
        surname: str

    class SecondRoot(GraphQLObject):
        __graphql_name__ = "Query"

        message: str

    schema = make_executable_schema(
        FirstRoot,
        SecondRoot,
        """
        type Query {
          score: Int!
        }
        """,
    )

    assert_schema_equals(
        schema,
        """
        type Query {
          message: String!
          name: String!
          score: Int!
          surname: String!
        }
        """,
    )


def test_multiple_roots_fail_validation_if_merge_roots_is_disabled(snapshot):
    class FirstRoot(GraphQLObject):
        __graphql_name__ = "Query"

        name: str
        surname: str

    class SecondRoot(GraphQLObject):
        __graphql_name__ = "Query"

        message: str

    class ThirdRoot(GraphQLObject):
        __graphql_name__ = "Query"

        score: int

    with pytest.raises(ValueError) as exc_info:
        make_executable_schema(FirstRoot, SecondRoot, ThirdRoot, merge_roots=False)

    snapshot.assert_match(str(exc_info.value))
