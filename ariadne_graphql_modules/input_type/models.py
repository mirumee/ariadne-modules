from dataclasses import dataclass
from typing import Any, Dict

from ariadne import InputType as InputTypeBindable
from graphql import GraphQLSchema

from ..base import GraphQLModel


@dataclass(frozen=True)
class GraphQLInputModel(GraphQLModel):
    out_type: Any
    out_names: Dict[str, str]

    def bind_to_schema(self, schema: GraphQLSchema):
        bindable = InputTypeBindable(self.name, self.out_type, self.out_names)
        bindable.bind_to_schema(schema)
