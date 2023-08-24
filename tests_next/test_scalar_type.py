from datetime import date

from graphql import graphql_sync

from ariadne_graphql_modules import gql
from ariadne_graphql_modules.next import (
    GraphQLObject,
    GraphQLScalar,
    make_executable_schema,
)


class DateScalar(GraphQLScalar[date]):
    @classmethod
    def serialize(cls, value):
        if isinstance(value, cls):
            return str(value.unwrap())

        return str(value)


class SDLDateScalar(GraphQLScalar[date]):
    __schema__ = "scalar Date"

    @classmethod
    def serialize(cls, value):
        if isinstance(value, cls):
            return str(value.unwrap())

        return str(value)


def test_scalar_field_returning_scalar_instance(assert_schema_equals):
    class QueryType(GraphQLObject):
        date: DateScalar

        @GraphQLObject.resolver("date")
        def resolve_date(*_) -> DateScalar:
            return DateScalar(date(1989, 10, 30))

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        scalar Date

        type Query {
          date: Date!
        }
        """,
    )

    result = graphql_sync(schema, "{ date }")

    assert not result.errors
    assert result.data == {"date": "1989-10-30"}


def test_scalar_field_returning_scalar_wrapped_type(assert_schema_equals):
    class QueryType(GraphQLObject):
        date: DateScalar

        @GraphQLObject.resolver("date", type=DateScalar)
        def resolve_date(*_) -> date:
            return date(1989, 10, 30)

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        scalar Date

        type Query {
          date: Date!
        }
        """,
    )

    result = graphql_sync(schema, "{ date }")

    assert not result.errors
    assert result.data == {"date": "1989-10-30"}


def test_schema_first_scalar_type(assert_schema_equals):
    class QueryType(GraphQLObject):
        date: SDLDateScalar

        @GraphQLObject.resolver("date")
        def resolve_date(*_) -> SDLDateScalar:
            return SDLDateScalar(date(1989, 10, 30))

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        scalar Date

        type Query {
          date: Date!
        }
        """,
    )

    result = graphql_sync(schema, "{ date }")

    assert not result.errors
    assert result.data == {"date": "1989-10-30"}
