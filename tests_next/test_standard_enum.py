from enum import Enum

import pytest
from graphql import graphql_sync

from ariadne_graphql_modules.next import (
    GraphQLObject,
    create_graphql_enum_model,
    graphql_enum,
    make_executable_schema,
)


class UserLevel(Enum):
    GUEST = 0
    MEMBER = 1
    MODERATOR = 2
    ADMINISTRATOR = 3


def test_graphql_enum_model_is_created_from_python_enum(assert_ast_equals):
    graphql_model = create_graphql_enum_model(UserLevel)

    assert graphql_model.name == "UserLevel"
    assert graphql_model.members == {
        "GUEST": UserLevel.GUEST,
        "MEMBER": UserLevel.MEMBER,
        "MODERATOR": UserLevel.MODERATOR,
        "ADMINISTRATOR": UserLevel.ADMINISTRATOR,
    }

    assert_ast_equals(
        graphql_model.ast,
        """
        enum UserLevel {
          GUEST
          MEMBER
          MODERATOR
          ADMINISTRATOR
        }
        """,
    )


def test_graphql_enum_model_is_created_with_custom_name():
    graphql_model = create_graphql_enum_model(UserLevel, name="CustomName")
    assert graphql_model.name == "CustomName"


def test_graphql_enum_model_is_created_with_method():
    class UserLevel(Enum):
        GUEST = 0
        MEMBER = 1
        MODERATOR = 2
        ADMINISTRATOR = 3

        @staticmethod
        def __get_graphql_model__():
            return "CustomModel"

    graphql_model = create_graphql_enum_model(UserLevel)
    assert graphql_model == "CustomModel"


def test_graphql_enum_model_is_created_with_name_from_method(assert_ast_equals):
    class UserLevel(Enum):
        GUEST = 0
        MEMBER = 1
        MODERATOR = 2
        ADMINISTRATOR = 3

        @staticmethod
        def __get_graphql_name__():
            return "CustomName"

    graphql_model = create_graphql_enum_model(UserLevel)
    assert graphql_model.name == "CustomName"


def test_graphql_enum_model_is_created_with_description(assert_ast_equals):
    graphql_model = create_graphql_enum_model(UserLevel, description="Test enum.")

    assert graphql_model.name == "UserLevel"
    assert graphql_model.members == {
        "GUEST": UserLevel.GUEST,
        "MEMBER": UserLevel.MEMBER,
        "MODERATOR": UserLevel.MODERATOR,
        "ADMINISTRATOR": UserLevel.ADMINISTRATOR,
    }

    assert_ast_equals(
        graphql_model.ast,
        """
        "Test enum."
        enum UserLevel {
          GUEST
          MEMBER
          MODERATOR
          ADMINISTRATOR
        }
        """,
    )


def test_graphql_enum_model_is_created_with_specified_members(assert_ast_equals):
    graphql_model = create_graphql_enum_model(
        UserLevel,
        members_include=["GUEST", "MODERATOR"],
    )

    assert graphql_model.name == "UserLevel"
    assert graphql_model.members == {
        "GUEST": UserLevel.GUEST,
        "MODERATOR": UserLevel.MODERATOR,
    }

    assert_ast_equals(
        graphql_model.ast,
        """
        enum UserLevel {
          GUEST
          MODERATOR
        }
        """,
    )


def test_graphql_enum_model_is_created_without_specified_members(assert_ast_equals):
    graphql_model = create_graphql_enum_model(
        UserLevel,
        members_exclude=["GUEST", "MODERATOR"],
    )

    assert graphql_model.name == "UserLevel"
    assert graphql_model.members == {
        "MEMBER": UserLevel.MEMBER,
        "ADMINISTRATOR": UserLevel.ADMINISTRATOR,
    }

    assert_ast_equals(
        graphql_model.ast,
        """
        enum UserLevel {
          MEMBER
          ADMINISTRATOR
        }
        """,
    )


def test_graphql_enum_model_is_created_with_members_descriptions(assert_ast_equals):
    graphql_model = create_graphql_enum_model(
        UserLevel,
        members_descriptions={
            "GUEST": "Default role.",
            "ADMINISTRATOR": "Can use admin panel.",
        },
    )

    assert graphql_model.name == "UserLevel"
    assert graphql_model.members == {
        "GUEST": UserLevel.GUEST,
        "MEMBER": UserLevel.MEMBER,
        "MODERATOR": UserLevel.MODERATOR,
        "ADMINISTRATOR": UserLevel.ADMINISTRATOR,
    }

    assert_ast_equals(
        graphql_model.ast,
        """
        enum UserLevel {
          "Default role."
          GUEST
          MEMBER
          MODERATOR
          "Can use admin panel."
          ADMINISTRATOR
        }
        """,
    )


def test_value_error_is_raised_if_exclude_and_include_members_are_combined(snapshot):
    with pytest.raises(ValueError) as exc_info:
        create_graphql_enum_model(
            UserLevel,
            members_exclude=["MEMBER"],
            members_include=["ADMINISTRATOR"],
        )

    snapshot.assert_match(str(exc_info.value))


def test_value_error_is_raised_if_member_description_is_set_for_missing_item(snapshot):
    with pytest.raises(ValueError) as exc_info:
        create_graphql_enum_model(UserLevel, members_descriptions={"MISSING": "Hello!"})

    snapshot.assert_match(str(exc_info.value))


def test_value_error_is_raised_if_member_description_is_set_for_omitted_item(snapshot):
    with pytest.raises(ValueError) as exc_info:
        create_graphql_enum_model(
            UserLevel,
            members_include=["GUEST"],
            members_descriptions={"ADMINISTRATOR": "Hello!"},
        )

    snapshot.assert_match(str(exc_info.value))


def test_value_error_is_raised_if_member_description_is_set_for_excluded_item(snapshot):
    with pytest.raises(ValueError) as exc_info:
        create_graphql_enum_model(
            UserLevel,
            members_exclude=["ADMINISTRATOR"],
            members_descriptions={"ADMINISTRATOR": "Hello!"},
        )

    snapshot.assert_match(str(exc_info.value))


def test_enum_field_returning_enum_instance(assert_schema_equals):
    class QueryType(GraphQLObject):
        level: UserLevel

        @GraphQLObject.resolver("level")
        def resolve_level(*_) -> UserLevel:
            return UserLevel.MODERATOR

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          level: UserLevel!
        }

        enum UserLevel {
          GUEST
          MEMBER
          MODERATOR
          ADMINISTRATOR
        }
        """,
    )

    result = graphql_sync(schema, "{ level }")

    assert not result.errors
    assert result.data == {"level": "MODERATOR"}


def test_graphql_enum_decorator_without_options_sets_model_on_enum(assert_ast_equals):
    @graphql_enum
    class SeverityLevel(Enum):
        LOW = 0
        MEDIUM = 1
        HIGH = 2

    graphql_model = SeverityLevel.__get_graphql_model__()

    assert graphql_model.name == "SeverityLevel"
    assert graphql_model.members == {
        "LOW": SeverityLevel.LOW,
        "MEDIUM": SeverityLevel.MEDIUM,
        "HIGH": SeverityLevel.HIGH,
    }

    assert_ast_equals(
        graphql_model.ast,
        """
        enum SeverityLevel {
          LOW
          MEDIUM
          HIGH
        }
        """,
    )


def test_graphql_enum_decorator_with_options_sets_model_on_enum(assert_ast_equals):
    @graphql_enum(name="SeverityEnum", members_exclude=["HIGH"])
    class SeverityLevel(Enum):
        LOW = 0
        MEDIUM = 1
        HIGH = 2

    graphql_model = SeverityLevel.__get_graphql_model__()

    assert graphql_model.name == "SeverityEnum"
    assert graphql_model.members == {
        "LOW": SeverityLevel.LOW,
        "MEDIUM": SeverityLevel.MEDIUM,
    }

    assert_ast_equals(
        graphql_model.ast,
        """
        enum SeverityEnum {
          LOW
          MEDIUM
        }
        """,
    )
