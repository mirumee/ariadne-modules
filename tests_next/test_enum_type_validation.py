from enum import Enum

import pytest

from ariadne_graphql_modules import gql
from ariadne_graphql_modules.next import GraphQLEnum


def test_schema_enum_type_validation_fails_for_invalid_type_schema(snapshot):
    with pytest.raises(ValueError) as exc_info:

        class UserLevel(GraphQLEnum):
            __schema__ = gql("scalar Custom")

    snapshot.assert_match(str(exc_info.value))


def test_schema_enum_type_validation_fails_for_names_not_matching(
    snapshot,
):
    with pytest.raises(ValueError) as exc_info:

        class UserLevel(GraphQLEnum):
            __graphql_name__ = "UserRank"
            __schema__ = gql(
                """
                enum Custom {
                  GUEST
                  MEMBER
                }
                """
            )

    snapshot.assert_match(str(exc_info.value))


def test_schema_enum_type_validation_fails_for_empty_enum(snapshot):
    with pytest.raises(ValueError) as exc_info:

        class UserLevel(GraphQLEnum):
            __schema__ = gql("enum UserLevel")

    snapshot.assert_match(str(exc_info.value))


def test_schema_enum_type_validation_fails_for_two_descriptions(snapshot):
    with pytest.raises(ValueError) as exc_info:

        class UserLevel(GraphQLEnum):
            __description__ = "Hello world!"
            __schema__ = gql(
                """
                \"\"\"Other description\"\"\"
                enum Custom {
                  GUEST
                  MEMBER
                }
                """
            )

    snapshot.assert_match(str(exc_info.value))


def test_schema_enum_type_validation_fails_for_schema_and_members_list(snapshot):
    with pytest.raises(ValueError) as exc_info:

        class UserLevel(GraphQLEnum):
            __schema__ = gql(
                """
                enum Custom {
                  GUEST
                  MEMBER
                }
                """
            )
            __members__ = ["GUEST", "MEMBER"]

    snapshot.assert_match(str(exc_info.value))


def test_schema_enum_type_validation_fails_for_schema_and_members_dict_mismatch(
    snapshot,
):
    with pytest.raises(ValueError) as exc_info:

        class UserLevel(GraphQLEnum):
            __schema__ = gql(
                """
                enum Custom {
                  GUEST
                  MEMBER
                }
                """
            )
            __members__ = {
                "GUEST": 0,
                "MODERATOR": 1,
            }

    snapshot.assert_match(str(exc_info.value))


def test_schema_enum_type_validation_fails_for_schema_and_members_enum_mismatch(
    snapshot,
):
    with pytest.raises(ValueError) as exc_info:

        class UserLevelEnum(Enum):
            GUEST = 0
            MEMBER = 1
            ADMIN = 2

        class UserLevel(GraphQLEnum):
            __schema__ = gql(
                """
                enum Custom {
                  GUEST
                  MEMBER
                  MODERATOR
                }
                """
            )
            __members__ = UserLevelEnum

    snapshot.assert_match(str(exc_info.value))


def test_schema_enum_type_validation_fails_for_duplicated_members_descriptions(
    snapshot,
):
    with pytest.raises(ValueError) as exc_info:

        class UserLevel(GraphQLEnum):
            __schema__ = gql(
                """
                enum Custom {
                  GUEST
                  \"Lorem ipsum.\"
                  MEMBER
                }
                """
            )
            __members_descriptions__ = {"MEMBER": "Other description."}

    snapshot.assert_match(str(exc_info.value))


def test_schema_enum_type_validation_fails_for_invalid_members_descriptions(snapshot):
    with pytest.raises(ValueError) as exc_info:

        class UserLevel(GraphQLEnum):
            __schema__ = gql(
                """
                enum Custom {
                  GUEST
                  MEMBER
                }
                """
            )
            __members_descriptions__ = {"INVALID": "Other description."}

    snapshot.assert_match(str(exc_info.value))


def test_enum_type_validation_fails_for_missing_members(snapshot):
    with pytest.raises(ValueError) as exc_info:

        class UserLevel(GraphQLEnum):
            pass

    snapshot.assert_match(str(exc_info.value))


def test_enum_type_validation_fails_for_invalid_members(snapshot):
    with pytest.raises(ValueError) as exc_info:

        class UserLevel(GraphQLEnum):
            __members__ = "INVALID"

    snapshot.assert_match(str(exc_info.value))
