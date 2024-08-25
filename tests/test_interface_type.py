from typing import List, Union

from graphql import graphql_sync

from ariadne_graphql_modules import (
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

    class UserType(GraphQLObject, UserInterface):
        name: str

    class ResultType(GraphQLUnion):
        __types__ = [UserType, CommentType]

    class QueryType(GraphQLObject):
        @GraphQLObject.field(graphql_type=List[ResultType])
        def search(*_) -> List[Union[UserType, CommentType]]:
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
          summary: String!
          score: Int!
          name: String!
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


def test_interface_inheritance_without_schema(assert_schema_equals):
    def hello_resolver(*_, name: str) -> str:
        return f"Hello {name}!"

    class UserInterface(GraphQLInterface):
        summary: str
        score: str = GraphQLInterface.field(
            hello_resolver,
            name="better_score",
            graphql_type=str,
            args={"name": GraphQLInterface.argument(name="json")},
            description="desc",
            default_value="my_json",
        )

    class UserType(GraphQLObject, UserInterface):
        name: str = GraphQLInterface.field(
            name="name",
            graphql_type=str,
            args={"name": GraphQLInterface.argument(name="json")},
            default_value="my_json",
        )

    class ResultType(GraphQLUnion):
        __types__ = [UserType, CommentType]

    class QueryType(GraphQLObject):
        @GraphQLObject.field(graphql_type=List[ResultType])
        def search(*_) -> List[Union[UserType, CommentType]]:
            return [
                UserType(),
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
          summary: String!

          \"\"\"desc\"\"\"
          better_score(json: String!): String!
          name: String!
        }

        type Comment {
          id: ID!
          content: String!
        }

        interface UserInterface {
          summary: String!

          \"\"\"desc\"\"\"
          better_score(json: String!): String!
        }

        """,
    )

    result = graphql_sync(
        schema, '{ search { ... on User{ better_score(json: "test") } } }'
    )

    assert not result.errors
    assert result.data == {"search": [{"better_score": "Hello test!"}, {}]}


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

        __requires__ = [UserInterface]

    class ResultType(GraphQLUnion):
        __types__ = [UserType, CommentType]

    class QueryType(GraphQLObject):
        @GraphQLObject.field(graphql_type=List[ResultType])
        def search(*_) -> List[Union[UserType, CommentType]]:
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


def test_interface_inherit_interface(assert_schema_equals):
    class BaseEntityInterface(GraphQLInterface):
        id: GraphQLID

    class UserInterface(BaseEntityInterface):
        username: str

    class UserType(GraphQLObject, UserInterface):
        name: str

    class SuperUserType(UserType):
        is_super_user: bool

    class QueryType(GraphQLObject):
        @GraphQLObject.field
        def users(*_) -> List[UserInterface]:
            return [
                UserType(id="1", username="test_user"),
                SuperUserType(
                    id="2",
                    username="test_super_user",
                    is_super_user=True,
                ),
            ]

    schema = make_executable_schema(
        QueryType, BaseEntityInterface, UserInterface, UserType, SuperUserType
    )

    assert_schema_equals(
        schema,
        """
        type Query {
          users: [UserInterface!]!
        }

        interface UserInterface implements BaseEntityInterface {
          id: ID!
          username: String!
        }

        interface BaseEntityInterface {
          id: ID!
        }

        type User implements BaseEntityInterface & UserInterface {
          id: ID!
          username: String!
          name: String!
        }

        type SuperUser implements BaseEntityInterface & UserInterface {
          id: ID!
          username: String!
          name: String!
          isSuperUser: Boolean!
        }
        """,
    )


def test_interface_descriptions(assert_schema_equals):
    class UserInterface(GraphQLInterface):
        summary: str
        score: int

        __description__ = "Lorem ipsum."

    class UserType(GraphQLObject, UserInterface):
        id: GraphQLID
        username: str

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
          summary: String!
          score: Int!
          id: ID!
          username: String!
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

    class UserType(GraphQLObject, UserInterface):
        id: GraphQLID

    class MyType(GraphQLObject, UserInterface):
        id: GraphQLID
        name: str

    class QueryType(GraphQLObject):
        @GraphQLObject.field(graphql_type=List[UserInterface])
        def users(*_) -> List[UserInterface]:
            return [MyType(id="2", name="old", summary="ss", score=22)]

    schema = make_executable_schema(QueryType, UserType, MyType, UserInterface)

    assert_schema_equals(
        schema,
        """
        type Query {
          users: [UserInterface!]!
        }

        interface UserInterface {
          summary: String!

          \"\"\"Lorem ipsum.\"\"\"
          score: Int!
        }

        type User implements UserInterface {
          summary: String!

          \"\"\"Lorem ipsum.\"\"\"
          score: Int!
          id: ID!
        }

        type My implements UserInterface {
          summary: String!

          \"\"\"Lorem ipsum.\"\"\"
          score: Int!
          id: ID!
          name: String!
        }
        """,
    )
    result = graphql_sync(schema, "{ users { ... on My { __typename score } } }")

    assert not result.errors
    assert result.data == {"users": [{"__typename": "My", "score": 200}]}


def test_interface_with_schema_object_with_schema(assert_schema_equals):
    class UserInterface(GraphQLInterface):
        __schema__ = """
        interface UserInterface {
            summary: String!
            score: Int!
        }
        """

        @GraphQLInterface.resolver("summary")
        def resolve_summary(*_):
            return "base_line"

    class UserType(GraphQLObject):
        __schema__ = """
        type User implements UserInterface {
            summary: String!
            score: Int!
            name: String!
        }
        """
        __requires__ = [UserInterface]

    class ResultType(GraphQLUnion):
        __types__ = [UserType, CommentType]

    class QueryType(GraphQLObject):
        @GraphQLObject.field(graphql_type=List[ResultType])
        def search(*_) -> List[Union[UserType, CommentType]]:
            return [
                UserType(name="Bob"),
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
          summary: String!
          score: Int!
          name: String!
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
    result = graphql_sync(schema, "{ search { ... on User{ summary } } }")

    assert not result.errors
    assert result.data == {
        "search": [
            {
                "summary": "base_line",
            },
            {},
        ]
    }
