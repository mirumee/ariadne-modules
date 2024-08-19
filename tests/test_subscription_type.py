import pytest
from ariadne import SchemaDirectiveVisitor
from graphql import GraphQLError, build_schema

from ariadne_graphql_modules import (
    DirectiveType,
    InterfaceType,
    ObjectType,
    SubscriptionType,
)


def test_subscription_type_raises_attribute_error_when_defined_without_schema(
    data_regression,
):
    with pytest.raises(AttributeError) as err:
        # pylint: disable=unused-variable
        class UsersSubscription(SubscriptionType):
            pass

    data_regression.check(str(err.value))


def test_subscription_type_raises_error_when_defined_with_invalid_schema_type(
    data_regression,
):
    with pytest.raises(TypeError) as err:
        # pylint: disable=unused-variable
        class UsersSubscription(SubscriptionType):
            __schema__ = True

    data_regression.check(str(err.value))


def test_subscription_type_raises_error_when_defined_with_invalid_schema_str(
    data_regression,
):
    with pytest.raises(GraphQLError) as err:
        # pylint: disable=unused-variable
        class UsersSubscription(SubscriptionType):
            __schema__ = "typo Subscription"

    data_regression.check(str(err.value))


def test_subscription_type_raises_error_when_defined_with_invalid_graphql_type_schema(
    data_regression,
):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class UsersSubscription(SubscriptionType):
            __schema__ = "scalar Subscription"

    data_regression.check(str(err.value))


def test_subscription_type_raises_error_when_defined_with_invalid_graphql_type_name(
    data_regression,
):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class UsersSubscription(SubscriptionType):
            __schema__ = "type Other"

    data_regression.check(str(err.value))


def test_subscription_type_raises_error_when_defined_without_fields(data_regression):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class UsersSubscription(SubscriptionType):
            __schema__ = "type Subscription"

    data_regression.check(str(err.value))


def test_subscription_type_extracts_graphql_name():
    class UsersSubscription(SubscriptionType):
        __schema__ = """
        type Subscription {
            thread: ID!
        }
        """

    assert UsersSubscription.graphql_name == "Subscription"


def test_subscription_type_raises_error_when_defined_without_return_type_dependency(
    data_regression,
):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class ChatSubscription(SubscriptionType):
            __schema__ = """
            type Subscription {
                chat: Chat
                Chats: [Chat!]
            }
            """

    data_regression.check(str(err.value))


def test_subscription_type_verifies_field_dependency():
    # pylint: disable=unused-variable
    class ChatType(ObjectType):
        __schema__ = """
        type Chat {
            id: ID!
        }
        """

    class ChatSubscription(SubscriptionType):
        __schema__ = """
        type Subscription {
            chat: Chat
            Chats: [Chat!]
        }
        """
        __requires__ = [ChatType]


def test_subscription_type_raises_error_when_defined_without_argument_type_dependency(
    data_regression,
):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class ChatSubscription(SubscriptionType):
            __schema__ = """
            type Subscription {
                chat(input: ChannelInput): [String!]!
            }
            """

    data_regression.check(str(err.value))


def test_subscription_type_can_be_extended_with_new_fields():
    # pylint: disable=unused-variable
    class ChatSubscription(SubscriptionType):
        __schema__ = """
        type Subscription {
            chat: ID!
        }
        """

    class ExtendChatSubscription(SubscriptionType):
        __schema__ = """
        extend type Subscription {
            thread: ID!
        }
        """
        __requires__ = [ChatSubscription]


def test_subscription_type_can_be_extended_with_directive():
    # pylint: disable=unused-variable
    class ExampleDirective(DirectiveType):
        __schema__ = "directive @example on OBJECT"
        __visitor__ = SchemaDirectiveVisitor

    class ChatSubscription(SubscriptionType):
        __schema__ = """
        type Subscription {
            chat: ID!
        }
        """

    class ExtendChatSubscription(SubscriptionType):
        __schema__ = "extend type Subscription @example"
        __requires__ = [ChatSubscription, ExampleDirective]


def test_subscription_type_can_be_extended_with_interface():
    # pylint: disable=unused-variable
    class ExampleInterface(InterfaceType):
        __schema__ = """
        interface Interface {
            threads: ID!
        }
        """

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


def test_subscription_type_raises_error_when_defined_without_extended_dependency(
    data_regression,
):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class ExtendChatSubscription(SubscriptionType):
            __schema__ = """
            extend type Subscription {
                thread: ID!
            }
            """

    data_regression.check(str(err.value))


def test_subscription_type_raises_error_when_extended_dependency_is_wrong_type(
    data_regression,
):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class ExampleInterface(InterfaceType):
            __schema__ = """
            interface Subscription {
                id: ID!
            }
            """

        class ExtendChatSubscription(SubscriptionType):
            __schema__ = """
            extend type Subscription {
                thread: ID!
            }
            """
            __requires__ = [ExampleInterface]

    data_regression.check(str(err.value))


def test_subscription_type_raises_error_when_defined_with_alias_for_nonexisting_field(
    data_regression,
):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class ChatSubscription(SubscriptionType):
            __schema__ = """
            type Subscription {
                chat: ID!
            }
            """
            __aliases__ = {
                "userAlerts": "user_alerts",
            }

    data_regression.check(str(err.value))


def test_subscription_type_raises_error_when_defined_with_resolver_for_nonexisting_field(
    data_regression,
):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class ChatSubscription(SubscriptionType):
            __schema__ = """
            type Subscription {
                chat: ID!
            }
            """

            @staticmethod
            def resolve_group(*_):
                return None

    data_regression.check(str(err.value))


def test_subscription_type_raises_error_when_defined_with_sub_for_nonexisting_field(
    data_regression,
):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class ChatSubscription(SubscriptionType):
            __schema__ = """
            type Subscription {
                chat: ID!
            }
            """

            @staticmethod
            def subscribe_group(*_):
                return None

    data_regression.check(str(err.value))


def test_subscription_type_binds_resolver_and_subscriber_to_schema():
    schema = build_schema(
        """
            type Query {
                hello: String
            }

            type Subscription {
                chat: ID!
            }
        """
    )

    class ChatSubscription(SubscriptionType):
        __schema__ = """
        type Subscription {
            chat: ID!
        }
        """

        @staticmethod
        def resolve_chat(*_):
            return None

        @staticmethod
        def subscribe_chat(*_):
            return None

    ChatSubscription.__bind_to_schema__(schema)

    field = schema.type_map.get("Subscription").fields["chat"]
    assert field.resolve is ChatSubscription.resolve_chat
    assert field.subscribe is ChatSubscription.subscribe_chat
