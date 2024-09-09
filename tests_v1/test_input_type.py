import pytest
from ariadne import SchemaDirectiveVisitor
from graphql import GraphQLError, graphql_sync

from ariadne_graphql_modules.v1 import (
    DeferredType,
    DirectiveType,
    EnumType,
    InputType,
    InterfaceType,
    ObjectType,
    ScalarType,
    make_executable_schema,
)


def test_input_type_raises_attribute_error_when_defined_without_schema(data_regression):
    with pytest.raises(AttributeError) as err:
        # pylint: disable=unused-variable
        class UserInput(InputType):
            pass

    data_regression.check(str(err.value))


def test_input_type_raises_error_when_defined_with_invalid_schema_type(data_regression):
    with pytest.raises(TypeError) as err:
        # pylint: disable=unused-variable
        class UserInput(InputType):
            __schema__ = True

    data_regression.check(str(err.value))


def test_input_type_raises_error_when_defined_with_invalid_schema_str(data_regression):
    with pytest.raises(GraphQLError) as err:
        # pylint: disable=unused-variable
        class UserInput(InputType):
            __schema__ = "inpet UserInput"

    data_regression.check(str(err.value))


def test_input_type_raises_error_when_defined_with_invalid_graphql_type_schema(
    data_regression,
):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class UserInput(InputType):
            __schema__ = """
            type User {
                id: ID!
            }
            """

    data_regression.check(str(err.value))


def test_input_type_raises_error_when_defined_with_multiple_types_schema(
    data_regression,
):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class UserInput(InputType):
            __schema__ = """
            input User

            input Group
            """

    data_regression.check(str(err.value))


def test_input_type_raises_error_when_defined_without_fields(data_regression):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class UserInput(InputType):
            __schema__ = "input User"

    data_regression.check(str(err.value))


def test_input_type_extracts_graphql_name():
    class UserInput(InputType):
        __schema__ = """
        input User {
            id: ID!
        }
        """

    assert UserInput.graphql_name == "User"


def test_input_type_raises_error_when_defined_without_field_type_dependency(
    data_regression,
):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class UserInput(InputType):
            __schema__ = """
            input User {
                id: ID!
                role: Role!
            }
            """

    data_regression.check(str(err.value))


def test_input_type_verifies_field_dependency():
    # pylint: disable=unused-variable
    class RoleEnum(EnumType):
        __schema__ = """
        enum Role {
            USER
            ADMIN
        }
        """

    class UserInput(InputType):
        __schema__ = """
        input User {
            id: ID!
            role: Role!
        }
        """
        __requires__ = [RoleEnum]


def test_input_type_verifies_circular_dependency():
    # pylint: disable=unused-variable
    class UserInput(InputType):
        __schema__ = """
        input User {
            id: ID!
            patron: User
        }
        """


def test_input_type_verifies_circular_dependency_using_deferred_type():
    # pylint: disable=unused-variable
    class GroupInput(InputType):
        __schema__ = """
        input Group {
            id: ID!
            patron: User
        }
        """
        __requires__ = [DeferredType("User")]

    class UserInput(InputType):
        __schema__ = """
        input User {
            id: ID!
            group: Group
        }
        """
        __requires__ = [GroupInput]


def test_input_type_can_be_extended_with_new_fields():
    # pylint: disable=unused-variable
    class UserInput(InputType):
        __schema__ = """
        input User {
            id: ID!
        }
        """

    class ExtendUserInput(InputType):
        __schema__ = """
        extend input User {
            name: String!
        }
        """
        __requires__ = [UserInput]


def test_input_type_can_be_extended_with_directive():
    # pylint: disable=unused-variable
    class ExampleDirective(DirectiveType):
        __schema__ = "directive @example on INPUT_OBJECT"
        __visitor__ = SchemaDirectiveVisitor

    class UserInput(InputType):
        __schema__ = """
        input User {
            id: ID!
        }
        """

    class ExtendUserInput(InputType):
        __schema__ = """
        extend input User @example
        """
        __requires__ = [UserInput, ExampleDirective]


def test_input_type_raises_error_when_defined_without_extended_dependency(
    data_regression,
):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class ExtendUserInput(InputType):
            __schema__ = """
            extend input User {
                name: String!
            }
            """

    data_regression.check(str(err.value))


def test_input_type_raises_error_when_extended_dependency_is_wrong_type(
    data_regression,
):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class ExampleInterface(InterfaceType):
            __schema__ = """
            interface User {
                id: ID!
            }
            """

        class ExtendUserInput(InputType):
            __schema__ = """
            extend input User {
                name: String!
            }
            """
            __requires__ = [ExampleInterface]

    data_regression.check(str(err.value))


def test_input_type_raises_error_when_defined_with_args_map_for_nonexisting_field(
    data_regression,
):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class UserInput(InputType):
            __schema__ = """
            input User {
                id: ID!
            }
            """
            __args__ = {
                "fullName": "full_name",
            }

    data_regression.check(str(err.value))


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


schema = make_executable_schema(QueryType)


def test_input_type_maps_args_to_python_dict_keys():
    result = graphql_sync(schema, '{ reprInput(input: {id: "1", fullName: "Alice"}) }')
    assert result.data == {
        "reprInput": {"id": "1", "full_name": "Alice"},
    }
