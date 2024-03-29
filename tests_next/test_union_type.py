from datetime import date
from typing import List

from graphql import graphql_sync

from ariadne_graphql_modules import gql
from ariadne_graphql_modules.next import (
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
        @GraphQLObject.field(type=List[ResultType])
        def search(*_) -> List[UserType | CommentType]:
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
