from dataclasses import dataclass
from typing import cast

from ariadne import SubscriptionType
from ariadne.types import Resolver, Subscriber
from graphql import GraphQLField, GraphQLObjectType, GraphQLSchema

from ariadne_graphql_modules.base import GraphQLModel


@dataclass(frozen=True)
class GraphQLSubscriptionModel(GraphQLModel):
    resolvers: dict[str, Resolver]
    out_names: dict[str, dict[str, str]]
    aliases: dict[str, str]
    subscribers: dict[str, Subscriber]

    def bind_to_schema(self, schema: GraphQLSchema):
        bindable = SubscriptionType()
        for field, resolver in self.resolvers.items():
            bindable.set_field(field, resolver)
        for alias, target in self.aliases.items():
            bindable.set_alias(alias, target)
        for source, generator in self.subscribers.items():
            bindable.set_source(source, generator)
        bindable.bind_to_schema(schema)

        graphql_type = cast(GraphQLObjectType, schema.get_type(self.name))
        for field_name, field_out_names in self.out_names.items():
            graphql_field = cast(GraphQLField, graphql_type.fields[field_name])
            for arg_name, out_name in field_out_names.items():
                graphql_field.args[arg_name].out_name = out_name
