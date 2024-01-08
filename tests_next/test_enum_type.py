from enum import Enum

from graphql import graphql_sync

from ariadne_graphql_modules.next import (
    GraphQLEnum,
    GraphQLObject,
    make_executable_schema,
)


class UserLevelEnum(Enum):
    GUEST = 0
    MEMBER = 1
    ADMIN = 2


def test_enum_field_returning_enum_value(assert_schema_equals):
    class UserLevel(GraphQLEnum):
        __members__ = UserLevelEnum

    class QueryType(GraphQLObject):
        level: UserLevel

        @GraphQLObject.resolver("level")
        def resolve_level(*_) -> UserLevelEnum:
            return UserLevelEnum.MEMBER

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
          ADMIN
        }
        """,
    )

    result = graphql_sync(schema, "{ level }")

    assert not result.errors
    assert result.data == {"level": "MEMBER"}


def test_enum_field_returning_dict_value(assert_schema_equals):
    class UserLevel(GraphQLEnum):
        __members__ = {
            "GUEST": 0,
            "MEMBER": 1,
            "ADMIN": 2,
        }

    class QueryType(GraphQLObject):
        level: UserLevel

        @GraphQLObject.resolver("level")
        def resolve_level(*_) -> dict:
            return 0

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
          ADMIN
        }
        """,
    )

    result = graphql_sync(schema, "{ level }")

    assert not result.errors
    assert result.data == {"level": "GUEST"}


def test_enum_field_returning_str_value(assert_schema_equals):
    class UserLevel(GraphQLEnum):
        __members__ = [
            "GUEST",
            "MEMBER",
            "ADMIN",
        ]

    class QueryType(GraphQLObject):
        level: UserLevel

        @GraphQLObject.resolver("level")
        def resolve_level(*_) -> str:
            return "ADMIN"

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
          ADMIN
        }
        """,
    )

    result = graphql_sync(schema, "{ level }")

    assert not result.errors
    assert result.data == {"level": "ADMIN"}


def test_enum_type_with_custom_name(assert_schema_equals):
    class UserLevel(GraphQLEnum):
        __graphql_name__ = "UserLevelEnum"
        __members__ = UserLevelEnum

    class QueryType(GraphQLObject):
        level: UserLevel

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          level: UserLevelEnum!
        }

        enum UserLevelEnum {
          GUEST
          MEMBER
          ADMIN
        }
        """,
    )


def test_enum_type_with_description(assert_schema_equals):
    class UserLevel(GraphQLEnum):
        __description__ = "Hello world."
        __members__ = UserLevelEnum

    class QueryType(GraphQLObject):
        level: UserLevel

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          level: UserLevel!
        }

        \"\"\"Hello world.\"\"\"
        enum UserLevel {
          GUEST
          MEMBER
          ADMIN
        }
        """,
    )


def test_enum_type_with_member_description(assert_schema_equals):
    class UserLevel(GraphQLEnum):
        __members__ = UserLevelEnum
        __members_descriptions__ = {"MEMBER": "Hello world."}

    class QueryType(GraphQLObject):
        level: UserLevel

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          level: UserLevel!
        }

        enum UserLevel {
          GUEST

          \"\"\"Hello world.\"\"\"
          MEMBER
          ADMIN
        }
        """,
    )


def test_schema_enum_field_returning_enum_value(assert_schema_equals):
    class UserLevel(GraphQLEnum):
        __schema__ = """
            enum UserLevel {
              GUEST
              MEMBER
              ADMIN
            }
            """
        __members__ = UserLevelEnum

    class QueryType(GraphQLObject):
        level: UserLevel

        @GraphQLObject.resolver("level")
        def resolve_level(*_) -> UserLevelEnum:
            return UserLevelEnum.MEMBER

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
          ADMIN
        }
        """,
    )

    result = graphql_sync(schema, "{ level }")

    assert not result.errors
    assert result.data == {"level": "MEMBER"}


def test_schema_enum_field_returning_dict_value(assert_schema_equals):
    class UserLevel(GraphQLEnum):
        __schema__ = """
            enum UserLevel {
              GUEST
              MEMBER
              ADMIN
            }
            """
        __members__ = {
            "GUEST": 0,
            "MEMBER": 1,
            "ADMIN": 2,
        }

    class QueryType(GraphQLObject):
        level: UserLevel

        @GraphQLObject.resolver("level")
        def resolve_level(*_) -> int:
            return 2

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
          ADMIN
        }
        """,
    )

    result = graphql_sync(schema, "{ level }")

    assert not result.errors
    assert result.data == {"level": "ADMIN"}


def test_schema_enum_field_returning_str_value(assert_schema_equals):
    class UserLevel(GraphQLEnum):
        __schema__ = """
            enum UserLevel {
              GUEST
              MEMBER
              ADMIN
            }
            """

    class QueryType(GraphQLObject):
        level: UserLevel

        @GraphQLObject.resolver("level")
        def resolve_level(*_) -> str:
            return "GUEST"

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
          ADMIN
        }
        """,
    )

    result = graphql_sync(schema, "{ level }")

    assert not result.errors
    assert result.data == {"level": "GUEST"}


def test_schema_enum_with_description_attr(assert_schema_equals):
    class UserLevel(GraphQLEnum):
        __schema__ = """
            enum UserLevel {
              GUEST
              MEMBER
              ADMIN
            }
            """
        __members__ = {
            "GUEST": 0,
            "MEMBER": 1,
            "ADMIN": 2,
        }
        __description__ = "Hello world."

    class QueryType(GraphQLObject):
        level: UserLevel

        @GraphQLObject.resolver("level")
        def resolve_level(*_) -> int:
            return 2

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          level: UserLevel!
        }

        \"\"\"Hello world.\"\"\"
        enum UserLevel {
          GUEST
          MEMBER
          ADMIN
        }
        """,
    )

    result = graphql_sync(schema, "{ level }")

    assert not result.errors
    assert result.data == {"level": "ADMIN"}


def test_schema_enum_with_schema_description(assert_schema_equals):
    class UserLevel(GraphQLEnum):
        __schema__ = """
            \"\"\"Hello world.\"\"\"
            enum UserLevel {
              GUEST
              MEMBER
              ADMIN
            }
            """
        __members__ = {
            "GUEST": 0,
            "MEMBER": 1,
            "ADMIN": 2,
        }

    class QueryType(GraphQLObject):
        level: UserLevel

        @GraphQLObject.resolver("level")
        def resolve_level(*_) -> int:
            return 2

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          level: UserLevel!
        }

        \"\"\"Hello world.\"\"\"
        enum UserLevel {
          GUEST
          MEMBER
          ADMIN
        }
        """,
    )

    result = graphql_sync(schema, "{ level }")

    assert not result.errors
    assert result.data == {"level": "ADMIN"}


def test_schema_enum_with_member_description(assert_schema_equals):
    class UserLevel(GraphQLEnum):
        __schema__ = """
            enum UserLevel {
              GUEST
              MEMBER
              ADMIN
            }
            """
        __members__ = {
            "GUEST": 0,
            "MEMBER": 1,
            "ADMIN": 2,
        }
        __members_descriptions__ = {"MEMBER": "Hello world."}

    class QueryType(GraphQLObject):
        level: UserLevel

        @GraphQLObject.resolver("level")
        def resolve_level(*_) -> int:
            return 2

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          level: UserLevel!
        }

        enum UserLevel {
          GUEST

          \"\"\"Hello world.\"\"\"
          MEMBER
          ADMIN
        }
        """,
    )

    result = graphql_sync(schema, "{ level }")

    assert not result.errors
    assert result.data == {"level": "ADMIN"}


def test_schema_enum_with_member_schema_description(assert_schema_equals):
    class UserLevel(GraphQLEnum):
        __schema__ = """
            enum UserLevel {
              GUEST
              \"\"\"Hello world.\"\"\"
              MEMBER
              ADMIN
            }
            """
        __members__ = {
            "GUEST": 0,
            "MEMBER": 1,
            "ADMIN": 2,
        }

    class QueryType(GraphQLObject):
        level: UserLevel

        @GraphQLObject.resolver("level")
        def resolve_level(*_) -> int:
            return 2

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          level: UserLevel!
        }

        enum UserLevel {
          GUEST

          \"\"\"Hello world.\"\"\"
          MEMBER
          ADMIN
        }
        """,
    )

    result = graphql_sync(schema, "{ level }")

    assert not result.errors
    assert result.data == {"level": "ADMIN"}
