from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Iterable, Optional, Type, Union

from graphql import GraphQLSchema, TypeDefinitionNode


class GraphQLType:
    __graphql_name__: Optional[str]
    __description__: Optional[str]
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
    def __get_graphql_model__(cls, metadata: "Metadata") -> "GraphQLModel":
        raise NotImplementedError(
            "Subclasses of 'GraphQLType' must define '__get_graphql_model__'"
        )

    @classmethod
    def __get_graphql_types__(cls) -> Iterable["GraphQLType"]:
        """Returns iterable with GraphQL types associated with this type"""
        return [cls]


@dataclass(frozen=True)
class GraphQLModel:
    name: str
    ast: TypeDefinitionNode
    ast_type: Type[TypeDefinitionNode]

    def __init__(self, name: str, ast: TypeDefinitionNode):
        self.name = name
        self.ast = ast

    def bind_to_schema(self, schema: GraphQLSchema):
        pass


@dataclass(frozen=True)
class GraphQLMetadata:
    models: Dict[Union[Type[GraphQLType], Type[Enum]], GraphQLModel] = field(
        default_factory=dict
    )

    def get_graphql_model(
        self, type: Union[Type[GraphQLType], Type[Enum]]
    ) -> GraphQLModel:
        if type not in self.models:
            if hasattr(type, "__get_graphql_model__"):
                self.models[type] = type.__get_graphql_model__(self)
            elif issubclass(type, Enum):
                from .enumtype import create_graphql_enum_model

                self.models[type] = create_graphql_enum_model(type)
            else:
                raise ValueError(f"Can't retrieve GraphQL model for '{type}'.")

        return self.models[type]

    def get_graphql_name(self, type: Union[Type[GraphQLType], Type[Enum]]) -> str:
        model = self.get_graphql_model(type)
        return model.name
