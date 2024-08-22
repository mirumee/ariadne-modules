from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Iterable, Optional, Type, Union

from graphql import GraphQLSchema, TypeDefinitionNode


class GraphQLType:
    __graphql_name__: Optional[str]
    __description__: Optional[str]
    __abstract__: bool = True

    @classmethod
    def __get_graphql_name__(cls) -> str:
        name = getattr(cls, "__graphql_name__", None)
        if name:
            return name

        name_mappings = [
            ("GraphQLEnum", "Enum"),
            ("GraphQLInput", "Input"),
            ("GraphQLScalar", ""),
            ("Scalar", ""),
            ("GraphQL", ""),
            ("Type", ""),
            ("GraphQLType", ""),
        ]

        name = cls.__name__
        for suffix, replacement in name_mappings:
            if name.endswith(suffix):
                return name[: -len(suffix)] + replacement

        return name

    @classmethod
    def __get_graphql_model__(cls, metadata: "GraphQLMetadata") -> "GraphQLModel":
        raise NotImplementedError(
            "Subclasses of 'GraphQLType' must define '__get_graphql_model__'"
        )

    @classmethod
    def __get_graphql_types__(
        cls, _: "GraphQLMetadata"
    ) -> Iterable[Union[Type["GraphQLType"], Type[Enum]]]:
        """Returns iterable with GraphQL types associated with this type"""
        return [cls]


@dataclass(frozen=True)
class GraphQLModel:
    name: str
    ast: TypeDefinitionNode
    ast_type: Type[TypeDefinitionNode]

    def bind_to_schema(self, schema: GraphQLSchema):
        pass


@dataclass(frozen=True)
class GraphQLMetadata:
    data: Dict[Union[Type[GraphQLType], Type[Enum]], Any] = field(default_factory=dict)
    names: Dict[Union[Type[GraphQLType], Type[Enum]], str] = field(default_factory=dict)
    models: Dict[Union[Type[GraphQLType], Type[Enum]], GraphQLModel] = field(
        default_factory=dict
    )

    def get_data(self, graphql_type: Union[Type[GraphQLType], Type[Enum]]) -> Any:
        try:
            return self.data[graphql_type]
        except KeyError as e:
            raise KeyError(f"No data is set for '{graphql_type}'.") from e

    def set_data(
        self, graphql_type: Union[Type[GraphQLType], Type[Enum]], data: Any
    ) -> Any:
        self.data[graphql_type] = data
        return data

    def get_graphql_model(
        self, graphql_type: Union[Type[GraphQLType], Type[Enum]]
    ) -> GraphQLModel:
        if graphql_type not in self.models:
            if hasattr(graphql_type, "__get_graphql_model__"):
                self.models[graphql_type] = graphql_type.__get_graphql_model__(self)
            elif issubclass(graphql_type, Enum):
                from .enum_type import (  # pylint: disable=R0401,C0415
                    create_graphql_enum_model,
                )

                self.models[graphql_type] = create_graphql_enum_model(graphql_type)
            else:
                raise ValueError(f"Can't retrieve GraphQL model for '{graphql_type}'.")

        return self.models[graphql_type]

    def set_graphql_name(
        self, graphql_type: Union[Type[GraphQLType], Type[Enum]], name: str
    ):
        self.names[graphql_type] = name

    def get_graphql_name(
        self, graphql_type: Union[Type[GraphQLType], Type[Enum]]
    ) -> str:
        if graphql_type not in self.names:
            model = self.get_graphql_model(graphql_type)
            self.set_graphql_name(graphql_type, model.name)

        return self.names[graphql_type]
