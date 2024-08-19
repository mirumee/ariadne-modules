import pytest

from ariadne_graphql_modules import gql
from ariadne_graphql_modules.next import GraphQLInput


def test_schema_input_type_validation_fails_for_invalid_type_schema(data_regression):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLInput):
            __schema__ = gql("scalar Custom")

    data_regression.check(str(exc_info.value))


def test_schema_input_type_validation_fails_for_names_not_matching(data_regression):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLInput):
            __graphql_name__ = "Lorem"
            __schema__ = gql(
                """
                input Custom {
                    hello: String!
                }
                """
            )

    data_regression.check(str(exc_info.value))


def test_schema_input_type_validation_fails_for_two_descriptions(data_regression):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLInput):
            __description__ = "Hello world!"
            __schema__ = gql(
                """
                \"\"\"Other description\"\"\"
                input Custom {
                  hello: String!
                }
                """
            )

    data_regression.check(str(exc_info.value))


def test_schema_input_type_validation_fails_for_schema_missing_fields(data_regression):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLInput):
            __schema__ = gql("input Custom")

    data_regression.check(str(exc_info.value))


def test_input_type_validation_fails_for_out_names_without_schema(data_regression):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLInput):
            hello: str

            __out_names__ = {
                "hello": "ok",
            }

    data_regression.check(str(exc_info.value))


def test_schema_input_type_validation_fails_for_invalid_out_name(data_regression):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLInput):
            __schema__ = gql(
                """
                input Query {
                  hello: String!
                }
                """
            )

            __out_names__ = {
                "invalid": "ok",
            }

    data_regression.check(str(exc_info.value))


def test_schema_input_type_validation_fails_for_duplicate_out_name(data_regression):
    with pytest.raises(ValueError) as exc_info:

        class CustomType(GraphQLInput):
            __schema__ = gql(
                """
                input Query {
                  hello: String!
                  name: String!
                }
                """
            )

            __out_names__ = {
                "hello": "ok",
                "name": "ok",
            }

    data_regression.check(str(exc_info.value))


class InvalidType:
    pass


def test_input_type_validation_fails_for_unsupported_attr_default(data_regression):
    with pytest.raises(TypeError) as exc_info:

        class QueryType(GraphQLInput):
            attr: str = InvalidType()

    data_regression.check(str(exc_info.value))


def test_input_type_validation_fails_for_unsupported_field_default_option(
    data_regression,
):
    with pytest.raises(TypeError) as exc_info:

        class QueryType(GraphQLInput):
            attr: str = GraphQLInput.field(default_value=InvalidType())

    data_regression.check(str(exc_info.value))
