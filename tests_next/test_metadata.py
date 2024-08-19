from enum import Enum

import pytest

from ariadne_graphql_modules.next import GraphQLObject, graphql_enum


class QueryType(GraphQLObject):
    hello: str


def test_metadata_returns_sets_and_returns_data_for_type(metadata):
    assert metadata.set_data(QueryType, 42) == 42
    assert metadata.get_data(QueryType) == 42


def test_metadata_raises_key_error_for_unset_data(data_regression, metadata):
    with pytest.raises(KeyError) as exc_info:
        metadata.get_data(QueryType)

    data_regression.check(str(exc_info.value))


def test_metadata_returns_model_for_type(assert_ast_equals, metadata):
    model = metadata.get_graphql_model(QueryType)
    assert model.name == "Query"

    assert_ast_equals(
        model.ast,
        (
            """
            type Query {
              hello: String!
            }
            """
        ),
    )


def test_metadata_returns_graphql_name_for_type(assert_ast_equals, metadata):
    assert metadata.get_graphql_name(QueryType) == "Query"


class UserLevel(Enum):
    GUEST = 0
    MEMBER = 1
    MODERATOR = 2
    ADMINISTRATOR = 3


def test_metadata_returns_model_for_standard_enum(assert_ast_equals, metadata):
    model = metadata.get_graphql_model(UserLevel)
    assert model.name == "UserLevel"

    assert_ast_equals(
        model.ast,
        (
            """
            enum UserLevel {
              GUEST
              MEMBER
              MODERATOR
              ADMINISTRATOR
            }
            """
        ),
    )


def test_metadata_returns_graphql_name_for_standard_enum(assert_ast_equals, metadata):
    assert metadata.get_graphql_name(UserLevel) == "UserLevel"


@graphql_enum(name="SeverityEnum")
class SeverityLevel(Enum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2


def test_metadata_returns_model_for_annotated_enum(assert_ast_equals, metadata):
    model = metadata.get_graphql_model(SeverityLevel)
    assert model.name == "SeverityEnum"

    assert_ast_equals(
        model.ast,
        (
            """
            enum SeverityEnum {
              LOW
              MEDIUM
              HIGH
            }
            """
        ),
    )


def test_metadata_returns_graphql_name_for_annotated_enum(assert_ast_equals, metadata):
    assert metadata.get_graphql_name(SeverityLevel) == "SeverityEnum"
