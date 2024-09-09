import pytest
from graphql import GraphQLError, graphql_sync

from ariadne_graphql_modules.v1 import (
    MutationType,
    ObjectType,
    make_executable_schema,
)


def test_mutation_type_raises_attribute_error_when_defined_without_schema(
    data_regression,
):
    with pytest.raises(AttributeError) as err:
        # pylint: disable=unused-variable
        class UserCreateMutation(MutationType):
            pass

    data_regression.check(str(err.value))


def test_mutation_type_raises_error_when_defined_with_invalid_schema_type(
    data_regression,
):
    with pytest.raises(TypeError) as err:
        # pylint: disable=unused-variable
        class UserCreateMutation(MutationType):
            __schema__ = True

    data_regression.check(str(err.value))


def test_object_type_raises_error_when_defined_with_invalid_schema_str(data_regression):
    with pytest.raises(GraphQLError) as err:
        # pylint: disable=unused-variable
        class UserCreateMutation(MutationType):
            __schema__ = "typo User"

    data_regression.check(str(err.value))


def test_mutation_type_raises_error_when_defined_with_invalid_graphql_type_schema(
    data_regression,
):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class UserCreateMutation(MutationType):
            __schema__ = "scalar DateTime"

    data_regression.check(str(err.value))


def test_mutation_type_raises_error_when_defined_with_multiple_types_schema(
    data_regression,
):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class UserCreateMutation(MutationType):
            __schema__ = """
            type User

            type Group
            """

    data_regression.check(str(err.value))


def test_mutation_type_raises_error_when_defined_for_different_type_name(
    data_regression,
):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class UserCreateMutation(MutationType):
            __schema__ = """
            type User {
                id: ID!
            }
            """

    data_regression.check(str(err.value))


def test_mutation_type_raises_error_when_defined_without_fields(data_regression):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class UserCreateMutation(MutationType):
            __schema__ = """
            type Mutation
            """

    data_regression.check(str(err.value))


def test_mutation_type_raises_error_when_defined_with_multiple_fields(data_regression):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class UserCreateMutation(MutationType):
            __schema__ = """
            type Mutation {
                userCreate(name: String!): Boolean!
                userUpdate(id: ID!, name: String!): Boolean!
            }
            """

    data_regression.check(str(err.value))


def test_mutation_type_raises_error_when_defined_without_resolve_mutation_attr(
    data_regression,
):
    with pytest.raises(AttributeError) as err:
        # pylint: disable=unused-variable
        class UserCreateMutation(MutationType):
            __schema__ = """
            type Mutation {
                userCreate(name: String!): Boolean!
            }
            """

    data_regression.check(str(err.value))


def test_mutation_type_raises_error_when_defined_without_callable_resolve_mutation_attr(
    data_regression,
):
    with pytest.raises(TypeError) as err:
        # pylint: disable=unused-variable
        class UserCreateMutation(MutationType):
            __schema__ = """
            type Mutation {
                userCreate(name: String!): Boolean!
            }
            """

            resolve_mutation = True

    data_regression.check(str(err.value))


def test_mutation_type_raises_error_when_defined_without_return_type_dependency(
    data_regression,
):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class UserCreateMutation(MutationType):
            __schema__ = """
            type Mutation {
                userCreate(name: String!): UserCreateResult!
            }
            """

            @staticmethod
            def resolve_mutation(*_args):
                pass

    data_regression.check(str(err.value))


def test_mutation_type_verifies_field_dependency():
    # pylint: disable=unused-variable
    class UserCreateResult(ObjectType):
        __schema__ = """
        type UserCreateResult {
            errors: [String!]
        }
        """

    class UserCreateMutation(MutationType):
        __schema__ = """
        type Mutation {
            userCreate(name: String!): UserCreateResult!
        }
        """
        __requires__ = [UserCreateResult]

        @staticmethod
        def resolve_mutation(*_args):
            pass


def test_mutation_type_raises_error_when_defined_with_nonexistant_args(
    data_regression,
):
    with pytest.raises(ValueError) as err:
        # pylint: disable=unused-variable
        class UserCreateMutation(MutationType):
            __schema__ = """
            type Mutation {
                userCreate(name: String!): Boolean!
            }
            """
            __args__ = {"realName": "real_name"}

            @staticmethod
            def resolve_mutation(*_args):
                pass

    data_regression.check(str(err.value))


class QueryType(ObjectType):
    __schema__ = """
    type Query {
        field: String!
    }
    """


class ResultType(ObjectType):
    __schema__ = """
    type Result {
        error: String
        total: Int
    }
    """


class SumMutation(MutationType):
    __schema__ = """
    type Mutation {
        sum(a: Int!, b: Int!): Result!
    }
    """
    __requires__ = [ResultType]

    @staticmethod
    def resolve_mutation(*_, a: int, b: int):
        return {"total": a + b}


class DivideMutation(MutationType):
    __schema__ = """
    type Mutation {
        divide(a: Int!, b: Int!): Result!
    }
    """
    __requires__ = [ResultType]

    @staticmethod
    def resolve_mutation(*_, a: int, b: int):
        if a == 0 or b == 0:
            return {"error": "Division by zero"}

        return {"total": a / b}


class SplitMutation(MutationType):
    __schema__ = """
    type Mutation {
        split(strToSplit: String!): [String!]!
    }
    """
    __args__ = {"strToSplit": "split_str"}

    @staticmethod
    def resolve_mutation(*_, split_str: str):
        return split_str.split()


schema = make_executable_schema(QueryType, SumMutation, DivideMutation, SplitMutation)


def test_sum_mutation_resolves_to_result():
    query = """
    mutation {
        sum(a: 5, b: 3) {
            total
            error
        }
    }
    """
    result = graphql_sync(schema, query)
    assert result.data == {
        "sum": {
            "total": 8,
            "error": None,
        },
    }


def test_divide_mutation_resolves_to_result():
    query = """
    mutation {
        divide(a: 6, b: 3) {
            total
            error
        }
    }
    """
    result = graphql_sync(schema, query)
    assert result.data == {
        "divide": {
            "total": 2,
            "error": None,
        },
    }


def test_divide_mutation_resolves_to_error_result():
    query = """
    mutation {
        divide(a: 6, b: 0) {
            total
            error
        }
    }
    """
    result = graphql_sync(schema, query)
    assert result.data == {
        "divide": {
            "total": None,
            "error": "Division by zero",
        },
    }


def test_split_mutation_uses_arg_mapping():
    query = """
    mutation {
        split(strToSplit: "a b c")
    }
    """
    result = graphql_sync(schema, query)
    assert result.data == {
        "split": ["a", "b", "c"],
    }
