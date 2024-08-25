from typing import List, Union

from graphql import graphql_sync

from ariadne_graphql_modules import (
    GraphQLID,
    GraphQLObject,
    GraphQLUnion,
    make_executable_schema,
)


class UserType(GraphQLObject):
    id: GraphQLID
    username: str


class CommentType(GraphQLObject):
    id: GraphQLID
    content: str


def test_union_field_returning_object_instance(assert_schema_equals):
    class ResultType(GraphQLUnion):
        __types__ = [UserType, CommentType]

    class QueryType(GraphQLObject):
        @GraphQLObject.field(graphql_type=List[ResultType])
        @staticmethod
        def search(*_) -> List[Union[UserType, CommentType]]:
            return [
                UserType(id=1, username="Bob"),
                CommentType(id=2, content="Hello World!"),
            ]

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          search: [Result!]!
        }

        union Result = User | Comment

        type User {
          id: ID!
          username: String!
        }

        type Comment {
          id: ID!
          content: String!
        }
        """,
    )

    result = graphql_sync(
        schema,
        """
        {
            search {
                ... on User {
                    id
                    username
                }
                ... on Comment {
                    id
                    content
                }
            }
        }
        """,
    )

    assert not result.errors
    assert result.data == {
        "search": [
            {"id": "1", "username": "Bob"},
            {"id": "2", "content": "Hello World!"},
        ]
    }


def test_union_field_returning_empty_list():
    class ResultType(GraphQLUnion):
        __types__ = [UserType, CommentType]

    class QueryType(GraphQLObject):
        @GraphQLObject.field(graphql_type=List[ResultType])
        @staticmethod
        def search(*_) -> List[Union[UserType, CommentType]]:
            return []

    schema = make_executable_schema(QueryType)

    result = graphql_sync(
        schema,
        """
        {
            search {
                ... on User {
                    id
                    username
                }
                ... on Comment {
                    id
                    content
                }
            }
        }
        """,
    )
    assert not result.errors
    assert result.data == {"search": []}


def test_union_field_with_invalid_type_access():
    class ResultType(GraphQLUnion):
        __types__ = [UserType, CommentType]

    class QueryType(GraphQLObject):
        @GraphQLObject.field(graphql_type=List[ResultType])
        @staticmethod
        def search(*_) -> List[Union[UserType, CommentType]]:
            return [
                UserType(id=1, username="Bob"),
                "InvalidType",
            ]

    schema = make_executable_schema(QueryType)

    result = graphql_sync(
        schema,
        """
        {
            search {
                ... on User {
                    id
                    username
                }
                ... on Comment {
                    id
                    content
                }
            }
        }
        """,
    )
    assert result.errors
    assert "InvalidType" in str(result.errors)


def test_serialization_error_handling():
    class InvalidType:
        def __init__(self, value):
            self.value = value

    class ResultType(GraphQLUnion):
        __types__ = [UserType, CommentType]

    class QueryType(GraphQLObject):
        @GraphQLObject.field(graphql_type=List[ResultType])
        @staticmethod
        def search(*_) -> List[Union[UserType, CommentType, InvalidType]]:
            return [InvalidType("This should cause an error")]

    schema = make_executable_schema(QueryType)

    result = graphql_sync(
        schema,
        """
        {
            search {
                ... on User {
                    id
                    username
                }
            }
        }
        """,
    )
    assert result.errors


def test_union_with_schema_definition():
    class SearchResultUnion(GraphQLUnion):
        __schema__ = """
        union SearchResult = User | Comment
        """
        __types__ = [UserType, CommentType]

    class QueryType(GraphQLObject):
        @GraphQLObject.field(graphql_type=List[SearchResultUnion])
        @staticmethod
        def search(*_) -> List[Union[UserType, CommentType]]:
            return [
                UserType(id="1", username="Alice"),
                CommentType(id="2", content="Test post"),
            ]

    schema = make_executable_schema(QueryType, SearchResultUnion)

    result = graphql_sync(
        schema,
        """
        {
            search {
                ... on User {
                    id
                    username
                }
                ... on Comment {
                    id
                    content
                }
            }
        }
        """,
    )
    assert not result.errors
    assert result.data == {
        "search": [
            {"id": "1", "username": "Alice"},
            {"id": "2", "content": "Test post"},
        ]
    }
