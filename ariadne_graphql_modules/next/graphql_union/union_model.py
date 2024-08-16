from dataclasses import dataclass
from typing import Any, Callable

from ariadne import UnionType
from graphql import GraphQLSchema

from ..base import GraphQLModel


@dataclass(frozen=True)
class GraphQLUnionModel(GraphQLModel):
    resolve_type: Callable[[Any], Any]

    def bind_to_schema(self, schema: GraphQLSchema):
        bindable = UnionType(self.name, self.resolve_type)
        bindable.bind_to_schema(schema)
