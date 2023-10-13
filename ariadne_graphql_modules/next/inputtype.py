from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Type

from ariadne import InputType as InputTypeBindable
from graphql import (
    GraphQLSchema,
    InputObjectTypeDefinitionNode,
    InputValueDefinitionNode,
    NameNode,
)

from .base import GraphQLMetadata, GraphQLModel, GraphQLType
from .convert_name import convert_python_name_to_graphql
from .description import get_description_node
from .typing import get_graphql_type, get_type_node
from .validators import validate_description, validate_name


class GraphQLInput(GraphQLType):
    def __init__(self, data: dict):
        raise NotImplementedError("GraphQLType.__init__() is not implemented")

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        if cls.__dict__.get("__abstract__"):
            return

        cls.__abstract__ = False

        if cls.__dict__.get("__schema__"):
            validate_input_type_with_schema(cls)
        else:
            validate_input_type(cls)

    @classmethod
    def __get_graphql_model__(cls, metadata: GraphQLMetadata) -> "GraphQLModel":
        name = cls.__get_graphql_name__()

        if getattr(cls, "__schema__", None):
            return cls.__get_graphql_model_with_schema__(metadata, name)

        return cls.__get_graphql_model_without_schema__(metadata, name)

    @classmethod
    def __get_graphql_model_with_schema__(
        cls, metadata: GraphQLMetadata, name: str
    ) -> "GraphQLInputModel":
        pass

    @classmethod
    def __get_graphql_model_without_schema__(
        cls, metadata: GraphQLMetadata, name: str
    ) -> "GraphQLInputModel":
        type_hints = cls.__annotations__
        fields_instances: Dict[str, GraphQLInputField] = {}
        fields_descriptions: Dict[str, str] = {}

        for attr_name in dir(cls):
            cls_attr = getattr(cls, attr_name)
            if isinstance(cls_attr, GraphQLInputField):
                fields_instances[attr_name] = cls_attr
                if cls_attr.description:
                    fields_descriptions[attr_name] = cls_attr.description

        fields_ast: List[InputValueDefinitionNode] = []
        out_names: Dict[str, str] = {}

        for hint_name, hint_type in type_hints.items():
            if hint_name.startswith("__"):
                continue

            if hint_name in fields_instances:
                continue

            hint_field_name = convert_python_name_to_graphql(hint_name)
            fields_ast.append(
                get_field_node_from_type_hint(
                    metadata,
                    hint_field_name,
                    hint_type,
                    fields_descriptions.get(hint_name),
                )
            )

        return GraphQLInputModel(
            name=name,
            ast_type=InputObjectTypeDefinitionNode,
            ast=InputObjectTypeDefinitionNode(
                name=NameNode(value=name),
                description=get_description_node(
                    getattr(cls, "__description__", None),
                ),
                fields=tuple(fields_ast),
            ),
            out_type=cls,
            out_names=out_names,
        )

    @classmethod
    def __get_graphql_types__(
        cls, metadata: "GraphQLMetadata"
    ) -> Iterable["GraphQLType"]:
        """Returns iterable with GraphQL types associated with this type"""
        types: List[GraphQLType] = [cls]

        for attr_name in dir(cls):
            cls_attr = getattr(cls, attr_name)
            if isinstance(cls_attr, GraphQLInputField):
                if cls_attr.type:
                    field_graphql_type = get_graphql_type(cls_attr.type)
                    if field_graphql_type and field_graphql_type not in types:
                        types.append(field_graphql_type)

        type_hints = cls.__annotations__
        for hint_name, hint_type in type_hints.values():
            if hint_name.startswith("__"):
                continue

            hint_graphql_type = get_graphql_type(hint_type)
            if hint_graphql_type and hint_graphql_type not in types:
                types.append(hint_graphql_type)

        return types

    @staticmethod
    def field(
        *,
        name: Optional[str] = None,
        type: Optional[Any] = None,
        description: Optional[str] = None,
    ):
        """Shortcut for GraphQLInputField()"""
        return GraphQLInputField(
            name=name,
            type=type,
            description=description,
        )


def validate_input_type_with_schema(cls: Type[GraphQLInput]):
    pass


def validate_input_type(cls: Type[GraphQLInput]):
    pass


class GraphQLInputField:
    name: Optional[str]
    description: Optional[str]
    type: Optional[Any]
    default_value: Optional[Any]

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        type: Optional[Any] = None,
        default_value: Optional[Any] = None,
    ):
        self.name = name
        self.description = description
        self.type = type
        self.default_value = default_value


@dataclass(frozen=True)
class GraphQLInputModel(GraphQLModel):
    out_type: Any
    out_names: Dict[str, str]

    def bind_to_schema(self, schema: GraphQLSchema):
        bindable = InputTypeBindable(self.name, self.out_type, self.out_names)
        bindable.bind_to_schema(schema)


def get_field_node_from_type_hint(
    metadata: GraphQLMetadata,
    field_name: str,
    field_type: Any,
    field_description: Optional[str] = None,
) -> InputValueDefinitionNode:
    return InputValueDefinitionNode(
        description=get_description_node(field_description),
        name=NameNode(value=field_name),
        type=get_type_node(metadata, field_type),
        default_value=None,
    )
