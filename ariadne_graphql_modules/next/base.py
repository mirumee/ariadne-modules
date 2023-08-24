from typing import Iterable, Optional, Type

from graphql import GraphQLSchema, TypeDefinitionNode, parse


class GraphQLType:
    __graphql_name__: Optional[str]
    __abstract__: bool = True

    @classmethod
    def __get_graphql_name__(cls) -> "str":
        if getattr(cls, "__graphql_name__", None):
            return cls.__graphql_name__

        if getattr(cls, "__schema__", None):
            return cls.__get_graphql_name_from_schema__()

        name = cls.__name__
        if name.endswith("GraphQLType"):
            # 'UserGraphQLType' will produce the 'User' name
            return name[:-11] or name
        if name.endswith("Type"):
            # 'UserType' will produce the 'User' name
            return name[:-4] or name
        if name.endswith("GraphQLScalar"):
            # 'DateTimeGraphQLScalar' will produce the 'DateTime' name
            return name[:-13] or name
        if name.endswith("Scalar"):
            # 'DateTimeLScalar' will produce the 'DateTime' name
            return name[:-6] or name
        if name.endswith("GraphQL"):
            # 'UserGraphQL' will produce the 'User' name
            return name[:-7] or name

        return name

    @classmethod
    def __get_graphql_name_from_schema__(cls) -> "str":
        # Todo: cache this in future...
        document = parse(cls.__schema__)
        return document.definitions[0].name.value

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
    ast: TypeDefinitionNode
    ast_type: Type[TypeDefinitionNode]

    def __init__(self, name: str, ast: TypeDefinitionNode):
        self.name = name
        self.ast = ast

    def bind_to_schema(self, schema: GraphQLSchema):
        pass
