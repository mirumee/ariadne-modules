import pytest

from ariadne_graphql_modules.next import (
    GraphQLID,
    GraphQLObject,
    GraphQLInterface,
    make_executable_schema,
)


def test_interface_with_different_types(snapshot):
    with pytest.raises(TypeError) as exc_info:

        class UserInterface(GraphQLInterface):
            summary: str
            score: str

        class UserType(GraphQLObject):
            name: str
            summary: str
            score: int

            __implements__ = [UserInterface]

        make_executable_schema(UserType, UserInterface)

    snapshot.assert_match(str(exc_info.value))


def test_missing_interface_implementation(snapshot):
    with pytest.raises(TypeError) as exc_info:

        class RequiredInterface(GraphQLInterface):
            required_field: str

        class ImplementingType(GraphQLObject):
            optional_field: str

            __implements__ = [RequiredInterface]

        make_executable_schema(ImplementingType, RequiredInterface)

    snapshot.assert_match(str(exc_info.value))


def test_interface_no_interface_in_schema(snapshot):
    with pytest.raises(TypeError) as exc_info:

        class BaseInterface(GraphQLInterface):
            id: GraphQLID

        class UserType(GraphQLObject):
            id: GraphQLID
            username: str
            email: str

            __implements__ = [BaseInterface]

        make_executable_schema(UserType)

    snapshot.assert_match(str(exc_info.value))
