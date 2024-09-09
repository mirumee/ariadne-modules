from dataclasses import dataclass

from graphql import GraphQLSchema, TypeDefinitionNode


@dataclass(frozen=True)
class GraphQLModel:
    name: str
    ast: TypeDefinitionNode
    ast_type: type[TypeDefinitionNode]

    def bind_to_schema(self, schema: GraphQLSchema):
        pass
