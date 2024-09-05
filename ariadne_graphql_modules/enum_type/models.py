from dataclasses import dataclass
from typing import Any

from ariadne import EnumType
from graphql import GraphQLSchema

from ariadne_graphql_modules.base import GraphQLModel


@dataclass(frozen=True)
class GraphQLEnumModel(GraphQLModel):
    members: dict[str, Any]

    def bind_to_schema(self, schema: GraphQLSchema):
        bindable = EnumType(self.name, values=self.members)
        bindable.bind_to_schema(schema)
