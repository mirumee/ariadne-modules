from ariadne_graphql_modules.next import (
    GraphQLID,
    GraphQLObject,
    GraphQLUnion,
)
from ariadne_graphql_modules.next.graphql_union.validators import (
    validate_union_type_with_schema,
)
import pytest


class UserType(GraphQLObject):
    id: GraphQLID
    username: str


class CommentType(GraphQLObject):
    id: GraphQLID
    content: str


class PostType(GraphQLObject):
    id: GraphQLID
    content: str


def test_missing_type_in_schema(snapshot):
    with pytest.raises(ValueError) as exc_info:

        class MyUnion(GraphQLUnion):
            __types__ = [UserType, CommentType, PostType]
            __schema__ = """
            union MyUnion = User
            """

        validate_union_type_with_schema(MyUnion)
    snapshot.assert_match(str(exc_info.value))


def test_missing_type_in_types(snapshot):
    with pytest.raises(ValueError) as exc_info:

        class MyUnion(GraphQLUnion):
            __types__ = [UserType]
            __schema__ = """
            union MyUnion = User | Comment
            """

        validate_union_type_with_schema(MyUnion)
    snapshot.assert_match(str(exc_info.value))


def test_all_types_present():
    class MyUnion(GraphQLUnion):
        __types__ = [UserType, CommentType]
        __schema__ = """
        union MyUnion = User | Comment
        """

    try:
        validate_union_type_with_schema(MyUnion)
    except ValueError as e:
        pytest.fail(f"Unexpected ValueError raised: {e}")
