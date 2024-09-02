# pylint: disable=unused-variable
import pytest

from ariadne import gql
from ariadne_graphql_modules import GraphQLScalar


def test_schema_scalar_type_validation_fails_for_invalid_type_schema(data_regression):
    with pytest.raises(ValueError) as exc_info:

        class CustomScalar(GraphQLScalar[str]):
            __schema__ = gql("type Custom")

    data_regression.check(str(exc_info.value))


def test_schema_scalar_type_validation_fails_for_different_names(
    data_regression,
):
    with pytest.raises(ValueError) as exc_info:

        class CustomScalar(GraphQLScalar[str]):
            __graphql_name__ = "Date"
            __schema__ = gql("scalar Custom")

    data_regression.check(str(exc_info.value))


def test_schema_scalar_type_validation_fails_for_two_descriptions(data_regression):
    with pytest.raises(ValueError) as exc_info:

        class CustomScalar(GraphQLScalar[str]):
            __description__ = "Hello world!"
            __schema__ = gql(
                """
                \"\"\"Other description\"\"\"
                scalar Lorem
                """
            )

    data_regression.check(str(exc_info.value))
