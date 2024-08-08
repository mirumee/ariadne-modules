from typing import List, Type

from graphql import (
    EnumTypeDefinitionNode,
    InputObjectTypeDefinitionNode,
    InterfaceTypeDefinitionNode,
    NameNode,
    ObjectTypeDefinitionNode,
    ScalarTypeDefinitionNode,
    UnionTypeDefinitionNode,
)

from ariadne_graphql_modules.executable_schema import get_all_types
from ariadne_graphql_modules.next.inputtype import GraphQLInputModel
from ariadne_graphql_modules.next.interfacetype import (
    GraphQLInterfaceModel,
)
from ariadne_graphql_modules.next.scalartype import GraphQLScalarModel
from ariadne_graphql_modules.next.subscriptiontype import GraphQLSubscriptionModel
from ariadne_graphql_modules.next.uniontype import GraphQLUnionModel

from ..directive_type import DirectiveType
from ..enum_type import EnumType
from ..input_type import InputType
from ..interface_type import InterfaceType
from ..mutation_type import MutationType
from ..scalar_type import ScalarType
from ..subscription_type import SubscriptionType
from ..union_type import UnionType

from ..object_type import ObjectType

from .description import get_description_node
from ..bases import BindableType
from .base import GraphQLModel, GraphQLType
from . import GraphQLObjectModel, GraphQLEnumModel


def wrap_legacy_types(
    *bindable_types: Type[BindableType],
) -> List[Type["LegacyGraphQLType"]]:
    all_types = get_all_types(bindable_types)

    return [
        type(f"Legacy{t.__name__}", (LegacyGraphQLType,), {"__base_type__": t})
        for t in all_types
    ]


class LegacyGraphQLType(GraphQLType):
    __base_type__: Type[BindableType]
    __abstract__: bool = False

    @classmethod
    def __get_graphql_model__(cls, *_) -> GraphQLModel:
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
        else:
            raise ValueError(f"Unsupported base_type {cls.__base_type__}")

    @classmethod
    def construct_object_model(
        cls, base_type: Type[ObjectType]
    ) -> "GraphQLObjectModel":
        name = base_type.graphql_name
        description = base_type.__doc__

        return GraphQLObjectModel(
            name=name,
            ast_type=ObjectTypeDefinitionNode,
            ast=ObjectTypeDefinitionNode(
                name=NameNode(value=name),
                description=get_description_node(description),
                fields=tuple(base_type.graphql_fields.values()),
                interfaces=base_type.interfaces,
            ),
            resolvers=base_type.resolvers,
            aliases=base_type.__aliases__ or {},
            out_names=base_type.__fields_args__ or {},
        )

    @classmethod
    def construct_enum_model(cls, base_type: Type[EnumType]) -> GraphQLEnumModel:
        return GraphQLEnumModel(
            name=base_type.graphql_name,
            members=base_type.__enum__ or {},
            ast_type=EnumTypeDefinitionNode,
            ast=base_type.graphql_def,
        )

    @classmethod
    def construct_directive_model(cls, base_type: Type[DirectiveType]) -> GraphQLModel:
        """TODO: https://github.com/mirumee/ariadne-graphql-modules/issues/29"""

    @classmethod
    def construct_input_model(cls, base_type: Type[InputType]) -> GraphQLInputModel:
        return GraphQLInputModel(
            name=base_type.graphql_name,
            ast_type=InputObjectTypeDefinitionNode,
            ast=base_type.graphql_def,  # type: ignore
            out_type=base_type.graphql_type,
            out_names=base_type.graphql_fields or {},  # type: ignore
        )

    @classmethod
    def construct_interface_model(
        cls, base_type: Type[InterfaceType]
    ) -> GraphQLInterfaceModel:
        return GraphQLInterfaceModel(
            name=base_type.graphql_name,
            ast_type=InterfaceTypeDefinitionNode,
            ast=base_type.graphql_def,
            resolve_type=base_type.resolve_type,
            resolvers=base_type.resolvers,
            out_names={},
            aliases=base_type.__aliases__ or {},
        )

    @classmethod
    def construct_scalar_model(cls, base_type: Type[ScalarType]) -> GraphQLScalarModel:
        return GraphQLScalarModel(
            name=base_type.graphql_name,
            ast_type=ScalarTypeDefinitionNode,
            ast=base_type.graphql_def,
            serialize=base_type.serialize,
            parse_value=base_type.parse_value,
            parse_literal=base_type.parse_literal,
        )

    @classmethod
    def construct_subscription_model(
        cls, base_type: Type[SubscriptionType]
    ) -> GraphQLSubscriptionModel:
        return GraphQLSubscriptionModel(
            name=base_type.graphql_name,
            ast_type=ObjectTypeDefinitionNode,
            ast=base_type.graphql_def,
            resolve_type=None,
            resolvers=base_type.resolvers,
            aliases=base_type.__aliases__ or {},
            out_names=base_type.__fields_args__ or {},
            subscribers=base_type.subscribers,
        )

    @classmethod
    def construct_union_model(cls, base_type: Type[UnionType]) -> GraphQLUnionModel:
        return GraphQLUnionModel(
            name=base_type.graphql_name,
            ast_type=UnionTypeDefinitionNode,
            ast=base_type.graphql_def,
            resolve_type=base_type.resolve_type,
        )
