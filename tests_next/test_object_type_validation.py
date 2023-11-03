import pytest

from ariadne_graphql_modules import gql
from ariadne_graphql_modules.next import GraphQLObject


def test_object_type_validation_fails_for_invalid_type_schema(snapshot):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLObject):
            __schema__ = gql("scalar Custom")

    snapshot.assert_match(str(exc_info.value))


def test_object_type_validation_fails_for_names_not_matching(snapshot):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLObject):
            __graphql_name__ = "Lorem"
            __schema__ = gql(
                """
                type Custom {
                    hello: String
                }
                """
            )

    snapshot.assert_match(str(exc_info.value))


def test_object_type_validation_fails_for_two_descriptions(snapshot):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLObject):
            __description__ = "Hello world!"
            __schema__ = gql(
                """
                \"\"\"Other description\"\"\"
                type Query {
                  hello: String!
                }
                """
            )

    snapshot.assert_match(str(exc_info.value))


def test_object_type_validation_fails_for_schema_missing_fields(snapshot):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLObject):
            __schema__ = gql("type Custom")

    snapshot.assert_match(str(exc_info.value))


def test_object_type_validation_fails_for_undefined_attr_resolver(snapshot):
    with pytest.raises(ValueError) as exc_info:

        class QueryType(GraphQLObject):
            hello: str

            @GraphQLObject.resolver("other")
            def resolve_hello(*_):
                return "Hello World!"

    snapshot.assert_match(str(exc_info.value))


def test_object_type_validation_fails_for_undefined_field_resolver(snapshot):
    with pytest.raises(ValueError) as exc_info:

        class QueryType(GraphQLObject):
            __schema__ = gql(
                """
                type Query {
                  hello: String!
                }
                """
            )

            @GraphQLObject.resolver("other")
            def resolve_hello(*_):
                return "Hello World!"

    snapshot.assert_match(str(exc_info.value))


def test_object_type_validation_fails_for_multiple_attrs_with_same_graphql_name(
    snapshot,
):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLObject):
            user_id: str
            user__id: str

    snapshot.assert_match(str(exc_info.value))


def test_object_type_validation_fails_for_attr_and_field_with_same_graphql_name(
    snapshot,
):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLObject):
            user_id: str

            @GraphQLObject.field(name="userId")
            def lorem(*_) -> str:
                return "Hello World!"

    snapshot.assert_match(str(exc_info.value))


def test_object_type_validation_fails_for_multiple_fields_with_same_graphql_name(
    snapshot,
):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLObject):
            @GraphQLObject.field(name="hello")
            def lorem(*_) -> str:
                return "Hello World!"

            @GraphQLObject.field(name="hello")
            def ipsum(*_) -> str:
                return "Hello World!"

    snapshot.assert_match(str(exc_info.value))


def test_object_type_validation_fails_for_undefined_field_resolver_arg(snapshot):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLObject):
            @GraphQLObject.field(args={"invalid": GraphQLObject.argument(name="test")})
            def hello(*_) -> str:
                return "Hello World!"

    snapshot.assert_match(str(exc_info.value))


def test_object_type_validation_fails_for_undefined_resolver_arg(snapshot):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLObject):
            hello: str

            @GraphQLObject.resolver(
                "hello", args={"invalid": GraphQLObject.argument(name="test")}
            )
            def resolve_hello(*_):
                return "Hello World!"

    snapshot.assert_match(str(exc_info.value))


def test_object_type_validation_fails_for_missing_field_resolver_arg(snapshot):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLObject):
            @GraphQLObject.field(args={"invalid": GraphQLObject.argument(name="test")})
            def hello(*_, name: str) -> str:
                return "Hello World!"

    snapshot.assert_match(str(exc_info.value))


def test_object_type_validation_fails_for_missing_resolver_arg(snapshot):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLObject):
            hello: str

            @GraphQLObject.resolver(
                "hello", args={"invalid": GraphQLObject.argument(name="test")}
            )
            def resolve_hello(*_, name: str):
                return "Hello World!"

    snapshot.assert_match(str(exc_info.value))


def test_object_type_validation_fails_for_multiple_field_resolvers(snapshot):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLObject):
            hello: str

            @GraphQLObject.resolver("hello")
            def resolve_hello(*_):
                return "Hello World!"

            @GraphQLObject.resolver("hello")
            def resolve_hello_other(*_):
                return "Hello World!"

    snapshot.assert_match(str(exc_info.value))


def test_object_type_validation_fails_for_multiple_schema_field_resolvers(snapshot):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLObject):
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

            @GraphQLObject.resolver("hello")
            def resolve_hello_other(*_):
                return "Hello World!"

    snapshot.assert_match(str(exc_info.value))


def test_object_type_validation_fails_for_field_with_multiple_descriptions(
    snapshot,
):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLObject):
            hello: str = GraphQLObject.field(description="Description")

            @GraphQLObject.resolver("hello", description="Other")
            def ipsum(*_) -> str:
                return "Hello World!"

    snapshot.assert_match(str(exc_info.value))


def test_object_type_validation_fails_for_schema_field_with_multiple_descriptions(
    snapshot,
):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLObject):
            __schema__ = """
                type Custom {
                    \"\"\"Description\"\"\"
                    hello: String!
                }
                """

            @GraphQLObject.resolver("hello", description="Other")
            def ipsum(*_) -> str:
                return "Hello World!"

    snapshot.assert_match(str(exc_info.value))


def test_object_type_validation_fails_for_schema_field_with_invalid_arg_name(
    snapshot,
):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLObject):
            __schema__ = """
                type Custom {
                    hello(name: String!): String!
                }
                """

            @GraphQLObject.resolver(
                "hello", args={"other": GraphQLObject.argument(description="Ok")}
            )
            def ipsum(*_, name: str) -> str:
                return "Hello World!"

    snapshot.assert_match(str(exc_info.value))


def test_object_type_validation_fails_for_schema_field_with_arg_name(
    snapshot,
):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLObject):
            __schema__ = """
                type Custom {
                    hello(name: String!): String!
                }
                """

            @GraphQLObject.resolver(
                "hello", args={"name": GraphQLObject.argument(name="Other")}
            )
            def ipsum(*_, name: str) -> str:
                return "Hello World!"

    snapshot.assert_match(str(exc_info.value))


def test_object_type_validation_fails_for_schema_field_with_arg_type(
    snapshot,
):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLObject):
            __schema__ = """
                type Custom {
                    hello(name: String!): String!
                }
                """

            @GraphQLObject.resolver(
                "hello", args={"name": GraphQLObject.argument(type=str)}
            )
            def ipsum(*_, name: str) -> str:
                return "Hello World!"

    snapshot.assert_match(str(exc_info.value))


def test_object_type_validation_fails_for_schema_field_with_arg_double_description(
    snapshot,
):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLObject):
            __schema__ = """
                type Custom {
                    hello(
                      \"\"\"Description\"\"\"
                      name: String!
                    ): String!
                }
                """

            @GraphQLObject.resolver(
                "hello", args={"name": GraphQLObject.argument(description="Other")}
            )
            def ipsum(*_, name: str) -> str:
                return "Hello World!"

    snapshot.assert_match(str(exc_info.value))


def test_object_type_validation_fails_for_field_with_multiple_args(
    snapshot,
):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLObject):
            @GraphQLObject.field(name="hello", args={""})
            def lorem(*_, a: int) -> str:
                return "Hello World!"

            @GraphQLObject.resolver("lorem", description="Other")
            def ipsum(*_) -> str:
                return "Hello World!"

    snapshot.assert_match(str(exc_info.value))


def test_object_type_validation_fails_for_invalid_alias(snapshot):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLObject):
            hello: str

            __aliases__ = {
                "invalid": "ok",
            }

    snapshot.assert_match(str(exc_info.value))


def test_object_type_validation_fails_for_invalid_schema_alias(snapshot):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLObject):
            __schema__ = gql(
                """
                type Query {
                  hello: String!
                }
                """
            )

            __aliases__ = {
                "invalid": "ok",
            }

    snapshot.assert_match(str(exc_info.value))


def test_object_type_validation_fails_for_resolver_alias(snapshot):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLObject):
            hello: str

            __aliases__ = {
                "hello": "ok",
            }

            @GraphQLObject.resolver("hello")
            def resolve_hello(*_):
                return "Hello World!"

    snapshot.assert_match(str(exc_info.value))


def test_object_type_validation_fails_for_schema_resolver_alias(snapshot):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLObject):
            __schema__ = gql(
                """
                type Query {
                  hello: String!
                }
                """
            )

            __aliases__ = {
                "hello": "ok",
            }

            @GraphQLObject.resolver("hello")
            def resolve_hello(*_):
                return "Hello World!"

    snapshot.assert_match(str(exc_info.value))


def test_object_type_validation_fails_for_schema_with_field_instance(snapshot):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLObject):
            __schema__ = gql(
                """
                type Query {
                  hello: String!
                }
                """
            )

            hello = GraphQLObject.field(lambda *_: "noop")

    snapshot.assert_match(str(exc_info.value))


class InvalidType:
    pass


def test_object_type_validation_fails_for_unsupported_resolver_arg_default(snapshot):
    with pytest.raises(TypeError) as exc_info:

        class QueryType(GraphQLObject):
            @GraphQLObject.field
            def hello(*_, name: str = InvalidType):
                return "Hello World!"

    snapshot.assert_match(str(exc_info.value))


def test_object_type_validation_fails_for_unsupported_resolver_arg_default_option(
    snapshot,
):
    with pytest.raises(TypeError) as exc_info:

        class QueryType(GraphQLObject):
            @GraphQLObject.field(
                args={"name": GraphQLObject.argument(default_value=InvalidType)}
            )
            def hello(*_, name: str):
                return "Hello World!"

    snapshot.assert_match(str(exc_info.value))


def test_object_type_validation_fails_for_unsupported_schema_resolver_arg_default(
    snapshot,
):
    with pytest.raises(TypeError) as exc_info:

        class QueryType(GraphQLObject):
            __schema__ = gql(
                """
                type Query {
                  hello: String!
                }
                """
            )

            @GraphQLObject.resolver("hello")
            def resolve_hello(*_, name: str = InvalidType):
                return "Hello World!"

    snapshot.assert_match(str(exc_info.value))


def test_object_type_validation_fails_for_unsupported_schema_resolver_arg_option_default(
    snapshot,
):
    with pytest.raises(TypeError) as exc_info:

        class QueryType(GraphQLObject):
            __schema__ = gql(
                """
                type Query {
                  hello(name: String!): String!
                }
                """
            )

            @GraphQLObject.resolver(
                "hello",
                args={"name": GraphQLObject.argument(default_value=InvalidType)},
            )
            def resolve_hello(*_, name: str):
                return "Hello World!"

    snapshot.assert_match(str(exc_info.value))
