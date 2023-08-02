from graphql import graphql_sync

from ariadne import make_executable_schema

from ariadne_graphql_modules.next import GraphQLObject, make_executable_schema


def test_minimal_object_type(assert_schema_equals):
    class QueryType(GraphQLObject):
        @GraphQLObject.field
        def hello(obj, info) -> str:
            return "Hello World!"

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          hello: String!
        }
        """,
    )

    result = graphql_sync(schema, "{ hello }")

    assert not result.errors
    assert result.data == {"hello": "Hello World!"}
