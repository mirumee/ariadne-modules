import pytest
from graphql import GraphQLError
from graphql.language.ast import ObjectTypeDefinitionNode

from ariadne_graphql_modules.v1 import parse_definition


def test_definition_parser_returns_definition_type_from_valid_schema_string():
    type_def = parse_definition(
        "MyType",
        """
            type My {
                id: ID!
            }
        """,
    )

    assert isinstance(type_def, ObjectTypeDefinitionNode)
    assert type_def.name.value == "My"
    assert type_def.fields[0].name.value == "id"


def test_definition_parser_parses_definition_with_description():
    type_def = parse_definition(
        "MyType",
        """
        "Test user type"
        type User
        """,
    )

    assert isinstance(type_def, ObjectTypeDefinitionNode)
    assert type_def.name.value == "User"
    assert type_def.description.value == "Test user type"


def test_definition_parser_raises_error_when_schema_type_is_invalid(data_regression):
    with pytest.raises(TypeError) as err:
        parse_definition("MyType", True)

    data_regression.check(str(err.value))


def test_definition_parser_raises_error_when_schema_str_has_invalid_syntax(
    data_regression,
):
    with pytest.raises(GraphQLError) as err:
        parse_definition("MyType", "typo User")

    data_regression.check(str(err.value))


def test_definition_parser_raises_error_schema_str_contains_multiple_types(
    data_regression,
):
    with pytest.raises(ValueError) as err:
        parse_definition(
            "MyType",
            """
            type User

            type Group
            """,
        )

    data_regression.check(str(err.value))
