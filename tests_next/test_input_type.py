from typing import Optional

from graphql import graphql_sync

from ariadne_graphql_modules import gql
from ariadne_graphql_modules.next import (
    GraphQLInput,
    GraphQLObject,
    make_executable_schema,
)


def test_input_type_arg(assert_schema_equals):
    class SearchInput(GraphQLInput):
        query: Optional[str]
        age: Optional[int]

    class QueryType(GraphQLObject):
        search: str

        @GraphQLObject.resolver("search")
        def resolve_search(*_, input: SearchInput) -> str:
            return f"{repr([input.query, input.age])}"

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          search(input: SearchInput!): String!
        }

        input SearchInput {
          query: String
          age: Int
        }
        """,
    )

    result = graphql_sync(schema, '{ search(input: { query: "Hello" }) }')

    assert not result.errors
    assert result.data == {"search": "['Hello', None]"}


def test_schema_input_type_arg(assert_schema_equals):
    class SearchInput(GraphQLInput):
        __schema__ = """
        input SearchInput {
          query: String
          age: Int
        }
        """

        query: Optional[str]
        age: Optional[int]

    class QueryType(GraphQLObject):
        search: str

        @GraphQLObject.resolver("search")
        def resolve_search(*_, input: SearchInput) -> str:
            return f"{repr([input.query, input.age])}"

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          search(input: SearchInput!): String!
        }

        input SearchInput {
          query: String
          age: Int
        }
        """,
    )

    result = graphql_sync(schema, '{ search(input: { query: "Hello" }) }')

    assert not result.errors
    assert result.data == {"search": "['Hello', None]"}


def test_input_type_automatic_out_name_arg(assert_schema_equals):
    class SearchInput(GraphQLInput):
        query: Optional[str]
        min_age: Optional[int]

    class QueryType(GraphQLObject):
        search: str

        @GraphQLObject.resolver("search")
        def resolve_search(*_, input: SearchInput) -> str:
            return f"{repr([input.query, input.min_age])}"

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          search(input: SearchInput!): String!
        }

        input SearchInput {
          query: String
          minAge: Int
        }
        """,
    )

    result = graphql_sync(schema, "{ search(input: { minAge: 21 }) }")

    assert not result.errors
    assert result.data == {"search": "[None, 21]"}


def test_schema_input_type_automatic_out_name_arg(assert_schema_equals):
    class SearchInput(GraphQLInput):
        __schema__ = """
        input SearchInput {
          query: String
          minAge: Int
        }
        """

        query: Optional[str]
        min_age: Optional[int]

    class QueryType(GraphQLObject):
        search: str

        @GraphQLObject.resolver("search")
        def resolve_search(*_, input: SearchInput) -> str:
            return f"{repr([input.query, input.min_age])}"

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          search(input: SearchInput!): String!
        }

        input SearchInput {
          query: String
          minAge: Int
        }
        """,
    )

    result = graphql_sync(schema, "{ search(input: { minAge: 21 }) }")

    assert not result.errors
    assert result.data == {"search": "[None, 21]"}
