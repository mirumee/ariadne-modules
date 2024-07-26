from ariadne import gql
import pytest
from ariadne_graphql_modules.next import (
    GraphQLID,
    GraphQLObject,
    GraphQLSubscription,
    GraphQLUnion,
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
async def test_undefined_name_without_schema(snapshot):
    with pytest.raises(ValueError) as exc_info:

        class SubscriptionType(GraphQLSubscription):
            message_added: Message

            @GraphQLSubscription.source("messageAdded")
            async def message_added_generator(obj, info):
                while True:
                    yield {"id": "some_id", "content": "message", "author": "Anon"}

    snapshot.assert_match(str(exc_info.value))


@pytest.mark.asyncio
async def test_field_name_not_str_without_schema(snapshot):
    with pytest.raises(ValueError) as exc_info:

        class SubscriptionType(GraphQLSubscription):
            message_added: Message

            @GraphQLSubscription.source(23)
            async def message_added_generator(obj, info):
                while True:
                    yield {"id": "some_id", "content": "message", "author": "Anon"}

    snapshot.assert_match(str(exc_info.value))


@pytest.mark.asyncio
async def test_multiple_sources_without_schema(snapshot):
    with pytest.raises(ValueError) as exc_info:

        class SubscriptionType(GraphQLSubscription):
            message_added: Message

            @GraphQLSubscription.source("message_added")
            async def message_added_generator(obj, info):
                while True:
                    yield {"id": "some_id", "content": "message", "author": "Anon"}

            @GraphQLSubscription.source("message_added")
            async def message_added_generator_2(obj, info):
                while True:
                    yield {"id": "some_id", "content": "message", "author": "Anon"}

    snapshot.assert_match(str(exc_info.value))


@pytest.mark.asyncio
async def test_description_not_str_without_schema(snapshot):
    with pytest.raises(ValueError) as exc_info:

        class SubscriptionType(GraphQLSubscription):
            message_added: Message

            @GraphQLSubscription.source("message_added", description=12)
            async def message_added_generator(obj, info):
                while True:
                    yield {"id": "some_id", "content": "message", "author": "Anon"}

    snapshot.assert_match(str(exc_info.value))


@pytest.mark.asyncio
async def test_source_args_field_arg_not_dict_without_schema(snapshot):
    with pytest.raises(ValueError) as exc_info:

        class SubscriptionType(GraphQLSubscription):
            message_added: Message

            @GraphQLSubscription.source(
                "message_added",
                args={"channel": 123},
            )
            async def message_added_generator(obj, info):
                while True:
                    yield {"id": "some_id", "content": "message", "author": "Anon"}

    snapshot.assert_match(str(exc_info.value))


@pytest.mark.asyncio
async def test_source_args_not_dict_without_schema(snapshot):
    with pytest.raises(ValueError) as exc_info:

        class SubscriptionType(GraphQLSubscription):
            message_added: Message

            @GraphQLSubscription.source(
                "message_added",
                args=123,
            )
            async def message_added_generator(obj, info):
                while True:
                    yield {"id": "some_id", "content": "message", "author": "Anon"}

    snapshot.assert_match(str(exc_info.value))


@pytest.mark.asyncio
async def test_source_for_undefined_field_with_schema(snapshot):
    with pytest.raises(ValueError) as exc_info:

        class SubscriptionType(GraphQLSubscription):
            __schema__ = gql(
                """
                type Subscription {
                    messageAdded: Message!
                }
                """
            )

            @GraphQLSubscription.source("message_added")
            async def message_added_generator(obj, info):
                while True:
                    yield {"id": "some_id", "content": "message", "author": "Anon"}

    snapshot.assert_match(str(exc_info.value))


@pytest.mark.asyncio
async def test_multiple_sourced_for_field_with_schema(snapshot):
    with pytest.raises(ValueError) as exc_info:

        class SubscriptionType(GraphQLSubscription):
            __schema__ = gql(
                """
                type Subscription {
                    messageAdded: Message!
                }
                """
            )

            @GraphQLSubscription.source("messageAdded")
            async def message_added_generator(obj, info):
                while True:
                    yield {"id": "some_id", "content": "message", "author": "Anon"}

            @GraphQLSubscription.source("messageAdded")
            async def message_added_generator_2(obj, info):
                while True:
                    yield {"id": "some_id", "content": "message", "author": "Anon"}

    snapshot.assert_match(str(exc_info.value))


@pytest.mark.asyncio
async def test_multiple_descriptions_for_source_with_schema(snapshot):
    with pytest.raises(ValueError) as exc_info:

        class SubscriptionType(GraphQLSubscription):
            __schema__ = gql(
                """
                type Subscription {
                    \"\"\"Hello!\"\"\"
                    messageAdded: Message!
                }
                """
            )

            @GraphQLSubscription.source("messageAdded", description="hello")
            async def message_added_generator(obj, info):
                while True:
                    yield {"id": "some_id", "content": "message", "author": "Anon"}

    snapshot.assert_match(str(exc_info.value))


@pytest.mark.asyncio
async def test_invalid_arg_name_in_source_with_schema(snapshot):
    with pytest.raises(ValueError) as exc_info:

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
                args={"channelID": GraphQLObject.argument(description="Lorem ipsum.")},
            )
            async def message_added_generator(obj, info, channel):
                while True:
                    yield {"id": "some_id", "content": "message", "author": "Anon"}

    snapshot.assert_match(str(exc_info.value))


@pytest.mark.asyncio
async def test_arg_with_name_in_source_with_schema(snapshot):
    with pytest.raises(ValueError) as exc_info:

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
                args={
                    "channel": GraphQLObject.argument(
                        name="channelID", description="Lorem ipsum."
                    )
                },
            )
            async def message_added_generator(obj, info, channel):
                while True:
                    yield {"id": "some_id", "content": "message", "author": "Anon"}

    snapshot.assert_match(str(exc_info.value))


@pytest.mark.asyncio
async def test_arg_with_type_in_source_with_schema(snapshot):
    with pytest.raises(ValueError) as exc_info:

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
                args={
                    "channel": GraphQLObject.argument(
                        type=str, description="Lorem ipsum."
                    )
                },
            )
            async def message_added_generator(obj, info, channel):
                while True:
                    yield {"id": "some_id", "content": "message", "author": "Anon"}

    snapshot.assert_match(str(exc_info.value))


@pytest.mark.asyncio
async def test_arg_with_description_in_source_with_schema(snapshot):
    with pytest.raises(ValueError) as exc_info:

        class SubscriptionType(GraphQLSubscription):
            __schema__ = gql(
                """
                type Subscription {
                    messageAdded(
                      \"\"\"Lorem ipsum.\"\"\"
                      channel: ID!
                    ): Message!
                }
                """
            )

            @GraphQLSubscription.source(
                "messageAdded",
                args={
                    "channel": GraphQLObject.argument(
                        type=str, description="Lorem ipsum."
                    )
                },
            )
            async def message_added_generator(obj, info, channel):
                while True:
                    yield {"id": "some_id", "content": "message", "author": "Anon"}

    snapshot.assert_match(str(exc_info.value))
