from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from graphql import GraphQLSchema, ValueNode
from ariadne import ScalarType as ScalarTypeBindable
from ..base import GraphQLModel


@dataclass(frozen=True)
class GraphQLScalarModel(GraphQLModel):
    serialize: Callable[[Any], Any]
    parse_value: Callable[[Any], Any]
    parse_literal: Callable[[ValueNode, Optional[Dict[str, Any]]], Any]

    def bind_to_schema(self, schema: GraphQLSchema):
        bindable = ScalarTypeBindable(
            self.name,
            serializer=self.serialize,
            value_parser=self.parse_value,
            literal_parser=self.parse_literal,
        )

        bindable.bind_to_schema(schema)
