from dataclasses import dataclass
from datetime import date, datetime

from graphql import StringValueNode
from ariadne_graphql_modules.bases import DeferredType
from ariadne_graphql_modules.collection_type import CollectionType
from ariadne_graphql_modules.enum_type import EnumType
from ariadne_graphql_modules.input_type import InputType
from ariadne_graphql_modules.interface_type import InterfaceType
from ariadne_graphql_modules.next.compatibility_layer import wrap_legacy_types
from ariadne_graphql_modules.next.executable_schema import make_executable_schema
from ariadne_graphql_modules.object_type import ObjectType
from ariadne_graphql_modules.scalar_type import ScalarType
from ariadne_graphql_modules.subscription_type import SubscriptionType
from ariadne_graphql_modules.union_type import UnionType


def test_object_type(
    assert_schema_equals,
):
    # pylint: disable=unused-variable
    class FancyObjectType(ObjectType):
        __schema__ = """
        type FancyObject {
            id: ID!
            someInt: Int!
            someFloat: Float!
            someBoolean: Boolean!
            someString: String!
        }
        """

    class QueryType(ObjectType):
        __schema__ = """
        type Query {
            field: String!
            other: String!
            firstField: String!
            secondField: String!
            fieldWithArg(someArg: String): String!
        }
        """
        __aliases__ = {
            "firstField": "first_field",
            "secondField": "second_field",
            "fieldWithArg": "field_with_arg",
        }
        __fields_args__ = {"fieldWithArg": {"someArg": "some_arg"}}

        @staticmethod
        def resolve_other(*_):
            return "Word Up!"

        @staticmethod
        def resolve_second_field(obj, *_):
            return "Obj: %s" % obj["secondField"]

        @staticmethod
        def resolve_field_with_arg(*_, some_arg):
            return some_arg

    class UserRoleEnum(EnumType):
        __schema__ = """
            enum UserRole {
                USER
                MOD
                ADMIN
            }
        """

    my_legacy_types = wrap_legacy_types(QueryType, UserRoleEnum, FancyObjectType)
    schema = make_executable_schema(*my_legacy_types)

    assert_schema_equals(
        schema,
        """
        type Query {
          field: String!
          other: String!
          firstField: String!
          secondField: String!
          fieldWithArg(someArg: String): String!
        }

        enum UserRole {
          USER
          MOD
          ADMIN
        }

        type FancyObject {
          id: ID!
          someInt: Int!
          someFloat: Float!
          someBoolean: Boolean!
          someString: String!
        }
        """,
    )


def test_collection_types_are_included_in_schema(assert_schema_equals):
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

    my_legacy_types = wrap_legacy_types(UserTypes)
    schema = make_executable_schema(*my_legacy_types)

    assert_schema_equals(
        schema,
        """
        type Query {
          user: User
        }

        type User {
          id: ID!
          group: UserGroup!
        }

        type UserGroup {
          id: ID!
        }
        """,
    )


def test_input_type(assert_schema_equals):
    class UserInput(InputType):
        __schema__ = """
        input UserInput {
            id: ID!
            fullName: String!
        }
        """
        __args__ = {
            "fullName": "full_name",
        }

    class GenericScalar(ScalarType):
        __schema__ = "scalar Generic"

    class QueryType(ObjectType):
        __schema__ = """
        type Query {
            reprInput(input: UserInput): Generic!
        }
        """
        __aliases__ = {"reprInput": "repr_input"}
        __requires__ = [GenericScalar, UserInput]

        @staticmethod
        def resolve_repr_input(*_, input):  # pylint: disable=redefined-builtin
            return input

    my_legacy_types = wrap_legacy_types(QueryType)
    schema = make_executable_schema(*my_legacy_types)

    assert_schema_equals(
        schema,
        """
        scalar Generic

        type Query {
          reprInput(input: UserInput): Generic!
        }

        input UserInput {
          id: ID!
          fullName: String!
        }
        """,
    )


def test_interface_type(assert_schema_equals):
    @dataclass
    class User:
        id: int
        name: str
        summary: str

    @dataclass
    class Comment:
        id: int
        message: str
        summary: str

    class ResultInterface(InterfaceType):
        __schema__ = """
        interface Result {
            summary: String!
            score: Int!
        }
        """

        @staticmethod
        def resolve_type(instance, *_):
            if isinstance(instance, Comment):
                return "Comment"

            if isinstance(instance, User):
                return "User"

            return None

    class QueryType(ObjectType):
        __schema__ = """
        type Query {
            results: [Result!]!
        }
        """
        __requires__ = [ResultInterface]

    my_legacy_types = wrap_legacy_types(QueryType)
    schema = make_executable_schema(*my_legacy_types)

    assert_schema_equals(
        schema,
        """
        type Query {
          results: [Result!]!
        }

        interface Result {
          summary: String!
          score: Int!
        }
        """,
    )


def test_scalar_type(assert_schema_equals):
    TEST_DATE = date(2006, 9, 13)

    class DateReadOnlyScalar(ScalarType):
        __schema__ = "scalar DateReadOnly"

        @staticmethod
        def serialize(date):
            return date.strftime("%Y-%m-%d")

    class DateInputScalar(ScalarType):
        __schema__ = "scalar DateInput"

        @staticmethod
        def parse_value(formatted_date):
            parsed_datetime = datetime.strptime(formatted_date, "%Y-%m-%d")
            return parsed_datetime.date()

        @staticmethod
        def parse_literal(ast, variable_values=None):  # pylint: disable=unused-argument
            if not isinstance(ast, StringValueNode):
                raise ValueError()

            formatted_date = ast.value
            parsed_datetime = datetime.strptime(formatted_date, "%Y-%m-%d")
            return parsed_datetime.date()

    class DefaultParserScalar(ScalarType):
        __schema__ = "scalar DefaultParser"

        @staticmethod
        def parse_value(value):
            return type(value).__name__

    class QueryType(ObjectType):
        __schema__ = """
        type Query {
            testSerialize: DateReadOnly!
            testInput(value: DateInput!): Boolean!
            testInputValueType(value: DefaultParser!): String!
        }
        """
        __requires__ = [
            DateReadOnlyScalar,
            DateInputScalar,
            DefaultParserScalar,
        ]
        __aliases__ = {
            "testSerialize": "test_serialize",
            "testInput": "test_input",
            "testInputValueType": "test_input_value_type",
        }

        @staticmethod
        def resolve_test_serialize(*_):
            return TEST_DATE

        @staticmethod
        def resolve_test_input(*_, value):
            assert value == TEST_DATE
            return True

        @staticmethod
        def resolve_test_input_value_type(*_, value):
            return value

    my_legacy_types = wrap_legacy_types(QueryType)
    schema = make_executable_schema(*my_legacy_types)

    assert_schema_equals(
        schema,
        """
        scalar DateInput

        scalar DateReadOnly

        scalar DefaultParser

        type Query {
          testSerialize: DateReadOnly!
          testInput(value: DateInput!): Boolean!
          testInputValueType(value: DefaultParser!): String!
        }
        """,
    )


def test_subscription_type(assert_schema_equals):
    class ExampleInterface(InterfaceType):
        __schema__ = """
        interface Interface {
            threads: ID!
        }
        """

        @staticmethod
        def resolve_type(instance, *_):
            return "Threads"

    class ChatSubscription(SubscriptionType):
        __schema__ = """
        type Subscription {
            chat: ID!
        }
        """

    class ExtendChatSubscription(SubscriptionType):
        __schema__ = """
        extend type Subscription implements Interface {
            threads: ID!
        }
        """
        __requires__ = [ChatSubscription, ExampleInterface]

    class QueryType(ObjectType):
        __schema__ = """
        type Query {
            testSubscription: String!
        }
        """

    my_legacy_types = wrap_legacy_types(
        QueryType,
        ExampleInterface,
        ChatSubscription,
        ExtendChatSubscription,
    )

    schema = make_executable_schema(*my_legacy_types)

    assert_schema_equals(
        schema,
        """
        type Query {
          testSubscription: String!
        }

        type Subscription implements Interface {
          chat: ID!
          threads: ID!
        }

        interface Interface {
          threads: ID!
        }
        """,
    )


def test_union_type(assert_schema_equals):
    @dataclass
    class User:
        id: int
        name: str

    @dataclass
    class Comment:
        id: int
        message: str

    class UserType(ObjectType):
        __schema__ = """
        type User {
            id: ID!
            name: String!
        }
        """

    class CommentType(ObjectType):
        __schema__ = """
        type Comment {
            id: ID!
            message: String!
        }
        """

    class ExampleUnion(UnionType):
        __schema__ = "union Result = User | Comment"
        __requires__ = [UserType, CommentType]

        @staticmethod
        def resolve_type(instance, *_):
            if isinstance(instance, Comment):
                return "Comment"

            if isinstance(instance, User):
                return "User"

            return None

    class QueryType(ObjectType):
        __schema__ = """
        type Query {
            testUnion: String!
        }
        """

    my_legacy_types = wrap_legacy_types(ExampleUnion, CommentType, QueryType)

    schema = make_executable_schema(*my_legacy_types)

    assert_schema_equals(
        schema,
        """
        type Query {
          testUnion: String!
        }

        union Result = User | Comment

        type User {
          id: ID!
          name: String!
        }

        type Comment {
          id: ID!
          message: String!
        }
        """,
    )
