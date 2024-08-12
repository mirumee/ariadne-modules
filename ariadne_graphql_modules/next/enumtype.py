from dataclasses import dataclass
from enum import Enum
from inspect import isclass
from typing import Any, Dict, Iterable, List, Optional, Set, Type, Union, cast

from ariadne import EnumType
from graphql import (
    EnumTypeDefinitionNode,
    EnumValueDefinitionNode,
    GraphQLSchema,
    NameNode,
)

from ..utils import parse_definition
from .base import GraphQLMetadata, GraphQLModel, GraphQLType
from .description import get_description_node
from .validators import validate_description, validate_name


class GraphQLEnum(GraphQLType):
    __abstract__: bool = True
    __schema__: Optional[str]
    __description__: Optional[str]
    __members__: Optional[Union[Type[Enum], Dict[str, Any], List[str]]]
    __members_descriptions__: Optional[Dict[str, str]]

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        if cls.__dict__.get("__abstract__"):
            return

        cls.__abstract__ = False

        if cls.__dict__.get("__schema__"):
            validate_enum_type_with_schema(cls)
        else:
            validate_enum_type(cls)

    @classmethod
    def __get_graphql_model__(cls, metadata: GraphQLMetadata) -> "GraphQLModel":
        name = cls.__get_graphql_name__()

        if getattr(cls, "__schema__", None):
            return cls.__get_graphql_model_with_schema__(name)

        return cls.__get_graphql_model_without_schema__(name)

    # pylint: disable=E1101
    @classmethod
    def __get_graphql_model_with_schema__(cls, name: str) -> "GraphQLEnumModel":
        definition = cast(
            EnumTypeDefinitionNode,
            parse_definition(EnumTypeDefinitionNode, cls.__schema__),
        )

        members = getattr(cls, "__members__", [])
        members_values: Dict[str, Any] = {}
        if isinstance(members, dict):
            members_values = dict(members.items())
        elif isclass(members) and issubclass(members, Enum):
            members_values = {i.name: i for i in members}
        else:
            members_values = {i.name.value: i.name.value for i in definition.values}

        members_descriptions = getattr(cls, "__members_descriptions__", {})

        return GraphQLEnumModel(
            name=name,
            members=members_values,
            ast_type=EnumTypeDefinitionNode,
            ast=EnumTypeDefinitionNode(
                name=NameNode(value=name),
                directives=definition.directives,
                description=definition.description
                or (get_description_node(getattr(cls, "__description__", None))),
                values=tuple(
                    EnumValueDefinitionNode(
                        name=value.name,
                        directives=value.directives,
                        description=value.description
                        or (
                            get_description_node(
                                members_descriptions.get(value.name.value),
                            )
                        ),
                    )
                    for value in definition.values
                ),
            ),
        )

    @classmethod
    def __get_graphql_model_without_schema__(cls, name: str) -> "GraphQLEnumModel":
        members = getattr(cls, "__members__", [])
        members_values = {}
        if isinstance(members, dict):
            members_values = dict(members.items())
        elif isclass(members) and issubclass(members, Enum):
            members_values = {i.name: i for i in members}
        elif isinstance(members, list):
            members_values = {kv: kv for kv in members}

        members_descriptions = getattr(cls, "__members_descriptions__", {})

        return GraphQLEnumModel(
            name=name,
            members=members_values,
            ast_type=EnumTypeDefinitionNode,
            ast=EnumTypeDefinitionNode(
                name=NameNode(value=name),
                description=get_description_node(
                    getattr(cls, "__description__", None),
                ),
                values=tuple(
                    EnumValueDefinitionNode(
                        name=NameNode(value=value_name),
                        description=get_description_node(
                            members_descriptions.get(value_name)
                        ),
                    )
                    for value_name in members_values
                ),
            ),
        )


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
            "'members_include' and 'members_exclude' options are mutually exclusive."
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


# pylint: disable=E1101
def validate_enum_type_with_schema(cls: Type[GraphQLEnum]):
    definition = parse_definition(EnumTypeDefinitionNode, cls.__schema__)

    if not isinstance(definition, EnumTypeDefinitionNode):
        raise ValueError(
            f"Class '{cls.__name__}' defines '__schema__' attribute "
            f"with declaration for an invalid GraphQL type. "
            f"('{definition.__class__.__name__}' != '{EnumTypeDefinitionNode.__name__}')"
        )

    validate_name(cls, definition)
    validate_description(cls, definition)

    members_names = {value.name.value for value in definition.values}
    if not members_names:
        raise ValueError(
            f"Class '{cls.__name__}' defines '__schema__' attribute "
            "that doesn't declare any enum members."
        )

    members_values = getattr(cls, "__members__", None)
    if members_values:
        validate_members_values(cls, members_values, members_names)

    members_descriptions = getattr(cls, "__members_descriptions__", {})
    validate_enum_members_descriptions(cls, members_names, members_descriptions)

    duplicate_descriptions = [
        ast_member.name.value
        for ast_member in definition.values
        if ast_member.description
        and ast_member.description.value
        and members_descriptions.get(ast_member.name.value)
    ]

    if duplicate_descriptions:
        raise ValueError(
            f"Class '{cls.__name__}' '__members_descriptions__' attribute defines "
            f"descriptions for enum members that also have description in '__schema__' "
            f"attribute. (members: '{', '.join(duplicate_descriptions)}')"
        )


def validate_members_values(cls, members_values, members_names):
    if isinstance(members_values, list):
        raise ValueError(
            f"Class '{cls.__name__}' '__members__' attribute "
            "can't be a list when used together with '__schema__'."
        )

    missing_members = None
    if isinstance(members_values, dict):
        missing_members = members_names - set(members_values)
    elif isclass(members_values) and issubclass(members_values, Enum):
        missing_members = members_names - {value.name for value in members_values}

    if missing_members:
        raise ValueError(
            f"Class '{cls.__name__}' '__members__' is missing values "
            f"for enum members defined in '__schema__'. "
            f"(missing items: '{', '.join(missing_members)}')"
        )


def validate_enum_type(cls: Type[GraphQLEnum]):
    members_values = getattr(cls, "__members__", None)
    if not members_values:
        raise ValueError(
            f"Class '{cls.__name__}' '__members__' attribute is either missing or "
            "empty. Either define it or provide full SDL for this enum using "
            "the '__schema__' attribute."
        )

    if not any(
        [
            isinstance(members_values, (dict, list)),
            isclass(members_values) and issubclass(members_values, Enum),
        ]
    ):
        raise ValueError(
            f"Class '{cls.__name__}' '__members__' attribute is of unsupported type. "
            f"Expected 'Dict[str, Any]', 'Type[Enum]' or List[str]. "
            f"(found: '{type(members_values)}')"
        )

    members_names = get_members_set(members_values)
    members_descriptions = getattr(cls, "__members_descriptions__", {})
    validate_enum_members_descriptions(cls, members_names, members_descriptions)


def validate_enum_members_descriptions(
    cls: Type[GraphQLEnum], members: Set[str], members_descriptions: dict
):
    invalid_descriptions = set(members_descriptions) - members
    if invalid_descriptions:
        invalid_descriptions_str = "', '".join(invalid_descriptions)
        raise ValueError(
            f"Class '{cls.__name__}' '__members_descriptions__' attribute defines "
            f"descriptions for undefined enum members. "
            f"(undefined members: '{invalid_descriptions_str}')"
        )


def get_members_set(
    members: Optional[Union[Type[Enum], Dict[str, Any], List[str]]]
) -> Set[str]:
    if isinstance(members, dict):
        return set(members.keys())

    if isclass(members) and issubclass(members, Enum):
        return set(member.name for member in members)

    return set(members)
