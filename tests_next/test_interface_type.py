from typing import List

from ariadne_graphql_modules.next import (
    GraphQLID,
    GraphQLObject,
    GraphQLInterface,
    GraphQLUnion,
    make_executable_schema,
)


class CommentType(GraphQLObject):
    id: GraphQLID
    content: str


def test_interface_without_schema(assert_schema_equals):
    class UserInterface(GraphQLInterface):
        summary: str
        score: int

    class UserType(GraphQLObject):
        name: str
        summary: str
        score: int

        __implements__ = [UserInterface]

    class ResultType(GraphQLUnion):
        __types__ = [UserType, CommentType]

    class QueryType(GraphQLObject):
        @GraphQLObject.field(type=List[ResultType])
        def search(*_) -> List[UserType | CommentType]:
            return [
                UserType(id=1, username="Bob"),
                CommentType(id=2, content="Hello World!"),
            ]

    schema = make_executable_schema(QueryType, UserInterface, UserType)

    assert_schema_equals(
        schema,
        """
        type Query {
          search: [Result!]!
        }

        union Result = User | Comment

        type User implements UserInterface {
          name: String!
          summary: String!
          score: Int!
        }

        type Comment {
          id: ID!
          content: String!
        }

        interface UserInterface {
          summary: String!
          score: Int!
        }

        """,
    )


def test_interface_with_schema(assert_schema_equals):
    class UserInterface(GraphQLInterface):
        __schema__ = """
        interface UserInterface {
            summary: String!
            score: Int!
        }
        """

    class UserType(GraphQLObject):
        __schema__ = """
        type User implements UserInterface {
            id: ID!
            name: String!
            summary: String!
            score: Int!
        }
        """

        __implements__ = [UserInterface]

    class ResultType(GraphQLUnion):
        __types__ = [UserType, CommentType]

    class QueryType(GraphQLObject):
        @GraphQLObject.field(type=List[ResultType])
        def search(*_) -> List[UserType | CommentType]:
            return [
                UserType(id=1, username="Bob"),
                CommentType(id=2, content="Hello World!"),
            ]

    schema = make_executable_schema(QueryType, UserInterface, UserType)

    assert_schema_equals(
        schema,
        """
        type Query {
          search: [Result!]!
        }

        union Result = User | Comment

        type User implements UserInterface {
          id: ID!
          name: String!
          summary: String!
          score: Int!
        }

        type Comment {
          id: ID!
          content: String!
        }

        interface UserInterface {
          summary: String!
          score: Int!
        }

        """,
    )
