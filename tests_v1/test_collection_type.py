from graphql import graphql_sync

from ariadne_graphql_modules.v1 import (
    CollectionType,
    DeferredType,
    ObjectType,
    make_executable_schema,
)


class QueryType(ObjectType):
    __schema__ = """
    type Query {
        user: User
    }
    """
    __requires__ = [DeferredType("User")]


class UserGroupType(ObjectType):
    __schema__ = """
    type UserGroup {
        id: ID!
    }
    """


class UserType(ObjectType):
    __schema__ = """
    type User {
        id: ID!
        group: UserGroup!
    }
    """
    __requires__ = [UserGroupType]


class UserTypes(CollectionType):
    __types__ = [
        QueryType,
        UserType,
    ]


def test_collection_types_are_included_in_schema():
    schema = make_executable_schema(UserTypes)
    assert schema.get_type("User")
    assert schema.get_type("UserGroup")


def test_collection_types_can_be_queries():
    schema = make_executable_schema(UserTypes)
    result = graphql_sync(
        schema,
        "{ user { id group { id } } }",
        root_value={
            "user": {
                "id": "1",
                "group": {
                    "id": "2",
                },
            },
        },
    )
    assert result.data == {
        "user": {
            "id": "1",
            "group": {
                "id": "2",
            },
        },
    }
