from typing import Union

import pytest
from ariadne import QueryType, SchemaDirectiveVisitor
from graphql import (
    GraphQLField,
    GraphQLInterfaceType,
    GraphQLObjectType,
    default_field_resolver,
    graphql_sync,
)

from ariadne_graphql_modules import GraphQLObject, make_executable_schema


def test_executable_schema_from_vanilla_schema_definition(assert_schema_equals):
    query_type = QueryType()
    query_type.set_field("message", lambda *_: "Hello world!")

    schema = make_executable_schema(
        """
        type Query {
          message: String!
        }
        """,
        query_type,
    )

    assert_schema_equals(
        schema,
        """
        type Query {
          message: String!
        }
        """,
    )

    result = graphql_sync(schema, "{ message }")

    assert not result.errors
    assert result.data == {"message": "Hello world!"}


def test_executable_schema_from_combined_vanilla_and_new_schema_definition(
    assert_schema_equals,
):
    class UserType(GraphQLObject):
        name: str
        email: str

    query_type = QueryType()
    query_type.set_field(
        "user", lambda *_: UserType(name="Bob", email="test@example.com")
    )

    schema = make_executable_schema(
        """
        type Query {
          user: User!
        }
        """,
        query_type,
        UserType,
    )

    assert_schema_equals(
        schema,
        """
        type Query {
          user: User!
        }

        type User {
          name: String!
          email: String!
        }
        """,
    )

    result = graphql_sync(schema, "{ user { name email } }")

    assert not result.errors
    assert result.data == {
        "user": {"name": "Bob", "email": "test@example.com"},
    }


def test_executable_schema_with_merged_roots(assert_schema_equals):
    class FirstRoot(GraphQLObject):
        __graphql_name__ = "Query"

        name: str
        surname: str

    class SecondRoot(GraphQLObject):
        __graphql_name__ = "Query"

        message: str

    class ThirdRoot(GraphQLObject):
        __graphql_name__ = "Query"

        score: int

    schema = make_executable_schema([FirstRoot, SecondRoot, ThirdRoot])

    assert_schema_equals(
        schema,
        """
        type Query {
          message: String!
          name: String!
          score: Int!
          surname: String!
        }
        """,
    )


def test_executable_schema_with_merged_object_and_vanilla_roots(assert_schema_equals):
    class FirstRoot(GraphQLObject):
        __graphql_name__ = "Query"

        name: str
        surname: str

    class SecondRoot(GraphQLObject):
        __graphql_name__ = "Query"

        message: str

    schema = make_executable_schema(
        FirstRoot,
        SecondRoot,
        """
        type Query {
          score: Int!
        }
        """,
    )

    assert_schema_equals(
        schema,
        """
        type Query {
          message: String!
          name: String!
          score: Int!
          surname: String!
        }
        """,
    )


def test_multiple_roots_fail_validation_if_merge_roots_is_disabled(data_regression):
    class FirstRoot(GraphQLObject):
        __graphql_name__ = "Query"

        name: str
        surname: str

    class SecondRoot(GraphQLObject):
        __graphql_name__ = "Query"

        message: str

    class ThirdRoot(GraphQLObject):
        __graphql_name__ = "Query"

        score: int

    with pytest.raises(ValueError) as exc_info:
        make_executable_schema(FirstRoot, SecondRoot, ThirdRoot, merge_roots=False)

    data_regression.check(str(exc_info.value))


def test_schema_validation_fails_if_lazy_type_doesnt_exist(data_regression):
    class QueryType(GraphQLObject):
        @GraphQLObject.field(graphql_type=list["Missing"])  # type: ignore  # noqa: F821
        @staticmethod
        def other(*_):
            return None

    with pytest.raises(TypeError) as exc_info:
        make_executable_schema(QueryType)

    data_regression.check(str(exc_info.value))


def test_schema_validation_passes_if_lazy_type_exists():
    class QueryType(GraphQLObject):
        @GraphQLObject.field(graphql_type=list["Exists"])  # type: ignore  # noqa: F821
        @staticmethod
        def other(*_):
            return None

    type_def = """
        type Exists {
            id: ID!
        }
        """

    make_executable_schema(QueryType, type_def)


def test_make_executable_schema_raises_error_if_called_without_any_types(
    data_regression,
):
    with pytest.raises(ValueError) as exc_info:
        make_executable_schema(QueryType)

    data_regression.check(str(exc_info.value))


def test_resolvers_not_set_without_name_case_conversion():
    class QueryType(GraphQLObject):
        other_field: str

    type_def = """
        type Query {
            firstField: String!
        }
        """

    schema = make_executable_schema(QueryType, type_def)
    result = graphql_sync(
        schema,
        "{ firstField otherField }",
        root_value={"firstField": "first", "other_field": "other"},
    )
    assert result.data == {"firstField": "first", "otherField": "other"}


def test_make_executable_schema_sets_resolvers_if_convert_names_case_is_enabled():
    class QueryType(GraphQLObject):
        other_field: str

    type_def = """
        type Query {
            firstField: String!
        }
        """

    schema = make_executable_schema(QueryType, type_def, convert_names_case=True)
    result = graphql_sync(
        schema,
        "{ firstField otherField }",
        root_value={"first_field": "first", "other_field": "other"},
    )
    assert result.data == {"firstField": "first", "otherField": "other"}


class UpperDirective(SchemaDirectiveVisitor):
    def visit_field_definition(
        self,
        field: GraphQLField,
        object_type: Union[GraphQLObjectType, GraphQLInterfaceType],
    ) -> GraphQLField:
        resolver = field.resolve or default_field_resolver

        def resolve_upper(obj, info, **kwargs):
            result = resolver(obj, info, **kwargs)
            return result.upper()

        field.resolve = resolve_upper
        return field


def test_make_executable_schema_supports_vanilla_directives():
    type_def = """
        directive @upper on FIELD_DEFINITION

        type Query {
            field: String! @upper
        }
        """
    schema = make_executable_schema(
        type_def,
        directives={
            "upper": UpperDirective,  # type: ignore
        },
    )
    result = graphql_sync(
        schema,
        "{ field }",
        root_value={"field": "first"},
    )
    assert result.data == {"field": "FIRST"}


def test_make_executable_schema_custom_convert_name_case(assert_schema_equals):
    def custom_name_converter(name: str, *_) -> str:
        return f"custom_{name}"

    class QueryType(GraphQLObject):
        other_field: str

    type_def = """
        type Query {
            firstField: String!
        }
        """

    schema = make_executable_schema(
        QueryType, type_def, convert_names_case=custom_name_converter
    )
    assert_schema_equals(
        schema,
        """
        type Query {
          firstField: String!
          otherField: String!
        }
        """,
    )
    result = graphql_sync(
        schema,
        "{ firstField otherField }",
        root_value={"custom_firstField": "first", "other_field": "other"},
    )

    assert result.data == {"firstField": "first", "otherField": "other"}
