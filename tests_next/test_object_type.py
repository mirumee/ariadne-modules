from graphql import graphql_sync

from ariadne import make_executable_schema

from ariadne_graphql_modules.next import GraphQLObject, make_executable_schema, object_field


def test_minimal_object_type(assert_schema_equals):
    class QueryType(GraphQLObject):
        @object_field
        def hello(obj) -> str:
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

    result = graphql_sync(schema, "{ hello }", root_value={"hello": "Hello World!"})

    assert not result.errors
    assert result.data == {"hello": "Hello World!"}
