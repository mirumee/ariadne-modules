# pylint: disable=unused-variable
import pytest
from ariadne import gql

from ariadne_graphql_modules import GraphQLObject


def test_schema_object_type_validation_fails_for_invalid_type_schema(data_regression):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLObject):
            __schema__ = gql("scalar Custom")

    data_regression.check(str(exc_info.value))


def test_schema_object_type_validation_fails_for_names_not_matching(data_regression):
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

    data_regression.check(str(exc_info.value))


def test_schema_object_type_validation_fails_for_two_descriptions(data_regression):
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

    data_regression.check(str(exc_info.value))


def test_schema_object_type_validation_fails_for_missing_fields(data_regression):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLObject):
            __schema__ = gql("type Custom")

    data_regression.check(str(exc_info.value))


def test_object_type_validation_fails_for_undefined_attr_resolver(data_regression):
    with pytest.raises(ValueError) as exc_info:

        class QueryType(GraphQLObject):
            hello: str

            @GraphQLObject.resolver("other")
            @staticmethod
            def resolve_hello(*_):
                return "Hello World!"

    data_regression.check(str(exc_info.value))


def test_schema_object_type_validation_fails_for_undefined_field_resolver(
    data_regression,
):
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
            @staticmethod
            def resolve_hello(*_):
                return "Hello World!"

    data_regression.check(str(exc_info.value))


def test_object_type_validation_fails_for_multiple_attrs_with_same_graphql_name(
    data_regression,
):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLObject):
            user_id: str
            user__id: str

    data_regression.check(str(exc_info.value))


def test_object_type_validation_fails_for_attr_and_field_with_same_graphql_name(
    data_regression,
):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLObject):
            user_id: str

            @GraphQLObject.field(name="userId")
            @staticmethod
            def lorem(*_) -> str:
                return "Hello World!"

    data_regression.check(str(exc_info.value))


def test_object_type_validation_fails_for_multiple_fields_with_same_graphql_name(
    data_regression,
):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLObject):
            @GraphQLObject.field(name="hello")
            @staticmethod
            def lorem(*_) -> str:
                return "Hello World!"

            @GraphQLObject.field(name="hello")
            @staticmethod
            def ipsum(*_) -> str:
                return "Hello World!"

    data_regression.check(str(exc_info.value))


def test_object_type_validation_fails_for_undefined_field_resolver_arg(data_regression):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLObject):
            @GraphQLObject.field(args={"invalid": GraphQLObject.argument(name="test")})
            @staticmethod
            def hello(*_) -> str:
                return "Hello World!"

    data_regression.check(str(exc_info.value))


def test_object_type_validation_fails_for_undefined_resolver_arg(data_regression):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLObject):
            hello: str

            @GraphQLObject.resolver(
                "hello", args={"invalid": GraphQLObject.argument(name="test")}
            )
            @staticmethod
            def resolve_hello(*_):
                return "Hello World!"

    data_regression.check(str(exc_info.value))


def test_object_type_validation_fails_for_missing_field_resolver_arg(data_regression):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLObject):
            @GraphQLObject.field(args={"invalid": GraphQLObject.argument(name="test")})
            @staticmethod
            def hello(*_, name: str) -> str:
                return f"Hello {name}!"

    data_regression.check(str(exc_info.value))


def test_object_type_validation_fails_for_missing_resolver_arg(data_regression):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLObject):
            hello: str

            @GraphQLObject.resolver(
                "hello", args={"invalid": GraphQLObject.argument(name="test")}
            )
            @staticmethod
            def resolve_hello(*_, name: str):
                return f"Hello {name}!"

    data_regression.check(str(exc_info.value))


def test_object_type_validation_fails_for_multiple_field_resolvers(data_regression):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLObject):
            hello: str

            @GraphQLObject.resolver("hello")
            @staticmethod
            def resolve_hello(*_):
                return "Hello World!"

            @GraphQLObject.resolver("hello")
            @staticmethod
            def resolve_hello_other(*_):
                return "Hello World!"

    data_regression.check(str(exc_info.value))


def test_schema_object_type_validation_fails_for_multiple_field_resolvers(
    data_regression,
):
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
            @staticmethod
            def resolve_hello(*_):
                return "Hello World!"

            @GraphQLObject.resolver("hello")
            @staticmethod
            def resolve_hello_other(*_):
                return "Hello World!"

    data_regression.check(str(exc_info.value))


def test_object_type_validation_fails_for_field_with_multiple_descriptions(
    data_regression,
):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLObject):
            hello: str = GraphQLObject.field(description="Description")

            @GraphQLObject.resolver("hello", description="Other")
            @staticmethod
            def ipsum(*_) -> str:
                return "Hello World!"

    data_regression.check(str(exc_info.value))


def test_schema_object_type_validation_fails_for_field_with_multiple_descriptions(
    data_regression,
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
            @staticmethod
            def ipsum(*_) -> str:
                return "Hello World!"

    data_regression.check(str(exc_info.value))


def test_schema_object_type_validation_fails_for_field_with_invalid_arg_name(
    data_regression,
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
            @staticmethod
            def ipsum(*_, name: str) -> str:
                return f"Hello {name}!"

    data_regression.check(str(exc_info.value))


def test_schema_object_type_validation_fails_for_arg_with_name_option(
    data_regression,
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
            @staticmethod
            def ipsum(*_, name: str) -> str:
                return f"Hello {name}!"

    data_regression.check(str(exc_info.value))


def test_schema_object_type_validation_fails_for_arg_with_type_option(
    data_regression,
):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLObject):
            __schema__ = """
                type Custom {
                    hello(name: String!): String!
                }
                """

            @GraphQLObject.resolver(
                "hello", args={"name": GraphQLObject.argument(graphql_type=str)}
            )
            @staticmethod
            def ipsum(*_, name: str) -> str:
                return f"Hello {name}!"

    data_regression.check(str(exc_info.value))


def test_schema_object_type_validation_fails_for_arg_with_double_description(
    data_regression,
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
            @staticmethod
            def ipsum(*_, name: str) -> str:
                return f"Hello {name}!"

    data_regression.check(str(exc_info.value))


def test_object_type_validation_fails_for_field_with_multiple_args(
    data_regression,
):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLObject):
            @GraphQLObject.field(name="hello", args={""})  # type: ignore
            @staticmethod
            def lorem(*_, a: int) -> str:
                return f"Hello {a}!"

            @GraphQLObject.resolver("lorem", description="Other")
            @staticmethod
            def ipsum(*_) -> str:
                return "Hello World!"

    data_regression.check(str(exc_info.value))


def test_object_type_validation_fails_for_invalid_alias(data_regression):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLObject):
            hello: str

            __aliases__ = {
                "invalid": "target",
            }

    data_regression.check(str(exc_info.value))


def test_schema_object_type_validation_fails_for_invalid_alias(data_regression):
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
                "invalid": "welcome",
            }

    data_regression.check(str(exc_info.value))


def test_object_type_validation_fails_for_alias_resolver(data_regression):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLObject):
            hello: str

            __aliases__ = {
                "hello": "welcome",
            }

            @GraphQLObject.resolver("hello")
            @staticmethod
            def resolve_hello(*_):
                return "Hello World!"

    data_regression.check(str(exc_info.value))


def test_object_type_validation_fails_for_alias_target_resolver(data_regression):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLObject):
            hello: str
            welcome: str

            __aliases__ = {
                "hello": "welcome",
            }

            @GraphQLObject.resolver("welcome")
            @staticmethod
            def resolve_welcome(*_):
                return "Hello World!"

    data_regression.check(str(exc_info.value))


def test_schema_object_type_validation_fails_for_alias_resolver(data_regression):
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
            @staticmethod
            def resolve_hello(*_):
                return "Hello World!"

    data_regression.check(str(exc_info.value))


def test_schema_object_type_validation_fails_for_alias_target_resolver(data_regression):
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

            ok: str

            @GraphQLObject.resolver("ok")
            @staticmethod
            def resolve_hello(*_):
                return "Hello World!"

    data_regression.check(str(exc_info.value))


def test_schema_object_type_validation_fails_for_field_instance(data_regression):
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

    data_regression.check(str(exc_info.value))


class InvalidType:
    pass


def test_object_type_validation_fails_for_unsupported_resolver_arg_default(
    data_regression,
):
    with pytest.raises(TypeError) as exc_info:

        class QueryType(GraphQLObject):
            @GraphQLObject.field
            @staticmethod
            def hello(*_, name: str = InvalidType):  # type: ignore
                return f"Hello {name}!"

    data_regression.check(str(exc_info.value))


def test_object_type_validation_fails_for_unsupported_resolver_arg_default_option(
    data_regression,
):
    with pytest.raises(TypeError) as exc_info:

        class QueryType(GraphQLObject):
            @GraphQLObject.field(
                args={"name": GraphQLObject.argument(default_value=InvalidType)}
            )
            @staticmethod
            def hello(*_, name: str):
                return f"Hello {name}!"

    data_regression.check(str(exc_info.value))


def test_schema_object_type_validation_fails_for_unsupported_resolver_arg_default(
    data_regression,
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
            @staticmethod
            def resolve_hello(*_, name: str = InvalidType):  # type: ignore
                return f"Hello {name}!"

    data_regression.check(str(exc_info.value))


def test_invalid_resolver_arg_option_default(
    data_regression,
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
            @staticmethod
            def resolve_hello(*_, name: str):
                return f"Hello {name}!"

    data_regression.check(str(exc_info.value))
