from datetime import date

from graphql import graphql_sync

from ariadne import gql
from ariadne_graphql_modules import (
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
        scalar_date: DateScalar

        @GraphQLObject.resolver("scalar_date", graphql_type=DateScalar)
        def resolve_date(*_) -> date:
            return date(1989, 10, 30)

    schema = make_executable_schema(QueryType)

    assert_schema_equals(
        schema,
        """
        scalar Date

        type Query {
          scalarDate: Date!
        }
        """,
    )

    result = graphql_sync(schema, "{ scalarDate }")

    assert not result.errors
    assert result.data == {"scalarDate": "1989-10-30"}


class SchemaDateScalar(GraphQLScalar[date]):
    __schema__ = gql("scalar Date")

    @classmethod
    def serialize(cls, value):
        if isinstance(value, cls):
            return str(value.unwrap())

        return str(value)


def test_schema_scalar_field_returning_scalar_instance(assert_schema_equals):
    class QueryType(GraphQLObject):
        date: SchemaDateScalar

        @GraphQLObject.resolver("date")
        def resolve_date(*_) -> SchemaDateScalar:
            return SchemaDateScalar(date(1989, 10, 30))

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
