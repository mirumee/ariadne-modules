from dataclasses import dataclass
from typing import Any

from ariadne import InputType as InputTypeBindable
from graphql import GraphQLSchema

from ariadne_graphql_modules.base_graphql_model import GraphQLModel


@dataclass(frozen=True)
class GraphQLInputModel(GraphQLModel):
    out_type: Any
    out_names: dict[str, str]

    def bind_to_schema(self, schema: GraphQLSchema):
        bindable = InputTypeBindable(self.name, self.out_type, self.out_names)
        bindable.bind_to_schema(schema)
