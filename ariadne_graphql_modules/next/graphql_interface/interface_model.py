from dataclasses import dataclass
from typing import Any, Callable, Dict, cast

from ariadne import InterfaceType
from ariadne.types import Resolver
from graphql import GraphQLField, GraphQLObjectType, GraphQLSchema

from ..base import GraphQLModel


@dataclass(frozen=True)
class GraphQLInterfaceModel(GraphQLModel):
    resolvers: Dict[str, Resolver]
    resolve_type: Callable[[Any], Any]
    out_names: Dict[str, Dict[str, str]]
    aliases: Dict[str, str]

    def bind_to_schema(self, schema: GraphQLSchema):
        bindable = InterfaceType(self.name, self.resolve_type)
        for field, resolver in self.resolvers.items():
            bindable.set_field(field, resolver)
        for alias, target in self.aliases.items():
            bindable.set_alias(alias, target)

        bindable.bind_to_schema(schema)

        graphql_type = cast(GraphQLObjectType, schema.get_type(self.name))
        for field_name, field_out_names in self.out_names.items():
            graphql_field = cast(GraphQLField, graphql_type.fields[field_name])
            for arg_name, out_name in field_out_names.items():
                graphql_field.args[arg_name].out_name = out_name
