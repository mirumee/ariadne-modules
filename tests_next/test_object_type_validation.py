import pytest

from ariadne_graphql_modules import gql
from ariadne_graphql_modules.next import GraphQLObject


def test_scalar_type_validation_fails_for_invalid_type_schema(snapshot):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLObject):
            __schema__ = gql("scalar Custom")

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
