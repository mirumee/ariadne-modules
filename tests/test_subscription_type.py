# pylint: disable=unnecessary-dunder-call
from typing import List

from ariadne import gql
from graphql import subscribe, parse
import pytest
from ariadne_graphql_modules import (
    GraphQLID,
    GraphQLObject,
    GraphQLSubscription,
    GraphQLUnion,
    make_executable_schema,
)


class Message(GraphQLObject):
    id: GraphQLID
    content: str
    author: str


class User(GraphQLObject):
    id: GraphQLID
    username: str


class Notification(GraphQLUnion):
    __types__ = [Message, User]


@pytest.mark.asyncio
async def test_basic_subscription_without_schema(assert_schema_equals):
    class SubscriptionType(GraphQLSubscription):
        message_added: Message

        @GraphQLSubscription.source("message_added", graphql_type=Message)
        @staticmethod
        async def message_added_generator(*_):
            while True:
                yield {"id": "some_id", "content": "message", "author": "Anon"}

        @GraphQLSubscription.resolver("message_added")
        @staticmethod
        async def resolve_message_added(message, *_):
            return message

    class QueryType(GraphQLObject):
        @GraphQLObject.field(graphql_type=str)
        @staticmethod
        def search_sth(*_) -> str:
            return "search"

    schema = make_executable_schema(QueryType, SubscriptionType)

    assert_schema_equals(
        schema,
        """
        type Query {
          searchSth: String!
        }

        type Subscription {
          messageAdded: Message!
        }

        type Message {
          id: ID!
          content: String!
          author: String!
        }
        """,
    )

    query = parse("subscription { messageAdded {id content author} }")
    sub = await subscribe(schema, query)

    # Ensure the subscription is an async iterator
    assert hasattr(sub, "__aiter__")

    # Fetch the first result
    result = await sub.__anext__()  # type: ignore

    # Validate the result
    assert not result.errors
    assert result.data == {
        "messageAdded": {"id": "some_id", "content": "message", "author": "Anon"}
    }


@pytest.mark.asyncio
async def test_basic_many_subscription_without_schema(assert_schema_equals):
    class SubscriptionType(GraphQLSubscription):
        message_added: Message

        @GraphQLSubscription.source("message_added", graphql_type=Message)
        @staticmethod
        async def message_added_generator(*_):
            while True:
                yield {"id": "some_id", "content": "message", "author": "Anon"}

        @GraphQLSubscription.resolver("message_added")
        @staticmethod
        async def resolve_message_added(message, *_):
            return message

    class SubscriptionSecondType(GraphQLSubscription):
        message_added_second: Message

        @GraphQLSubscription.source("message_added_second", graphql_type=Message)
        @staticmethod
        async def message_added_generator(*_):
            while True:
                yield {"id": "some_id", "content": "message", "author": "Anon"}

        @GraphQLSubscription.resolver("message_added_second")
        @staticmethod
        async def resolve_message_added(message, *_):
            return message

    class QueryType(GraphQLObject):
        @GraphQLObject.field(graphql_type=str)
        @staticmethod
        def search_sth(*_) -> str:
            return "search"

    schema = make_executable_schema(QueryType, SubscriptionType, SubscriptionSecondType)

    assert_schema_equals(
        schema,
        """
        type Query {
          searchSth: String!
        }

        type Subscription {
          messageAdded: Message!
          messageAddedSecond: Message!
        }

        type Message {
          id: ID!
          content: String!
          author: String!
        }
        """,
    )

    query = parse("subscription { messageAdded {id content author} }")
    sub = await subscribe(schema, query)

    # Ensure the subscription is an async iterator
    assert hasattr(sub, "__aiter__")

    # Fetch the first result
    result = await sub.__anext__()  # type: ignore

    # Validate the result
    assert not result.errors
    assert result.data == {
        "messageAdded": {"id": "some_id", "content": "message", "author": "Anon"}
    }


@pytest.mark.asyncio
async def test_subscription_with_arguments_without_schema(assert_schema_equals):
    class SubscriptionType(GraphQLSubscription):

        @GraphQLSubscription.source(
            "message_added",
            args={"channel": GraphQLObject.argument(description="Lorem ipsum.")},
            graphql_type=Message,
        )
        @staticmethod
        async def message_added_generator(*_, channel: GraphQLID):
            while True:
                yield {
                    "id": "some_id",
                    "content": f"message_{channel}",
                    "author": "Anon",
                }

        @GraphQLSubscription.field
        @staticmethod
        def message_added(
            message, *_, channel: GraphQLID
        ):  # pylint: disable=unused-argument
            return message

    class QueryType(GraphQLObject):
        @GraphQLObject.field(graphql_type=str)
        @staticmethod
        def search_sth(*_) -> str:
            return "search"

    schema = make_executable_schema(QueryType, SubscriptionType)

    assert_schema_equals(
        schema,
        """
        type Query {
          searchSth: String!
        }

        type Subscription {
          messageAdded(
            \"\"\"Lorem ipsum.\"\"\"
            channel: ID!
          ): Message!
        }

        type Message {
          id: ID!
          content: String!
          author: String!
        }
        """,
    )

    query = parse('subscription { messageAdded(channel: "123") {id content author} }')
    sub = await subscribe(schema, query)

    # Ensure the subscription is an async iterator
    assert hasattr(sub, "__aiter__")

    # Fetch the first result
    result = await sub.__anext__()  # type: ignore

    # Validate the result
    assert not result.errors
    assert result.data == {
        "messageAdded": {"id": "some_id", "content": "message_123", "author": "Anon"}
    }


@pytest.mark.asyncio
async def test_multiple_supscriptions_without_schema(assert_schema_equals):
    class SubscriptionType(GraphQLSubscription):
        message_added: Message
        user_joined: User

        @GraphQLSubscription.source(
            "message_added",
            args={"channel": GraphQLObject.argument(description="Lorem ipsum.")},
            graphql_type=Message,
        )
        @staticmethod
        async def message_added_generator(*_, channel: GraphQLID):
            while True:
                yield {
                    "id": "some_id",
                    "content": f"message_{channel}",
                    "author": "Anon",
                }

        @GraphQLSubscription.resolver(
            "message_added",
        )
        @staticmethod
        async def resolve_message_added(
            message, *_, channel: GraphQLID  # pylint: disable=unused-argument
        ):
            return message

        @GraphQLSubscription.source(
            "user_joined",
            graphql_type=Message,
        )
        @staticmethod
        async def user_joined_generator(*_):
            while True:
                yield {
                    "id": "some_id",
                    "username": "username",
                }

        @GraphQLSubscription.resolver(
            "user_joined",
        )
        @staticmethod
        async def resolve_user_joined(user, *_):
            return user

    class QueryType(GraphQLObject):
        @GraphQLObject.field(graphql_type=str)
        @staticmethod
        def search_sth(*_) -> str:
            return "search"

    schema = make_executable_schema(QueryType, SubscriptionType)

    assert_schema_equals(
        schema,
        """
        type Query {
          searchSth: String!
        }

        type Subscription {
          messageAdded(
            \"\"\"Lorem ipsum.\"\"\"
            channel: ID!
          ): Message!
          userJoined: User!
        }

        type Message {
          id: ID!
          content: String!
          author: String!
        }

        type User {
          id: ID!
          username: String!
        }
        """,
    )

    query = parse("subscription { userJoined {id username} }")
    sub = await subscribe(schema, query)

    # Ensure the subscription is an async iterator
    assert hasattr(sub, "__aiter__")

    # Fetch the first result
    result = await sub.__anext__()  # type: ignore

    # Validate the result
    assert not result.errors
    assert result.data == {"userJoined": {"id": "some_id", "username": "username"}}


@pytest.mark.asyncio
async def test_subscription_with_complex_data_without_schema(assert_schema_equals):
    class SubscriptionType(GraphQLSubscription):
        messages_in_channel: List[Message]

        @GraphQLSubscription.source(
            "messages_in_channel",
            args={"channel_id": GraphQLObject.argument(description="Lorem ipsum.")},
            graphql_type=List[Message],
        )
        @staticmethod
        async def message_added_generator(*_, channel_id: GraphQLID):
            while True:
                yield [
                    {
                        "id": "some_id",
                        "content": f"message_{channel_id}",
                        "author": "Anon",
                    }
                ]

        @GraphQLSubscription.resolver(
            "messages_in_channel",
        )
        @staticmethod
        async def resolve_message_added(
            message, *_, channel_id: GraphQLID
        ):  # pylint: disable=unused-argument
            return message

    class QueryType(GraphQLObject):
        @GraphQLObject.field(graphql_type=str)
        @staticmethod
        def search_sth(*_) -> str:
            return "search"

    schema = make_executable_schema(QueryType, SubscriptionType)

    assert_schema_equals(
        schema,
        """
        type Query {
          searchSth: String!
        }

        type Subscription {
          messagesInChannel(
            \"\"\"Lorem ipsum.\"\"\"
            channelId: ID!
          ): [Message!]!
        }

        type Message {
          id: ID!
          content: String!
          author: String!
        }
        """,
    )

    query = parse(
        'subscription { messagesInChannel(channelId: "123") {id content author} }'
    )
    sub = await subscribe(schema, query)

    # Ensure the subscription is an async iterator
    assert hasattr(sub, "__aiter__")

    # Fetch the first result
    result = await sub.__anext__()  # type: ignore

    # Validate the result
    assert not result.errors
    assert result.data == {
        "messagesInChannel": [
            {"id": "some_id", "content": "message_123", "author": "Anon"}
        ]
    }


@pytest.mark.asyncio
async def test_subscription_with_union_without_schema(assert_schema_equals):
    class SubscriptionType(GraphQLSubscription):
        notification_received: Notification
        __description__ = "test test"

        @GraphQLSubscription.source(
            "notification_received", description="hello", graphql_type=Message
        )
        @staticmethod
        async def message_added_generator(*_):
            while True:
                yield Message(id=1, content="content", author="anon")

        @GraphQLSubscription.resolver(
            "notification_received",
        )
        @staticmethod
        async def resolve_message_added(message: Message, *_):
            return message

    class QueryType(GraphQLObject):
        @GraphQLObject.field(graphql_type=str)
        @staticmethod
        def search_sth(*_) -> str:
            return "search"

    schema = make_executable_schema(QueryType, SubscriptionType)

    assert_schema_equals(
        schema,
        """
        type Query {
          searchSth: String!
        }

        \"\"\"test test\"\"\"
        type Subscription {
          \"\"\"hello\"\"\"
          notificationReceived: Notification!
        }

        union Notification = Message | User

        type Message {
          id: ID!
          content: String!
          author: String!
        }

        type User {
          id: ID!
          username: String!
        }
        """,
    )

    query = parse("subscription { notificationReceived { ... on Message { id } } }")
    sub = await subscribe(schema, query)

    # Ensure the subscription is an async iterator
    assert hasattr(sub, "__aiter__")

    # Fetch the first result
    result = await sub.__anext__()  # type: ignore

    # Validate the result
    assert not result.errors
    assert result.data == {"notificationReceived": {"id": "1"}}


@pytest.mark.asyncio
async def test_basic_subscription_with_schema(assert_schema_equals):
    class SubscriptionType(GraphQLSubscription):
        __schema__ = gql(
            """
            type Subscription {
                messageAdded: Message!
            }
            """
        )

        @GraphQLSubscription.source("messageAdded", graphql_type=Message)
        @staticmethod
        async def message_added_generator(*_):
            while True:
                yield {"id": "some_id", "content": "message", "author": "Anon"}

        @GraphQLSubscription.resolver("messageAdded")
        @staticmethod
        async def resolve_message_added(message, *_):
            return message

    class QueryType(GraphQLObject):
        @GraphQLObject.field(graphql_type=str)
        @staticmethod
        def search_sth(*_) -> str:
            return "search"

    schema = make_executable_schema(QueryType, SubscriptionType, Message)

    assert_schema_equals(
        schema,
        """
        type Query {
          searchSth: String!
        }

        type Subscription {
          messageAdded: Message!
        }

        type Message {
          id: ID!
          content: String!
          author: String!
        }
        """,
    )

    query = parse("subscription { messageAdded {id content author} }")
    sub = await subscribe(schema, query)

    # Ensure the subscription is an async iterator
    assert hasattr(sub, "__aiter__")

    # Fetch the first result
    result = await sub.__anext__()  # type: ignore

    # Validate the result
    assert not result.errors
    assert result.data == {
        "messageAdded": {"id": "some_id", "content": "message", "author": "Anon"}
    }


@pytest.mark.asyncio
async def test_subscription_with_arguments_with_schema(assert_schema_equals):
    class SubscriptionType(GraphQLSubscription):
        __schema__ = gql(
            """
            type Subscription {
                messageAdded(channel: ID!): Message!
            }
            """
        )

        @GraphQLSubscription.source(
            "messageAdded",
            graphql_type=Message,
        )
        @staticmethod
        async def message_added_generator(*_, channel: GraphQLID):
            while True:
                yield {
                    "id": "some_id",
                    "content": f"message_{channel}",
                    "author": "Anon",
                }

        @GraphQLSubscription.resolver(
            "messageAdded",
        )
        @staticmethod
        async def resolve_message_added(
            message, *_, channel: GraphQLID
        ):  # pylint: disable=unused-argument
            return message

    class QueryType(GraphQLObject):
        @GraphQLObject.field(graphql_type=str)
        @staticmethod
        def search_sth(*_) -> str:
            return "search"

    schema = make_executable_schema(QueryType, SubscriptionType, Message)

    assert_schema_equals(
        schema,
        """
        type Query {
          searchSth: String!
        }

        type Subscription {
          messageAdded(channel: ID!): Message!
        }

        type Message {
          id: ID!
          content: String!
          author: String!
        }
        """,
    )

    query = parse('subscription { messageAdded(channel: "123") {id content author} }')
    sub = await subscribe(schema, query)

    # Ensure the subscription is an async iterator
    assert hasattr(sub, "__aiter__")

    # Fetch the first result
    result = await sub.__anext__()  # type: ignore

    # Validate the result
    assert not result.errors
    assert result.data == {
        "messageAdded": {"id": "some_id", "content": "message_123", "author": "Anon"}
    }


@pytest.mark.asyncio
async def test_multiple_supscriptions_with_schema(assert_schema_equals):
    class SubscriptionType(GraphQLSubscription):
        __schema__ = gql(
            """
            type Subscription {
              messageAdded: Message!
              userJoined: User!
            }
            """
        )

        @GraphQLSubscription.source(
            "messageAdded",
        )
        @staticmethod
        async def message_added_generator(*_):
            while True:
                yield {
                    "id": "some_id",
                    "content": "message",
                    "author": "Anon",
                }

        @GraphQLSubscription.resolver(
            "messageAdded",
        )
        @staticmethod
        async def resolve_message_added(message, *_):
            return message

        @GraphQLSubscription.source(
            "userJoined",
        )
        @staticmethod
        async def user_joined_generator(*_):
            while True:
                yield {
                    "id": "some_id",
                    "username": "username",
                }

        @GraphQLSubscription.resolver(
            "userJoined",
        )
        @staticmethod
        async def resolve_user_joined(user, *_):
            return user

    class QueryType(GraphQLObject):
        @GraphQLObject.field(graphql_type=str)
        @staticmethod
        def search_sth(*_) -> str:
            return "search"

    schema = make_executable_schema(QueryType, SubscriptionType, Message, User)

    assert_schema_equals(
        schema,
        """
        type Query {
          searchSth: String!
        }

        type Subscription {
          messageAdded: Message!
          userJoined: User!
        }

        type Message {
          id: ID!
          content: String!
          author: String!
        }

        type User {
          id: ID!
          username: String!
        }
        """,
    )

    query = parse("subscription { userJoined {id username} }")
    sub = await subscribe(schema, query)

    # Ensure the subscription is an async iterator
    assert hasattr(sub, "__aiter__")

    # Fetch the first result
    result = await sub.__anext__()  # type: ignore

    # Validate the result
    assert not result.errors
    assert result.data == {"userJoined": {"id": "some_id", "username": "username"}}


@pytest.mark.asyncio
async def test_subscription_with_complex_data_with_schema(assert_schema_equals):
    class SubscriptionType(GraphQLSubscription):
        __schema__ = gql(
            """
            type Subscription {
              messagesInChannel(channelId: ID!): [Message!]!
            }
            """
        )

        @GraphQLSubscription.source(
            "messagesInChannel",
        )
        @staticmethod
        async def message_added_generator(
            obj, info, channelId: GraphQLID
        ):  # pylint: disable=unused-argument
            while True:
                yield [
                    {
                        "id": "some_id",
                        "content": f"message_{channelId}",
                        "author": "Anon",
                    }
                ]

        @GraphQLSubscription.resolver(
            "messagesInChannel",
        )
        @staticmethod
        async def resolve_message_added(
            message, *_, channelId: GraphQLID
        ):  # pylint: disable=unused-argument
            return message

    class QueryType(GraphQLObject):
        @GraphQLObject.field(graphql_type=str)
        @staticmethod
        def search_sth(*_) -> str:
            return "search"

    schema = make_executable_schema(QueryType, SubscriptionType, Message)

    assert_schema_equals(
        schema,
        """
        type Query {
          searchSth: String!
        }

        type Subscription {
          messagesInChannel(channelId: ID!): [Message!]!
        }

        type Message {
          id: ID!
          content: String!
          author: String!
        }
        """,
    )

    query = parse(
        'subscription { messagesInChannel(channelId: "123") {id content author} }'
    )
    sub = await subscribe(schema, query)

    # Ensure the subscription is an async iterator
    assert hasattr(sub, "__aiter__")

    # Fetch the first result
    result = await sub.__anext__()  # type: ignore

    # Validate the result
    assert not result.errors
    assert result.data == {
        "messagesInChannel": [
            {"id": "some_id", "content": "message_123", "author": "Anon"}
        ]
    }


@pytest.mark.asyncio
async def test_subscription_with_union_with_schema(assert_schema_equals):
    class SubscriptionType(GraphQLSubscription):
        __schema__ = gql(
            """
            type Subscription {
              notificationReceived(channel: String): Notification!
              name: String
            }
            """
        )
        __aliases__ = {"name": "title"}

        @GraphQLSubscription.resolver("notificationReceived")
        @staticmethod
        async def resolve_message_added(
            message, *_, channel: str  # pylint: disable=unused-argument
        ):
            return message

        @GraphQLSubscription.source(
            "notificationReceived",
            description="my description",
            args={
                "channel": GraphQLObject.argument(
                    description="Lorem ipsum.", default_value="123"
                )
            },
        )
        @staticmethod
        async def message_added_generator(
            *_, channel: str  # pylint: disable=unused-argument
        ):
            while True:
                yield Message(id=1, content="content", author="anon")

    class QueryType(GraphQLObject):
        @GraphQLObject.field(graphql_type=str)
        @staticmethod
        def search_sth(*_) -> str:
            return "search"

    schema = make_executable_schema(QueryType, SubscriptionType, Notification)

    assert_schema_equals(
        schema,
        """
        type Query {
          searchSth: String!
        }

        type Subscription {
          \"\"\"my description\"\"\"
          notificationReceived(
            \"\"\"Lorem ipsum.\"\"\"
            channel: String = "123"
          ): Notification!
          name: String
        }

        union Notification = Message | User

        type Message {
          id: ID!
          content: String!
          author: String!
        }

        type User {
          id: ID!
          username: String!
        }
        """,
    )

    query = parse(
        'subscription { notificationReceived(channel: "hello") '
        "{ ... on Message { id } } }"
    )
    sub = await subscribe(schema, query)

    # Ensure the subscription is an async iterator
    assert hasattr(sub, "__aiter__")

    # Fetch the first result
    result = await sub.__anext__()  # type: ignore

    # Validate the result
    assert not result.errors
    assert result.data == {"notificationReceived": {"id": "1"}}


@pytest.mark.asyncio
async def test_subscription_descriptions_without_schema(assert_schema_equals):
    class SubscriptionType(GraphQLSubscription):
        notification_received: Notification
        __description__ = "test test"

        @GraphQLSubscription.source(
            "notification_received", description="hello", graphql_type=Message
        )
        @staticmethod
        async def message_added_generator(*_):
            while True:
                yield Message(id=1, content="content", author="anon")

        @GraphQLSubscription.resolver(
            "notification_received",
        )
        @staticmethod
        async def resolve_message_added(message: Message, *_):
            return message

    class QueryType(GraphQLObject):
        @GraphQLObject.field(graphql_type=str)
        @staticmethod
        def search_sth(*_) -> str:
            return "search"

    schema = make_executable_schema(QueryType, SubscriptionType)

    assert_schema_equals(
        schema,
        """
        type Query {
          searchSth: String!
        }

        \"\"\"test test\"\"\"
        type Subscription {
          \"\"\"hello\"\"\"
          notificationReceived: Notification!
        }

        union Notification = Message | User

        type Message {
          id: ID!
          content: String!
          author: String!
        }

        type User {
          id: ID!
          username: String!
        }
        """,
    )

    query = parse("subscription { notificationReceived { ... on Message { id } } }")
    sub = await subscribe(schema, query)

    # Ensure the subscription is an async iterator
    assert hasattr(sub, "__aiter__")

    # Fetch the first result
    result = await sub.__anext__()  # type: ignore

    # Validate the result
    assert not result.errors
    assert result.data == {"notificationReceived": {"id": "1"}}
