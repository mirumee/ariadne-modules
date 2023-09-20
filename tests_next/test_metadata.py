from enum import Enum

from ariadne_graphql_modules.next import GraphQLObject, graphql_enum


class QueryType(GraphQLObject):
    hello: str


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
