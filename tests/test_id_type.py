from graphql import graphql_sync

from ariadne_graphql_modules import (
    GraphQLID,
    GraphQLInput,
    GraphQLObject,
    make_executable_schema,
)


def test_graphql_id_instance_from_int_is_casted_to_str():
    gid = GraphQLID(123)
    assert gid.value == "123"


def test_graphql_id_instance_from_str_remains_as_str():
    gid = GraphQLID("obj-id")
    assert gid.value == "obj-id"


def test_graphql_id_can_be_cast_to_int():
    gid = GraphQLID(123)
    assert int(gid) == 123


def test_graphql_id_can_be_cast_to_str():
    gid = GraphQLID(123)
    assert str(gid) == "123"


def test_graphql_id_can_be_compared_to_other_id():
    assert GraphQLID("123") == GraphQLID("123")
    assert GraphQLID(123) == GraphQLID(123)
    assert GraphQLID(123) == GraphQLID("123")
    assert GraphQLID("123") == GraphQLID(123)

    assert GraphQLID("123") != GraphQLID("321")
    assert GraphQLID(123) != GraphQLID(321)
    assert GraphQLID(321) != GraphQLID("123")
    assert GraphQLID("123") != GraphQLID(321)


def test_graphql_id_can_be_compared_to_str():
    assert GraphQLID("123") == "123"
    assert GraphQLID(123) == "123"

    assert GraphQLID("123") != "321"
    assert GraphQLID(123) != "321"


def test_graphql_id_can_be_compared_to_int():
    assert GraphQLID("123") == 123
    assert GraphQLID(123) == 123

    assert GraphQLID("123") != 321
    assert GraphQLID(123) != 321


def test_graphql_id_can_be_compared_to_others():
    assert GraphQLID("123") != 123.0
    assert GraphQLID(123) != 123.0


def test_graphql_id_object_field_type_hint(assert_schema_equals):
    class QueryType(GraphQLObject):
        id: GraphQLID

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          id: ID!
        }
        """,
    )

    result = graphql_sync(schema, "{ id }", root_value={"id": 123})

    assert not result.errors
    assert result.data == {"id": "123"}


def test_graphql_id_object_field_instance(assert_schema_equals):
    class QueryType(GraphQLObject):
        @GraphQLObject.field(name="id")
        @staticmethod
        def id_type(*_) -> GraphQLID:
            return GraphQLID(115)

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          id: ID!
        }
        """,
    )

    result = graphql_sync(schema, "{ id }")

    assert not result.errors
    assert result.data == {"id": "115"}


def test_graphql_id_object_field_instance_arg(assert_schema_equals):
    class QueryType(GraphQLObject):
        @GraphQLObject.field(name="id")
        @staticmethod
        def id_type(*_, arg: GraphQLID) -> str:
            return str(arg)

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          id(arg: ID!): String!
        }
        """,
    )

    result = graphql_sync(schema, '{ id(arg: "123") }')

    assert not result.errors
    assert result.data == {"id": "123"}


def test_graphql_id_input_field(assert_schema_equals):
    class ArgType(GraphQLInput):
        id: GraphQLID

    class QueryType(GraphQLObject):
        @GraphQLObject.field(name="id")
        @staticmethod
        def id_type(*_, arg: ArgType) -> str:
            return str(arg.id)

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        type Query {
          id(arg: Arg!): String!
        }

        input Arg {
          id: ID!
        }
        """,
    )

    result = graphql_sync(schema, '{ id(arg: {id: "123"}) }')

    assert not result.errors
    assert result.data == {"id": "123"}
