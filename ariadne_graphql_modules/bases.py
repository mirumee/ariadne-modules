from typing import List, Type, Union

from graphql import (
    DefinitionNode,
    GraphQLSchema,
    ObjectTypeDefinitionNode,
    TypeSystemDefinitionNode,
)

from .dependencies import Dependencies
from .types import RequirementsDict

__all__ = ["BaseType", "BindableType", "DeferredType", "DefinitionType"]


class BaseType:
    __abstract__: bool = True

    @classmethod
    def __get_types__(cls) -> List[Type["BaseType"]]:
        return []


class DeferredType(BaseType):
    graphql_name: str
    graphql_type = ObjectTypeDefinitionNode

    def __init__(self, name: str):
        self.graphql_name = name


class DefinitionType(BaseType):
    __abstract__: bool = True
    __schema__: str
    __requires__: List[Union[Type["DefinitionType"], DeferredType]] = []

    graphql_name: str
    graphql_type: Type[DefinitionNode]
    graphql_def: TypeSystemDefinitionNode

    @classmethod
    def __get_requirements__(cls) -> RequirementsDict:
        return {req.graphql_name: req.graphql_type for req in cls.__requires__}

    @classmethod
    def __validate_requirements__(
        cls, requirements: RequirementsDict, dependencies: Dependencies
    ):
        for graphql_name in dependencies:
            if graphql_name not in requirements:
                raise ValueError(
                    f"{cls.__name__} class was defined without required GraphQL "
                    f"definition for '{graphql_name}' in __requires__"
                )

    @classmethod
    def __get_types__(cls) -> List[Type["BaseType"]]:
        types: List[Type["BaseType"]] = [cls]
        for type_ in cls.__requires__:
            child_types = type_.__get_types__()
            for child_type in child_types:
                if child_type not in types:
                    types.append(child_type)
        return types


class BindableType(DefinitionType):
    __abstract__: bool = True

    @classmethod
    def __bind_to_schema__(cls, schema: GraphQLSchema):
        raise NotImplementedError()
