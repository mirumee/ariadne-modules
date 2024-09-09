import pytest

from ariadne_graphql_modules import (
    GraphQLID,
    GraphQLObject,
    GraphQLUnion,
)
from ariadne_graphql_modules.union_type.validators import (
    validate_union_type_with_schema,
)


class UserType(GraphQLObject):
    id: GraphQLID
    username: str


class CommentType(GraphQLObject):
    id: GraphQLID
    content: str


class PostType(GraphQLObject):
    id: GraphQLID
    content: str


def test_missing_type_in_schema(data_regression):
    with pytest.raises(ValueError) as exc_info:

        class MyUnion(GraphQLUnion):
            __types__ = [UserType, CommentType, PostType]
            __schema__ = """
            union MyUnion = User
            """

        validate_union_type_with_schema(MyUnion)
    data_regression.check(str(exc_info.value))


def test_missing_type_in_types(data_regression):
    with pytest.raises(ValueError) as exc_info:

        class MyUnion(GraphQLUnion):
            __types__ = [UserType]
            __schema__ = """
            union MyUnion = User | Comment
            """

        validate_union_type_with_schema(MyUnion)
    data_regression.check(str(exc_info.value))


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
