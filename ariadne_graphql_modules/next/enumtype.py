from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Iterable, Optional, Type, cast

from ariadne import EnumType
from graphql import (
    EnumTypeDefinitionNode,
    EnumValueDefinitionNode,
    GraphQLSchema,
    NameNode,
)

from .base import GraphQLModel
from .description import get_description_node


def create_graphql_enum_model(
    enum: Type[Enum],
    *,
    name: Optional[str] = None,
    description: Optional[str] = None,
    members_descriptions: Optional[Dict[str, str]] = None,
    members_include: Optional[Iterable[str]] = None,
    members_exclude: Optional[Iterable[str]] = None,
) -> "GraphQLEnumModel":
    if members_include and members_exclude:
        raise ValueError(
            "'members_include' and 'members_exclude' " "options are mutually exclusive."
        )

    if hasattr(enum, "__get_graphql_model__"):
        return cast(GraphQLEnumModel, enum.__get_graphql_model__())

    if not name:
        if hasattr(enum, "__get_graphql_name__"):
            name = cast("str", enum.__get_graphql_name__())
        else:
            name = enum.__name__

    members: Dict[str, Any] = {i.name: i for i in enum}
    final_members: Dict[str, Any] = {}

    if members_include:
        for key, value in members.items():
            if key in members_include:
                final_members[key] = value
    elif members_exclude:
        for key, value in members.items():
            if key not in members_exclude:
                final_members[key] = value
    else:
        final_members = members

    members_descriptions = members_descriptions or {}
    for member in members_descriptions:
        if member not in final_members:
            raise ValueError(
                f"Member description was specified for a member '{member}' "
                "not present in final GraphQL enum."
            )

    return GraphQLEnumModel(
        name=name,
        members=final_members,
        ast_type=EnumTypeDefinitionNode,
        ast=EnumTypeDefinitionNode(
            name=NameNode(value=name),
            description=get_description_node(description),
            values=tuple(
                EnumValueDefinitionNode(
                    name=NameNode(value=value_name),
                    description=get_description_node(
                        members_descriptions.get(value_name)
                    ),
                )
                for value_name in final_members
            ),
        ),
    )


@dataclass(frozen=True)
class GraphQLEnumModel(GraphQLModel):
    members: Dict[str, Any]

    def bind_to_schema(self, schema: GraphQLSchema):
        bindable = EnumType(self.name, values=self.members)
        bindable.bind_to_schema(schema)


def graphql_enum(
    cls: Optional[Type[Enum]] = None,
    *,
    name: Optional[str] = None,
    description: Optional[str] = None,
    members_descriptions: Optional[Dict[str, str]] = None,
    members_include: Optional[Iterable[str]] = None,
    members_exclude: Optional[Iterable[str]] = None,
):
    def graphql_enum_decorator(cls: Type[Enum]):
        graphql_model = create_graphql_enum_model(
            cls,
            name=name,
            description=description,
            members_descriptions=members_descriptions,
            members_include=members_include,
            members_exclude=members_exclude,
        )

        @classmethod
        def __get_graphql_model__(*_) -> GraphQLEnumModel:
            return graphql_model

        setattr(cls, "__get_graphql_model__", __get_graphql_model__)
        return cls

    if cls:
        return graphql_enum_decorator(cls)

    return graphql_enum_decorator
