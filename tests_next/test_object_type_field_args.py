from graphql import GraphQLResolveInfo, graphql_sync

from ariadne_graphql_modules import gql
from ariadne_graphql_modules.next import GraphQLObject, make_executable_schema


def test_object_type_field_resolver_with_scalar_arg(assert_schema_equals):
    class QueryType(GraphQLObject):
        @GraphQLObject.field
        def hello(obj, info: GraphQLResolveInfo, *, name: str) -> str:
            return f"Hello {name}!"

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          hello(name: String!): String!
        }
        """,
    )

    result = graphql_sync(schema, '{ hello(name: "Bob") }')

    assert not result.errors
    assert result.data == {"hello": "Hello Bob!"}


def test_object_type_field_instance_with_scalar_arg(assert_schema_equals):
    def hello_resolver(*_, name: str) -> str:
        return f"Hello {name}!"

    class QueryType(GraphQLObject):
        hello = GraphQLObject.field(hello_resolver)

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          hello(name: String!): String!
        }
        """,
    )

    result = graphql_sync(schema, '{ hello(name: "Bob") }')

    assert not result.errors
    assert result.data == {"hello": "Hello Bob!"}


def test_object_type_field_instance_with_description(assert_schema_equals):
    def hello_resolver(*_, name: str) -> str:
        return f"Hello {name}!"

    class QueryType(GraphQLObject):
        hello = GraphQLObject.field(
            hello_resolver,
            args={
                "name": GraphQLObject.argument(
                    description="Lorem ipsum dolor met!",
                ),
            },
        )

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          hello(
            \"\"\"Lorem ipsum dolor met!\"\"\"
            name: String!
          ): String!
        }
        """,
    )

    result = graphql_sync(schema, '{ hello(name: "Bob") }')

    assert not result.errors
    assert result.data == {"hello": "Hello Bob!"}


def test_resolver_decorator_sets_resolver_with_arg_for_type_hint_field(
    assert_schema_equals,
):
    class QueryType(GraphQLObject):
        hello: str

        @GraphQLObject.resolver("hello")
        def resolve_hello(*_, name: str):
            return f"Hello {name}!"

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          hello(name: String!): String!
        }
        """,
    )

    result = graphql_sync(schema, '{ hello(name: "Bob") }')

    assert not result.errors
    assert result.data == {"hello": "Hello Bob!"}


def test_object_type_field_instance_with_argument_description(assert_schema_equals):
    def hello_resolver(*_, name: str) -> str:
        return f"Hello {name}!"

    class QueryType(GraphQLObject):
        hello = GraphQLObject.field(
            hello_resolver,
            args={
                "name": GraphQLObject.argument(
                    description="Lorem ipsum dolor met!",
                ),
            },
        )

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          hello(
            \"\"\"Lorem ipsum dolor met!\"\"\"
            name: String!
          ): String!
        }
        """,
    )

    result = graphql_sync(schema, '{ hello(name: "Bob") }')

    assert not result.errors
    assert result.data == {"hello": "Hello Bob!"}


def test_object_type_field_resolver_instance_arg_with_out_name(assert_schema_equals):
    class QueryType(GraphQLObject):
        hello: str

        @GraphQLObject.resolver("hello")
        def resolve_hello(*_, first_name: str) -> str:
            return f"Hello {first_name}!"

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          hello(firstName: String!): String!
        }
        """,
    )

    result = graphql_sync(schema, '{ hello(firstName: "Bob") }')

    assert not result.errors
    assert result.data == {"hello": "Hello Bob!"}


def test_object_type_field_instance_arg_with_out_name(assert_schema_equals):
    class QueryType(GraphQLObject):
        @GraphQLObject.field
        def hello(*_, first_name: str) -> str:
            return f"Hello {first_name}!"

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          hello(firstName: String!): String!
        }
        """,
    )

    result = graphql_sync(schema, '{ hello(firstName: "Bob") }')

    assert not result.errors
    assert result.data == {"hello": "Hello Bob!"}


def test_object_type_field_resolver_instance_arg_with_custom_name(assert_schema_equals):
    class QueryType(GraphQLObject):
        hello: str

        @GraphQLObject.resolver(
            "hello", args={"first_name": GraphQLObject.argument(name="name")}
        )
        def resolve_hello(*_, first_name: str) -> str:
            return f"Hello {first_name}!"

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          hello(name: String!): String!
        }
        """,
    )

    result = graphql_sync(schema, '{ hello(name: "Bob") }')

    assert not result.errors
    assert result.data == {"hello": "Hello Bob!"}


def test_object_type_field_instance_arg_with_custom_name(assert_schema_equals):
    class QueryType(GraphQLObject):
        @GraphQLObject.field(args={"first_name": GraphQLObject.argument(name="name")})
        def hello(*_, first_name: str) -> str:
            return f"Hello {first_name}!"

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          hello(name: String!): String!
        }
        """,
    )

    result = graphql_sync(schema, '{ hello(name: "Bob") }')

    assert not result.errors
    assert result.data == {"hello": "Hello Bob!"}
