# pylint: disable=unused-variable
from typing import Optional

import pytest

from ariadne_graphql_modules import (
    GraphQLID,
    GraphQLInterface,
    GraphQLObject,
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


def test_interface_with_schema_object_with_no_schema(data_regression):
    with pytest.raises(ValueError) as exc_info:

        class UserInterface(GraphQLInterface):
            __schema__: Optional[str] = """
            interface UserInterface {
                summary: String!
                score: Int!
            }
            """

            @GraphQLInterface.resolver("score")
            @staticmethod
            def resolve_score(*_):
                return 2211

        class UserType(GraphQLObject, UserInterface):
            name: str

    data_regression.check(str(exc_info.value))
