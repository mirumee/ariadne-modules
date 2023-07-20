from textwrap import dedent

import pytest
from graphql import GraphQLSchema, print_schema


@pytest.fixture
def assert_schema_equals():
    def schema_equals_assertion(schema: GraphQLSchema, target: str):
        schema_str = print_schema(schema)
        print(schema_str)

        assert schema_str == dedent(target).strip()

    return schema_equals_assertion
