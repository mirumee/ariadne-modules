from dataclasses import dataclass
from typing import Optional

from ariadne import ScalarType as ScalarTypeBindable
from graphql import (
    GraphQLScalarLiteralParser,
    GraphQLScalarSerializer,
    GraphQLScalarValueParser,
    GraphQLSchema,
)

from ariadne_graphql_modules.base import GraphQLModel


@dataclass(frozen=True)
class GraphQLScalarModel(GraphQLModel):
    serialize: Optional[GraphQLScalarSerializer]
    parse_value: Optional[GraphQLScalarValueParser]
    parse_literal: Optional[GraphQLScalarLiteralParser]

    def bind_to_schema(self, schema: GraphQLSchema):
        bindable = ScalarTypeBindable(
            self.name,
            serializer=self.serialize,
            value_parser=self.parse_value,
            literal_parser=self.parse_literal,
        )

        bindable.bind_to_schema(schema)
