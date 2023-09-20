from textwrap import dedent

import pytest
from graphql import TypeDefinitionNode, GraphQLSchema, print_ast, print_schema

from ariadne_graphql_modules.next import GraphQLMetadata


@pytest.fixture
def assert_schema_equals():
    def schema_equals_assertion(schema: GraphQLSchema, target: str):
        schema_str = print_schema(schema)
        assert schema_str == dedent(target).strip()

    return schema_equals_assertion


@pytest.fixture
def assert_ast_equals():
    def ast_equals_assertion(ast: TypeDefinitionNode, target: str):
        ast_str = print_ast(ast)
        assert ast_str == dedent(target).strip()

    return ast_equals_assertion


@pytest.fixture
def metadata():
    return GraphQLMetadata()
