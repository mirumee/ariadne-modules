from typing import Optional

import pytest
from graphql import graphql_sync

from ariadne_graphql_modules import gql
from ariadne_graphql_modules.next import (
    GraphQLInput,
    GraphQLObject,
    make_executable_schema,
)


def test_input_type_instance_with_all_attrs_values():
    class SearchInput(GraphQLInput):
        query: str
        age: int

    obj = SearchInput(query="search", age=20)
    assert obj.query == "search"
    assert obj.age == 20


def test_input_type_instance_with_omitted_attrs_being_none():
    class SearchInput(GraphQLInput):
        query: str
        age: int

    obj = SearchInput(age=20)
    assert obj.query is None
    assert obj.age == 20


def test_input_type_instance_with_default_attrs_values():
    class SearchInput(GraphQLInput):
        query: str = "default"
        age: int = 42

    obj = SearchInput(age=20)
    assert obj.query == "default"
    assert obj.age == 20


def test_input_type_instance_with_all_fields_values():
    class SearchInput(GraphQLInput):
        query: str = GraphQLInput.field()
        age: int = GraphQLInput.field()

    obj = SearchInput(query="search", age=20)
    assert obj.query == "search"
    assert obj.age == 20


def test_input_type_instance_with_all_fields_default_values():
    class SearchInput(GraphQLInput):
        query: str = GraphQLInput.field(default_value="default")
        age: int = GraphQLInput.field(default_value=42)

    obj = SearchInput(age=20)
    assert obj.query == "default"
    assert obj.age == 20


def test_input_type_instance_with_invalid_attrs_raising_error(snapshot):
    class SearchInput(GraphQLInput):
        query: str
        age: int

    with pytest.raises(TypeError) as exc_info:
        SearchInput(age=20, invalid="Ok")

    snapshot.assert_match(str(exc_info.value))


def test_schema_input_type_instance_with_all_attrs_values():
    class SearchInput(GraphQLInput):
        __schema__ = gql(
            """
            input Search {
                query: String
                age: Int
            }
            """
        )

        query: str
        age: int

    obj = SearchInput(query="search", age=20)
    assert obj.query == "search"
    assert obj.age == 20


def test_schema_input_type_instance_with_omitted_attrs_being_none():
    class SearchInput(GraphQLInput):
        __schema__ = gql(
            """
            input Search {
                query: String
                age: Int
            }
            """
        )

        query: str
        age: int

    obj = SearchInput(age=20)
    assert obj.query is None
    assert obj.age == 20


def test_schema_input_type_instance_with_default_attrs_values():
    class SearchInput(GraphQLInput):
        __schema__ = gql(
            """
            input Search {
                query: String = "default"
                age: Int = 42
            }
            """
        )

        query: str
        age: int

    obj = SearchInput(age=20)
    assert obj.query == "default"
    assert obj.age == 20


def test_schema_input_type_instance_with_all_attrs_default_values():
    class SearchInput(GraphQLInput):
        __schema__ = gql(
            """
            input Search {
                query: String = "default"
                age: Int = 42
            }
            """
        )

        query: str
        age: int

    obj = SearchInput()
    assert obj.query == "default"
    assert obj.age == 42


def test_schema_input_type_instance_with_default_attrs_python_values():
    class SearchInput(GraphQLInput):
        __schema__ = gql(
            """
            input Search {
                query: String
                age: Int
            }
            """
        )

        query: str = "default"
        age: int = 42

    obj = SearchInput(age=20)
    assert obj.query == "default"
    assert obj.age == 20


def test_schema_input_type_instance_with_invalid_attrs_raising_error(snapshot):
    class SearchInput(GraphQLInput):
        __schema__ = gql(
            """
            input Search {
                query: String
                age: Int
            }
            """
        )

        query: str
        age: int

    with pytest.raises(TypeError) as exc_info:
        SearchInput(age=20, invalid="Ok")

    snapshot.assert_match(str(exc_info.value))


def test_input_type_arg(assert_schema_equals):
    class SearchInput(GraphQLInput):
        query: Optional[str]
        age: Optional[int]

    class QueryType(GraphQLObject):
        search: str

        @GraphQLObject.resolver("search")
        def resolve_search(*_, input: SearchInput) -> str:
            return f"{repr([input.query, input.age])}"

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          search(input: SearchInput!): String!
        }

        input SearchInput {
          query: String
          age: Int
        }
        """,
    )

    result = graphql_sync(schema, '{ search(input: { query: "Hello" }) }')

    assert not result.errors
    assert result.data == {"search": "['Hello', None]"}


def test_schema_input_type_arg(assert_schema_equals):
    class SearchInput(GraphQLInput):
        __schema__ = """
        input SearchInput {
          query: String
          age: Int
        }
        """

        query: Optional[str]
        age: Optional[int]

    class QueryType(GraphQLObject):
        search: str

        @GraphQLObject.resolver("search")
        def resolve_search(*_, input: SearchInput) -> str:
            return f"{repr([input.query, input.age])}"

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          search(input: SearchInput!): String!
        }

        input SearchInput {
          query: String
          age: Int
        }
        """,
    )

    result = graphql_sync(schema, '{ search(input: { query: "Hello" }) }')

    assert not result.errors
    assert result.data == {"search": "['Hello', None]"}


def test_input_type_automatic_out_name_arg(assert_schema_equals):
    class SearchInput(GraphQLInput):
        query: Optional[str]
        min_age: Optional[int]

    class QueryType(GraphQLObject):
        search: str

        @GraphQLObject.resolver("search")
        def resolve_search(*_, input: SearchInput) -> str:
            return f"{repr([input.query, input.min_age])}"

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          search(input: SearchInput!): String!
        }

        input SearchInput {
          query: String
          minAge: Int
        }
        """,
    )

    result = graphql_sync(schema, "{ search(input: { minAge: 21 }) }")

    assert not result.errors
    assert result.data == {"search": "[None, 21]"}


def test_schema_input_type_automatic_out_name_arg(assert_schema_equals):
    class SearchInput(GraphQLInput):
        __schema__ = """
        input SearchInput {
          query: String
          minAge: Int
        }
        """

        query: Optional[str]
        min_age: Optional[int]

    class QueryType(GraphQLObject):
        search: str

        @GraphQLObject.resolver("search")
        def resolve_search(*_, input: SearchInput) -> str:
            return f"{repr([input.query, input.min_age])}"

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          search(input: SearchInput!): String!
        }

        input SearchInput {
          query: String
          minAge: Int
        }
        """,
    )

    result = graphql_sync(schema, "{ search(input: { minAge: 21 }) }")

    assert not result.errors
    assert result.data == {"search": "[None, 21]"}


def test_schema_input_type_explicit_out_name_arg(assert_schema_equals):
    class SearchInput(GraphQLInput):
        __schema__ = """
        input SearchInput {
          query: String
          minAge: Int
        }
        """
        __out_names__ = {"minAge": "age"}

        query: Optional[str]
        age: Optional[int]

    class QueryType(GraphQLObject):
        search: str

        @GraphQLObject.resolver("search")
        def resolve_search(*_, input: SearchInput) -> str:
            return f"{repr([input.query, input.age])}"

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          search(input: SearchInput!): String!
        }

        input SearchInput {
          query: String
          minAge: Int
        }
        """,
    )

    result = graphql_sync(schema, "{ search(input: { minAge: 21 }) }")

    assert not result.errors
    assert result.data == {"search": "[None, 21]"}


def test_input_type_self_reference(assert_schema_equals):
    class SearchInput(GraphQLInput):
        query: Optional[str]
        extra: Optional["SearchInput"]

    class QueryType(GraphQLObject):
        search: str

        @GraphQLObject.resolver("search")
        def resolve_search(*_, input: SearchInput) -> str:
            if input.extra:
                extra_repr = input.extra.query
            else:
                extra_repr = None

            return f"{repr([input.query, extra_repr])}"

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          search(input: SearchInput!): String!
        }

        input SearchInput {
          query: String
          extra: SearchInput
        }
        """,
    )

    result = graphql_sync(
        schema,
        """
        {
            search(
                input: { query: "Hello", extra: { query: "Other" } }
            )
        }
        """,
    )

    assert not result.errors
    assert result.data == {"search": "['Hello', 'Other']"}


def test_schema_input_type_with_default_value(assert_schema_equals):
    class SearchInput(GraphQLInput):
        __schema__ = """
        input SearchInput {
          query: String = "Search"
          age: Int = 42
        }
        """

        query: str
        age: int

    class QueryType(GraphQLObject):
        search: str

        @GraphQLObject.resolver("search")
        def resolve_search(*_, input: SearchInput) -> str:
            return f"{repr([input.query, input.age])}"

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          search(input: SearchInput!): String!
        }

        input SearchInput {
          query: String = "Search"
          age: Int = 42
        }
        """,
    )

    result = graphql_sync(schema, "{ search(input: {}) }")

    assert not result.errors
    assert result.data == {"search": "['Search', 42]"}


def test_input_type_with_field_default_value(assert_schema_equals):
    class SearchInput(GraphQLInput):
        query: str = "default"
        age: int = 42
        flag: bool = False

    class QueryType(GraphQLObject):
        search: str

        @GraphQLObject.resolver("search")
        def resolve_search(*_, input: SearchInput) -> str:
            return f"{repr([input.query, input.age, input.flag])}"

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          search(input: SearchInput!): String!
        }

        input SearchInput {
          query: String! = "default"
          age: Int! = 42
          flag: Boolean! = false
        }
        """,
    )

    result = graphql_sync(schema, "{ search(input: {}) }")

    assert not result.errors
    assert result.data == {"search": "['default', 42, False]"}


def test_input_type_with_field_instance_default_value(assert_schema_equals):
    class SearchInput(GraphQLInput):
        query: str = GraphQLInput.field(default_value="default")
        age: int = GraphQLInput.field(default_value=42)
        flag: bool = GraphQLInput.field(default_value=False)

    class QueryType(GraphQLObject):
        search: str

        @GraphQLObject.resolver("search")
        def resolve_search(*_, input: SearchInput) -> str:
            return f"{repr([input.query, input.age, input.flag])}"

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          search(input: SearchInput!): String!
        }

        input SearchInput {
          query: String! = "default"
          age: Int! = 42
          flag: Boolean! = false
        }
        """,
    )

    result = graphql_sync(schema, "{ search(input: {}) }")

    assert not result.errors
    assert result.data == {"search": "['default', 42, False]"}


def test_input_type_with_field_type(assert_schema_equals):
    class SearchInput(GraphQLInput):
        query: str = GraphQLInput.field(type=int)

    class QueryType(GraphQLObject):
        search: str

        @GraphQLObject.resolver("search")
        def resolve_search(*_, input: SearchInput) -> str:
            return str(input)

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          search(input: SearchInput!): String!
        }

        input SearchInput {
          query: Int!
        }
        """,
    )


def test_schema_input_type_with_field_description(assert_schema_equals):
    class SearchInput(GraphQLInput):
        __schema__ = """
        input SearchInput {
          \"\"\"Hello world.\"\"\"
          query: String!
        }
        """

    class QueryType(GraphQLObject):
        search: str

        @GraphQLObject.resolver("search")
        def resolve_search(*_, input: SearchInput) -> str:
            return str(input)

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          search(input: SearchInput!): String!
        }

        input SearchInput {
          \"\"\"Hello world.\"\"\"
          query: String!
        }
        """,
    )


def test_input_type_with_field_description(assert_schema_equals):
    class SearchInput(GraphQLInput):
        query: str = GraphQLInput.field(description="Hello world.")

    class QueryType(GraphQLObject):
        search: str

        @GraphQLObject.resolver("search")
        def resolve_search(*_, input: SearchInput) -> str:
            return str(input)

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          search(input: SearchInput!): String!
        }

        input SearchInput {
          \"\"\"Hello world.\"\"\"
          query: String!
        }
        """,
    )
