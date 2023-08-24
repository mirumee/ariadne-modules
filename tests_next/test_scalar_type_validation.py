import pytest

from ariadne_graphql_modules import gql
from ariadne_graphql_modules.next import GraphQLScalar


def test_scalar_type_validation_fails_for_invalid_type_schema(snapshot):
    with pytest.raises(ValueError) as exc_info:

        class CustomScalar(GraphQLScalar[str]):
            __schema__ = gql("type Custom")

    snapshot.assert_match(str(exc_info.value))


def test_scalar_type_validation_fails_for_name_mismatch_between_schema_and_attr(
    snapshot,
):
    with pytest.raises(ValueError) as exc_info:

        class CustomScalar(GraphQLScalar[str]):
            __graphql_name__ = "Date"
            __schema__ = gql("scalar Custom")

    snapshot.assert_match(str(exc_info.value))
