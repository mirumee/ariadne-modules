from graphql import graphql_sync

from ariadne_graphql_modules import gql
from ariadne_graphql_modules.next import GraphQLObject, make_executable_schema


def test_object_type_with_field(assert_schema_equals):
    class QueryType(GraphQLObject):
        hello: str

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


def test_object_type_with_alias(assert_schema_equals):
    class QueryType(GraphQLObject):
        __aliases__ = {"hello": "welcome"}

        hello: str

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          hello: String!
        }
        """,
    )

    result = graphql_sync(schema, "{ hello }", root_value={"welcome": "Hello World!"})

    assert not result.errors
    assert result.data == {"hello": "Hello World!"}


def test_object_type_with_field_resolver(assert_schema_equals):
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


def test_object_type_with_typed_field_instance(assert_schema_equals):
    class QueryType(GraphQLObject):
        hello = GraphQLObject.field(lambda *_: "Hello World!", type=str)

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


def test_object_type_with_annotated_field_instance(assert_schema_equals):
    class QueryType(GraphQLObject):
        hello: str = GraphQLObject.field(lambda *_: "Hello World!")

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


def test_object_type_with_typed_field_and_field_resolver(assert_schema_equals):
    class QueryType(GraphQLObject):
        name: str

        @GraphQLObject.field
        def hello(obj, info) -> str:
            return "Hello World!"

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          name: String!
          hello: String!
        }
        """,
    )

    result = graphql_sync(schema, "{ name hello }", root_value={"name": "Ok"})

    assert not result.errors
    assert result.data == {"name": "Ok", "hello": "Hello World!"}


def test_object_type_with_schema(assert_schema_equals):
    class QueryType(GraphQLObject):
        __schema__ = gql(
            """
            type Query {
              hello: String!
            }
            """
        )

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


def test_object_type_with_nested_types(assert_schema_equals):
    class UserType(GraphQLObject):
        name: str

    class PostType(GraphQLObject):
        message: str

    class QueryType(GraphQLObject):
        user: UserType

        @GraphQLObject.field(type=PostType)
        def post(obj, info):
            return {"message": "test"}

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          user: User!
          post: Post!
        }

        type User {
          name: String!
        }

        type Post {
          message: String!
        }
        """,
    )

    result = graphql_sync(
        schema,
        "{ user { name } post { message } }",
        root_value={"user": {"name": "Bob"}},
    )

    assert not result.errors
    assert result.data == {
        "user": {
            "name": "Bob",
        },
        "post": {"message": "test"},
    }


def test_resolver_decorator_sets_resolver_for_type_hint_field(assert_schema_equals):
    class QueryType(GraphQLObject):
        hello: str

        @GraphQLObject.resolver("hello")
        def resolve_hello(*_):
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


def test_resolver_decorator_sets_resolver_for_instance_field(assert_schema_equals):
    class QueryType(GraphQLObject):
        hello: str = GraphQLObject.field(name="hello")

        @GraphQLObject.resolver("hello")
        def resolve_hello(*_):
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


def test_resolver_decorator_sets_resolver_for_field_in_schema(assert_schema_equals):
    class QueryType(GraphQLObject):
        __schema__ = gql(
            """
            type Query {
              hello: String!
            }
            """
        )

        @GraphQLObject.resolver("hello")
        def resolve_hello(*_):
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


def test_object_type_with_description(assert_schema_equals):
    class QueryType(GraphQLObject):
        __description__ = "Lorem ipsum."

        hello: str

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        \"\"\"Lorem ipsum.\"\"\"
        type Query {
          hello: String!
        }
        """,
    )

    result = graphql_sync(schema, "{ hello }", root_value={"hello": "Hello World!"})

    assert not result.errors
    assert result.data == {"hello": "Hello World!"}


def test_field_decorator_sets_description_for_field(assert_schema_equals):
    class QueryType(GraphQLObject):
        @GraphQLObject.field(description="Lorem ipsum.")
        def hello(obj, info) -> str:
            return "Hello World!"

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          \"\"\"Lorem ipsum.\"\"\"
          hello: String!
        }
        """,
    )

    result = graphql_sync(schema, "{ hello }")

    assert not result.errors
    assert result.data == {"hello": "Hello World!"}


def test_field_decorator_sets_description_for_field_arg(assert_schema_equals):
    class QueryType(GraphQLObject):
        @GraphQLObject.field(
            args={"name": GraphQLObject.argument(description="Lorem ipsum.")}
        )
        def hello(obj, info, name: str) -> str:
            return f"Hello {name}!"

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          hello(
            \"\"\"Lorem ipsum.\"\"\"
            name: String!
          ): String!
        }
        """,
    )

    result = graphql_sync(schema, '{ hello(name: "Bob") }')

    assert not result.errors
    assert result.data == {"hello": "Hello Bob!"}


def test_resolver_decorator_sets_description_for_type_hint_field(assert_schema_equals):
    class QueryType(GraphQLObject):
        hello: str

        @GraphQLObject.resolver("hello", description="Lorem ipsum.")
        def resolve_hello(*_):
            return "Hello World!"

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          \"\"\"Lorem ipsum.\"\"\"
          hello: String!
        }
        """,
    )

    result = graphql_sync(schema, "{ hello }")

    assert not result.errors
    assert result.data == {"hello": "Hello World!"}


def test_resolver_decorator_sets_description_for_field_in_schema(assert_schema_equals):
    class QueryType(GraphQLObject):
        __schema__ = gql(
            """
            type Query {
              hello: String!
            }
            """
        )

        @GraphQLObject.resolver("hello", description="Lorem ipsum.")
        def resolve_hello(*_):
            return "Hello World!"

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          \"\"\"Lorem ipsum.\"\"\"
          hello: String!
        }
        """,
    )

    result = graphql_sync(schema, "{ hello }")

    assert not result.errors
    assert result.data == {"hello": "Hello World!"}


def test_resolver_decorator_sets_description_for_field_arg(assert_schema_equals):
    class QueryType(GraphQLObject):
        hello: str

        @GraphQLObject.resolver(
            "hello", args={"name": GraphQLObject.argument(description="Lorem ipsum.")}
        )
        def resolve_hello(obj, info, name: str) -> str:
            return f"Hello {name}!"

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          hello(
            \"\"\"Lorem ipsum.\"\"\"
            name: String!
          ): String!
        }
        """,
    )

    result = graphql_sync(schema, '{ hello(name: "Bob") }')

    assert not result.errors
    assert result.data == {"hello": "Hello Bob!"}


def test_schema_sets_description_for_field_arg(assert_schema_equals):
    class QueryType(GraphQLObject):
        __schema__ = gql(
            """
            type Query {
              hello(
                \"\"\"Lorem ipsum.\"\"\"
                name: String!
              ): String!
            }
            """
        )

        @GraphQLObject.resolver("hello")
        def resolve_hello(*_, name: str):
            return f"Hello {name}!"

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          hello(
            \"\"\"Lorem ipsum.\"\"\"
            name: String!
          ): String!
        }
        """,
    )

    result = graphql_sync(schema, '{ hello(name: "Bob") }')

    assert not result.errors
    assert result.data == {"hello": "Hello Bob!"}


def test_resolver_decorator_sets_description_for_field_arg_in_schema(
    assert_schema_equals,
):
    class QueryType(GraphQLObject):
        __schema__ = gql(
            """
            type Query {
              hello(name: String!): String!
            }
            """
        )

        @GraphQLObject.resolver(
            "hello", args={"name": GraphQLObject.argument(description="Description")}
        )
        def resolve_hello(*_, name: str):
            return f"Hello {name}!"

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          hello(
            \"\"\"Description\"\"\"
            name: String!
          ): String!
        }
        """,
    )

    result = graphql_sync(schema, '{ hello(name: "Bob") }')

    assert not result.errors
    assert result.data == {"hello": "Hello Bob!"}
