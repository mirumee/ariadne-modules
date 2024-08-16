from dataclasses import dataclass
from typing import Any, Dict
from ariadne import EnumType
from graphql import GraphQLSchema

from ..base import GraphQLModel


@dataclass(frozen=True)
class GraphQLEnumModel(GraphQLModel):
    members: Dict[str, Any]

    def bind_to_schema(self, schema: GraphQLSchema):
        bindable = EnumType(self.name, values=self.members)
        bindable.bind_to_schema(schema)
