from enum import Enum

import pytest

from ariadne_graphql_modules import gql
from ariadne_graphql_modules.next import GraphQLEnum


def test_schema_enum_type_validation_fails_for_invalid_type_schema(data_regression):
    with pytest.raises(ValueError) as exc_info:

        class UserLevel(GraphQLEnum):
            __schema__ = gql("scalar Custom")

    data_regression.check(str(exc_info.value))


def test_schema_enum_type_validation_fails_for_names_not_matching(
    data_regression,
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

    data_regression.check(str(exc_info.value))


def test_schema_enum_type_validation_fails_for_empty_enum(data_regression):
    with pytest.raises(ValueError) as exc_info:

        class UserLevel(GraphQLEnum):
            __schema__ = gql("enum UserLevel")

    data_regression.check(str(exc_info.value))


def test_schema_enum_type_validation_fails_for_two_descriptions(data_regression):
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

    data_regression.check(str(exc_info.value))


def test_schema_enum_type_validation_fails_for_schema_and_members_list(data_regression):
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

    data_regression.check(str(exc_info.value))


def test_schema_enum_type_validation_fails_for_schema_and_members_dict_mismatch(
    data_regression,
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

    data_regression.check(str(exc_info.value))


def test_schema_enum_type_validation_fails_for_schema_and_members_enum_mismatch(
    data_regression,
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

    data_regression.check(str(exc_info.value))


def test_schema_enum_type_validation_fails_for_duplicated_members_descriptions(
    data_regression,
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

    data_regression.check(str(exc_info.value))


def test_schema_enum_type_validation_fails_for_invalid_members_descriptions(data_regression):
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

    data_regression.check(str(exc_info.value))


def test_enum_type_validation_fails_for_missing_members(data_regression):
    with pytest.raises(ValueError) as exc_info:

        class UserLevel(GraphQLEnum):
            pass

    data_regression.check(str(exc_info.value))


def test_enum_type_validation_fails_for_invalid_members(data_regression):
    with pytest.raises(ValueError) as exc_info:

        class UserLevel(GraphQLEnum):
            __members__ = "INVALID"

    data_regression.check(str(exc_info.value))
