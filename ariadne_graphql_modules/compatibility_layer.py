from enum import Enum
from inspect import isclass
from typing import Any, Union, cast

from graphql import (
    EnumTypeDefinitionNode,
    InputObjectTypeDefinitionNode,
    InterfaceTypeDefinitionNode,
    ObjectTypeDefinitionNode,
    ScalarTypeDefinitionNode,
    TypeExtensionNode,
    UnionTypeDefinitionNode,
)

from ariadne_graphql_modules import (
    GraphQLEnumModel,
    GraphQLInputModel,
    GraphQLInterfaceModel,
    GraphQLObjectModel,
    GraphQLScalarModel,
    GraphQLSubscriptionModel,
    GraphQLUnionModel,
)
from ariadne_graphql_modules.base import GraphQLModel, GraphQLType
from ariadne_graphql_modules.v1.bases import BaseType, BindableType
from ariadne_graphql_modules.v1.directive_type import DirectiveType
from ariadne_graphql_modules.v1.enum_type import EnumType
from ariadne_graphql_modules.v1.executable_schema import get_all_types
from ariadne_graphql_modules.v1.input_type import InputType
from ariadne_graphql_modules.v1.interface_type import InterfaceType
from ariadne_graphql_modules.v1.mutation_type import MutationType
from ariadne_graphql_modules.v1.object_type import ObjectType
from ariadne_graphql_modules.v1.scalar_type import ScalarType
from ariadne_graphql_modules.v1.subscription_type import SubscriptionType
from ariadne_graphql_modules.v1.union_type import UnionType


def wrap_legacy_types(
    *bindable_types: type[BaseType],
) -> list[type["LegacyGraphQLType"]]:
    all_types = get_all_types(bindable_types)

    return [
        type(f"Legacy{t.__name__}", (LegacyGraphQLType,), {"__base_type__": t})
        for t in all_types
    ]


class LegacyGraphQLType(GraphQLType):
    __base_type__: type[BindableType]
    __abstract__: bool = False

    @classmethod
    def __get_graphql_model__(cls, *_) -> GraphQLModel:
        if issubclass(cls.__base_type__.graphql_type, TypeExtensionNode):
            pass
        if issubclass(cls.__base_type__, ObjectType):
            return cls.construct_object_model(cls.__base_type__)
        if issubclass(cls.__base_type__, EnumType):
            return cls.construct_enum_model(cls.__base_type__)
        if issubclass(cls.__base_type__, InputType):
            return cls.construct_input_model(cls.__base_type__)
        if issubclass(cls.__base_type__, InterfaceType):
            return cls.construct_interface_model(cls.__base_type__)
        if issubclass(cls.__base_type__, MutationType):
            return cls.construct_object_model(cls.__base_type__)
        if issubclass(cls.__base_type__, ScalarType):
            return cls.construct_scalar_model(cls.__base_type__)
        if issubclass(cls.__base_type__, SubscriptionType):
            return cls.construct_subscription_model(cls.__base_type__)
        if issubclass(cls.__base_type__, UnionType):
            return cls.construct_union_model(cls.__base_type__)
        raise ValueError(f"Unsupported base_type {cls.__base_type__}")

    @classmethod
    def construct_object_model(
        cls, base_type: type[Union[ObjectType, MutationType]]
    ) -> GraphQLObjectModel:
        return GraphQLObjectModel(
            name=base_type.graphql_name,
            ast_type=ObjectTypeDefinitionNode,
            ast=cast(ObjectTypeDefinitionNode, base_type.graphql_def),
            resolvers=base_type.resolvers,  # type: ignore
            aliases=base_type.__aliases__ or {},  # type: ignore
            out_names={},
        )

    @classmethod
    def construct_enum_model(cls, base_type: type[EnumType]) -> GraphQLEnumModel:
        members = base_type.__enum__ or {}
        members_values: dict[str, Any] = {}

        if isinstance(members, dict):
            members_values = dict(members.items())
        elif isclass(members) and issubclass(members, Enum):
            members_values = {member.name: member for member in members}

        return GraphQLEnumModel(
            name=base_type.graphql_name,
            members=members_values,
            ast_type=EnumTypeDefinitionNode,
            ast=cast(EnumTypeDefinitionNode, base_type.graphql_def),
        )

    @classmethod
    def construct_directive_model(cls, base_type: type[DirectiveType]):
        """TODO: https://github.com/mirumee/ariadne-graphql-modules/issues/29"""

    @classmethod
    def construct_input_model(cls, base_type: type[InputType]) -> GraphQLInputModel:
        return GraphQLInputModel(
            name=base_type.graphql_name,
            ast_type=InputObjectTypeDefinitionNode,
            ast=cast(InputObjectTypeDefinitionNode, base_type.graphql_def),
            out_type=base_type.graphql_type,
            out_names={},
        )

    @classmethod
    def construct_interface_model(
        cls, base_type: type[InterfaceType]
    ) -> GraphQLInterfaceModel:
        return GraphQLInterfaceModel(
            name=base_type.graphql_name,
            ast_type=InterfaceTypeDefinitionNode,
            ast=cast(InterfaceTypeDefinitionNode, base_type.graphql_def),
            resolve_type=base_type.resolve_type,
            resolvers=base_type.resolvers,
            out_names={},
            aliases=base_type.__aliases__ or {},  # type: ignore
        )

    @classmethod
    def construct_scalar_model(cls, base_type: type[ScalarType]) -> GraphQLScalarModel:
        return GraphQLScalarModel(
            name=base_type.graphql_name,
            ast_type=ScalarTypeDefinitionNode,
            ast=cast(ScalarTypeDefinitionNode, base_type.graphql_def),
            serialize=base_type.serialize,
            parse_value=base_type.parse_value,
            parse_literal=base_type.parse_literal,
        )

    @classmethod
    def construct_subscription_model(
        cls, base_type: type[SubscriptionType]
    ) -> GraphQLSubscriptionModel:
        return GraphQLSubscriptionModel(
            name=base_type.graphql_name,
            ast_type=ObjectTypeDefinitionNode,
            ast=cast(ObjectTypeDefinitionNode, base_type.graphql_def),
            resolvers=base_type.resolvers,
            aliases=base_type.__aliases__ or {},  # type: ignore
            out_names={},
            subscribers=base_type.subscribers,
        )

    @classmethod
    def construct_union_model(cls, base_type: type[UnionType]) -> GraphQLUnionModel:
        return GraphQLUnionModel(
            name=base_type.graphql_name,
            ast_type=UnionTypeDefinitionNode,
            ast=cast(UnionTypeDefinitionNode, base_type.graphql_def),
            resolve_type=base_type.resolve_type,
        )
