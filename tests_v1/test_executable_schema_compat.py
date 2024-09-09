from ariadne import ObjectType as OldObjectType, QueryType, gql, graphql_sync
from ariadne_graphql_modules.v1 import DeferredType, ObjectType, make_executable_schema


def test_old_schema_definition_is_executable():
    type_defs = gql(
        """
        type Query {
            random: Int!
            user: User!
        }

        type User {
            id: ID!
            name: String!
            score: Int!
        }
        """
    )

    query_type = QueryType()

    @query_type.field("random")
    def resolve_random(*_):
        return 6

    @query_type.field("user")
    def resolve_user(*_):
        return {
            "id": 1,
            "name": "Alice",
        }

    user_type = OldObjectType("User")

    @user_type.field("score")
    def resolve_user_score(user, _):
        return user["id"] * 7

    schema = make_executable_schema(type_defs, query_type, user_type)

    _, result = graphql_sync(schema, {"query": "{ random user { id name score } }"})
    assert result == {
        "data": {
            "random": 6,
            "user": {
                "id": "1",
                "name": "Alice",
                "score": 7,
            },
        },
    }


def test_old_schema_depending_on_new_types_is_executable():
    type_defs = gql(
        """
        type Query {
            random: Int!
            user: User!
        }
        """
    )

    query_type = QueryType()

    @query_type.field("random")
    def resolve_random(*_):
        return 6

    @query_type.field("user")
    def resolve_user(*_):
        return {
            "id": 1,
            "name": "Alice",
        }

    class UserType(ObjectType):
        __schema__ = gql(
            """
            type User {
                id: ID!
                name: String!
                score: Int!
            }
            """
        )

        @staticmethod
        def resolve_score(user, _):
            return user["id"] * 7

    schema = make_executable_schema(UserType, type_defs, query_type)

    _, result = graphql_sync(schema, {"query": "{ random user { id name score } }"})
    assert result == {
        "data": {
            "random": 6,
            "user": {
                "id": "1",
                "name": "Alice",
                "score": 7,
            },
        },
    }


def test_new_schema_depending_on_old_types_is_executable():
    class QueryType(ObjectType):
        __schema__ = gql(
            """
            type Query {
                random: Int!
                user: User!
            }
            """
        )
        __requires__ = [DeferredType("User")]

        @staticmethod
        def resolve_random(*_):
            return 6

        @staticmethod
        def resolve_user(*_):
            return {
                "id": 1,
                "name": "Alice",
            }

    type_defs = gql(
        """
        type User {
            id: ID!
            name: String!
            score: Int!
        }
        """
    )

    user_type = OldObjectType("User")

    @user_type.field("score")
    def resolve_user_score(user, _):
        return user["id"] * 7

    schema = make_executable_schema(QueryType, type_defs, user_type)

    _, result = graphql_sync(schema, {"query": "{ random user { id name score } }"})
    assert result == {
        "data": {
            "random": 6,
            "user": {
                "id": "1",
                "name": "Alice",
                "score": 7,
            },
        },
    }


def test_old_and_new_roots_can_be_combined():
    type_defs = gql(
        """
        type Query {
            random: Int!
        }
        """
    )

    query_type = QueryType()

    @query_type.field("random")
    def resolve_random(*_):
        return 6

    class UserType(ObjectType):
        __schema__ = gql(
            """
            type User {
                id: ID!
                name: String!
                score: Int!
            }
            """
        )

        @staticmethod
        def resolve_score(user, _):
            return user["id"] * 7

    class NewQueryType(ObjectType):
        __schema__ = gql(
            """
            type Query {
                user: User!
            }
            """
        )
        __requires__ = [UserType]

        @staticmethod
        def resolve_user(*_):
            return {
                "id": 1,
                "name": "Alice",
            }

    schema = make_executable_schema(NewQueryType, type_defs, query_type)

    _, result = graphql_sync(schema, {"query": "{ random user { id name score } }"})
    assert result == {
        "data": {
            "random": 6,
            "user": {
                "id": "1",
                "name": "Alice",
                "score": 7,
            },
        },
    }
