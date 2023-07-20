from typing import Iterable, Optional

from graphql import GraphQLSchema, TypeDefinitionNode


class GraphQLType:
    __graphql_name__: Optional[str]
    __abstract__: bool = True

    @classmethod
    def __get_graphql_name__(cls) -> "str":
        if getattr(cls, "__graphql_name__", None):
            return cls.__graphql_name__

        name = cls.__name__
        if name.endswith("GraphQLType"):
            # 'UserGraphQLType' will produce the 'User' name
            return name[:-11] or name
        if name.endswith("Type"):
            # 'UserType' will produce the 'User' name
            return name[:-4] or name
        if name.endswith("GraphQL"):
            # 'UserGraphQL' will produce the 'User' name
            return name[:-7] or name
        return name

    @classmethod
    def __get_graphql_model__(cls) -> "GraphQLModel":
        raise NotImplementedError(
            "Subclasses of 'GraphQLType' must define '__get_graphql_model__'"
        )

    @classmethod
    def __get_graphql_types__(cls) -> Iterable["GraphQLType"]:
        """Returns iterable with GraphQL types associated with this type"""
        return [cls]


class GraphQLModel:
    name: str
    ast_type: TypeDefinitionNode

    def __init__(self, name: str):
        self.name = name

    def get_ast(self) -> TypeDefinitionNode:
        raise NotImplementedError(
            "Subclasses of 'GraphQLModel' need to define a 'get_ast' method."
        )

    def bind_to_schema(self, schema: GraphQLSchema):
        pass
