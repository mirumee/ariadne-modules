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
