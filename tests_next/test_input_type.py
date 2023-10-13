from typing import Optional

from graphql import graphql_sync

from ariadne_graphql_modules import gql
from ariadne_graphql_modules.next import (
    GraphQLInput,
    GraphQLObject,
    make_executable_schema,
)


def test_field_with_input_type_arg(assert_schema_equals):
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
    assert result.data == {"hello": "Hello World!"}
