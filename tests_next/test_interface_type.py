from typing import List

from graphql import graphql_sync

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

    schema = make_executable_schema(QueryType, UserType)

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
        
        interface UserInterface {
          summary: String!
          score: Int!
        }

        type Comment {
          id: ID!
          content: String!
        }

        """,
    )


def test_interface_inheritance(assert_schema_equals):
    class BaseEntityInterface(GraphQLInterface):
        id: GraphQLID

    class UserInterface(GraphQLInterface):
        id: GraphQLID
        username: str

        __implements__ = [BaseEntityInterface]

    class UserType(GraphQLObject):
        id: GraphQLID
        username: str

        __implements__ = [UserInterface, BaseEntityInterface]

    class QueryType(GraphQLObject):
        @GraphQLObject.field
        def user(*_) -> UserType:
            return UserType(id="1", username="test_user")

    schema = make_executable_schema(
        QueryType, BaseEntityInterface, UserInterface, UserType
    )

    assert_schema_equals(
        schema,
        """
        type Query {
          user: User!
        }

        type User implements UserInterface & BaseEntityInterface {
          id: ID!
          username: String!
        }

        interface UserInterface implements BaseEntityInterface {
          id: ID!
          username: String!
        }

        interface BaseEntityInterface {
          id: ID!
        }
        """,
    )


def test_interface_descriptions(assert_schema_equals):
    class UserInterface(GraphQLInterface):
        summary: str
        score: int

        __description__ = "Lorem ipsum."

    class UserType(GraphQLObject):
        id: GraphQLID
        username: str
        summary: str
        score: int

        __implements__ = [UserInterface]

    class QueryType(GraphQLObject):
        @GraphQLObject.field
        def user(*_) -> UserType:
            return UserType(id="1", username="test_user")

    schema = make_executable_schema(QueryType, UserType, UserInterface)

    assert_schema_equals(
        schema,
        """
        type Query {
          user: User!
        }

        type User implements UserInterface {
          id: ID!
          username: String!
          summary: String!
          score: Int!
        }

        \"\"\"Lorem ipsum.\"\"\"
        interface UserInterface {
          summary: String!
          score: Int!
        }
        """,
    )


def test_interface_resolvers_and_field_descriptions(assert_schema_equals):
    class UserInterface(GraphQLInterface):
        summary: str
        score: int

        @GraphQLInterface.resolver("score", description="Lorem ipsum.")
        def resolve_score(*_):
            return 200

    class UserType(GraphQLObject):
        id: GraphQLID
        summary: str
        score: int

        __implements__ = [UserInterface]

    class QueryType(GraphQLObject):
        @GraphQLObject.field
        def user(*_) -> UserType:
            return UserType(id="1")

    schema = make_executable_schema(QueryType, UserType, UserInterface)

    assert_schema_equals(
        schema,
        """
        type Query {
          user: User!
        }

        type User implements UserInterface {
          id: ID!
          summary: String!
          score: Int!
        }

        interface UserInterface {
          summary: String!

          \"\"\"Lorem ipsum.\"\"\"
          score: Int!
        }
        """,
    )
    result = graphql_sync(schema, "{ user { score } }")

    assert not result.errors
    assert result.data == {"user": {"score": 200}}
