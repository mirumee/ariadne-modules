import pytest

from ariadne_graphql_modules import (
    GraphQLID,
    GraphQLObject,
    GraphQLInterface,
    make_executable_schema,
)


def test_interface_no_interface_in_schema(data_regression):
    with pytest.raises(TypeError) as exc_info:

        class BaseInterface(GraphQLInterface):
            id: GraphQLID

        class UserType(GraphQLObject, BaseInterface):
            username: str
            email: str

        make_executable_schema(UserType)

    data_regression.check(str(exc_info.value))
