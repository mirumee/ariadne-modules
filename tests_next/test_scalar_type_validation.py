import pytest

from ariadne_graphql_modules import gql
from ariadne_graphql_modules.next import GraphQLScalar


def test_schema_scalar_type_validation_fails_for_invalid_type_schema(snapshot):
    with pytest.raises(ValueError) as exc_info:

        class CustomScalar(GraphQLScalar[str]):
            __schema__ = gql("type Custom")

    snapshot.assert_match(str(exc_info.value))


def test_schema_scalar_type_validation_fails_for_different_names(
    snapshot,
):
    with pytest.raises(ValueError) as exc_info:

        class CustomScalar(GraphQLScalar[str]):
            __graphql_name__ = "Date"
            __schema__ = gql("scalar Custom")

    snapshot.assert_match(str(exc_info.value))


def test_schema_scalar_type_validation_fails_for_two_descriptions(snapshot):
    with pytest.raises(ValueError) as exc_info:

        class CustomScalar(GraphQLScalar[str]):
            __description__ = "Hello world!"
            __schema__ = gql(
                """
                \"\"\"Other description\"\"\"
                scalar Lorem
                """
            )

    snapshot.assert_match(str(exc_info.value))
