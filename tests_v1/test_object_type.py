import pytest
from ariadne import SchemaDirectiveVisitor
from graphql import GraphQLError, graphql_sync

from ariadne_graphql_modules.v1 import (
    DeferredType,
    DirectiveType,
    InterfaceType,
    ObjectType,
    make_executable_schema,
)


def test_object_type_raises_attribute_error_when_defined_without_schema(
    data_regression,
):
    with pytest.raises(AttributeError) as err:
        # pylint: disable=unused-variable
        class UserType(ObjectType):
            pass

    data_regression.check(str(err.value))


def test_object_type_raises_error_when_defined_with_invalid_schema_type(
    data_regression,
):
    with pytest.raises(TypeError) as err:
        # pylint: disable=unused-variable
        class UserType(ObjectType):
            __schema__ = True

    data_regression.check(str(err.value))


def test_object_type_raises_error_when_defined_with_invalid_schema_str(data_regression):
    with pytest.raises(GraphQLError) as err:
        # pylint: disable=unused-variable
        class UserType(ObjectType):
            __schema__ = "typo User"

    data_regression.check(str(err.value))


def test_object_type_raises_error_when_defined_with_invalid_graphql_type_schema(
    data_regression,
):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class UserType(ObjectType):
            __schema__ = "scalar DateTime"

    data_regression.check(str(err.value))


def test_object_type_raises_error_when_defined_with_multiple_types_schema(
    data_regression,
):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class UserType(ObjectType):
            __schema__ = """
            type User

            type Group
            """

    data_regression.check(str(err.value))


def test_object_type_raises_error_when_defined_without_fields(data_regression):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class UserType(ObjectType):
            __schema__ = "type User"

    data_regression.check(str(err.value))


def test_object_type_extracts_graphql_name():
    class GroupType(ObjectType):
        __schema__ = """
        type Group {
            id: ID!
        }
        """

    assert GroupType.graphql_name == "Group"


def test_object_type_accepts_all_builtin_scalar_types():
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


def test_object_type_raises_error_when_defined_without_return_type_dependency(
    data_regression,
):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class UserType(ObjectType):
            __schema__ = """
            type User {
                group: Group
                groups: [Group!]
            }
            """

    data_regression.check(str(err.value))


def test_object_type_verifies_field_dependency():
    # pylint: disable=unused-variable
    class GroupType(ObjectType):
        __schema__ = """
        type Group {
            id: ID!
        }
        """

    class UserType(ObjectType):
        __schema__ = """
        type User {
            group: Group
            groups: [Group!]
        }
        """
        __requires__ = [GroupType]


def test_object_type_verifies_circular_dependency():
    # pylint: disable=unused-variable
    class UserType(ObjectType):
        __schema__ = """
        type User {
            follows: User
        }
        """


def test_object_type_raises_error_when_defined_without_argument_type_dependency(
    data_regression,
):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class UserType(ObjectType):
            __schema__ = """
            type User {
                actions(input: UserInput): [String!]!
            }
            """

    data_regression.check(str(err.value))


def test_object_type_verifies_circular_dependency_using_deferred_type():
    # pylint: disable=unused-variable
    class GroupType(ObjectType):
        __schema__ = """
        type Group {
            id: ID!
            users: [User]
        }
        """
        __requires__ = [DeferredType("User")]

    class UserType(ObjectType):
        __schema__ = """
        type User {
            group: Group
        }
        """
        __requires__ = [GroupType]


def test_object_type_can_be_extended_with_new_fields():
    # pylint: disable=unused-variable
    class UserType(ObjectType):
        __schema__ = """
        type User {
            id: ID!
        }
        """

    class ExtendUserType(ObjectType):
        __schema__ = """
        extend type User {
            name: String
        }
        """
        __requires__ = [UserType]


def test_object_type_can_be_extended_with_directive():
    # pylint: disable=unused-variable
    class ExampleDirective(DirectiveType):
        __schema__ = "directive @example on OBJECT"
        __visitor__ = SchemaDirectiveVisitor

    class UserType(ObjectType):
        __schema__ = """
        type User {
            id: ID!
        }
        """

    class ExtendUserType(ObjectType):
        __schema__ = """
        extend type User @example
        """
        __requires__ = [UserType, ExampleDirective]


def test_object_type_can_be_extended_with_interface():
    # pylint: disable=unused-variable
    class ExampleInterface(InterfaceType):
        __schema__ = """
        interface Interface {
            id: ID!
        }
        """

    class UserType(ObjectType):
        __schema__ = """
        type User {
            id: ID!
        }
        """

    class ExtendUserType(ObjectType):
        __schema__ = """
        extend type User implements Interface
        """
        __requires__ = [UserType, ExampleInterface]


def test_object_type_raises_error_when_defined_without_extended_dependency(
    data_regression,
):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class ExtendUserType(ObjectType):
            __schema__ = """
            extend type User {
                name: String
            }
            """

    data_regression.check(str(err.value))


def test_object_type_raises_error_when_extended_dependency_is_wrong_type(
    data_regression,
):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class ExampleInterface(InterfaceType):
            __schema__ = """
            interface Example {
                id: ID!
            }
            """

        class ExampleType(ObjectType):
            __schema__ = """
            extend type Example {
                name: String
            }
            """
            __requires__ = [ExampleInterface]

    data_regression.check(str(err.value))


def test_object_type_raises_error_when_defined_with_alias_for_nonexisting_field(
    data_regression,
):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class UserType(ObjectType):
            __schema__ = """
            type User {
                name: String
            }
            """
            __aliases__ = {
                "joinedDate": "joined_date",
            }

    data_regression.check(str(err.value))


def test_object_type_raises_error_when_defined_with_resolver_for_nonexisting_field(
    data_regression,
):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class UserType(ObjectType):
            __schema__ = """
            type User {
                name: String
            }
            """

            @staticmethod
            def resolve_group(*_):
                return None

    data_regression.check(str(err.value))


def test_object_type_raises_error_when_defined_with_field_args_for_nonexisting_field(
    data_regression,
):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class UserType(ObjectType):
            __schema__ = """
            type User {
                name: String
            }
            """
            __fields_args__ = {"group": {}}

    data_regression.check(str(err.value))


def test_object_type_raises_error_when_defined_with_field_args_for_nonexisting_arg(
    data_regression,
):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class UserType(ObjectType):
            __schema__ = """
            type User {
                name: String
            }
            """
            __fields_args__ = {"name": {"arg": "arg2"}}

    data_regression.check(str(err.value))


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


schema = make_executable_schema(QueryType)


def test_object_resolves_field_with_default_resolver():
    result = graphql_sync(schema, "{ field }", root_value={"field": "Hello!"})
    assert result.data["field"] == "Hello!"


def test_object_resolves_field_with_custom_resolver():
    result = graphql_sync(schema, "{ other }")
    assert result.data["other"] == "Word Up!"


def test_object_resolves_field_with_aliased_default_resolver():
    result = graphql_sync(
        schema, "{ firstField }", root_value={"first_field": "Howdy?"}
    )
    assert result.data["firstField"] == "Howdy?"


def test_object_resolves_field_with_aliased_custom_resolver():
    result = graphql_sync(schema, "{ secondField }", root_value={"secondField": "Hey!"})
    assert result.data["secondField"] == "Obj: Hey!"


def test_object_resolves_field_with_arg_out_name_customized():
    result = graphql_sync(schema, '{ fieldWithArg(someArg: "test") }')
    assert result.data["fieldWithArg"] == "test"
