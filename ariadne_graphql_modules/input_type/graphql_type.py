from copy import deepcopy
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Type, Union, cast

from graphql import InputObjectTypeDefinitionNode, InputValueDefinitionNode, NameNode

from .graphql_field import GraphQLInputField
from ..base import GraphQLMetadata, GraphQLModel, GraphQLType
from ..convert_name import (
    convert_graphql_name_to_python,
    convert_python_name_to_graphql,
)
from ..description import get_description_node
from .models import GraphQLInputModel
from .validators import (
    validate_input_type,
    validate_input_type_with_schema,
)
from ..typing import get_graphql_type, get_type_node
from ..value import get_value_node
from ..utils import parse_definition


class GraphQLInput(GraphQLType):
    __kwargs__: Dict[str, Any]
    __schema__: Optional[str]
    __out_names__: Optional[Dict[str, str]] = None

    def __init__(self, **kwargs: Any):
        for kwarg in kwargs:
            if kwarg not in self.__kwargs__:
                valid_kwargs = "', '".join(self.__kwargs__)
                raise TypeError(
                    f"{type(self).__name__}.__init__() got an unexpected "
                    f"keyword argument '{kwarg}'. "
                    f"Valid keyword arguments: '{valid_kwargs}'"
                )

        for kwarg, default in self.__kwargs__.items():
            setattr(self, kwarg, kwargs.get(kwarg, deepcopy(default)))

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        if cls.__dict__.get("__abstract__"):
            return

        cls.__abstract__ = False

        if cls.__dict__.get("__schema__"):
            cls.__kwargs__ = validate_input_type_with_schema(cls)
        else:
            cls.__kwargs__ = validate_input_type(cls)

    @classmethod
    def create_from_data(cls, data: Dict[str, Any]) -> "GraphQLInput":
        return cls(**data)

    @classmethod
    def __get_graphql_model__(cls, metadata: GraphQLMetadata) -> "GraphQLModel":
        name = cls.__get_graphql_name__()
        metadata.set_graphql_name(cls, name)

        if getattr(cls, "__schema__", None):
            return cls.__get_graphql_model_with_schema__()

        return cls.__get_graphql_model_without_schema__(metadata, name)

    @classmethod
    def __get_graphql_model_with_schema__(cls) -> "GraphQLInputModel":
        definition = cast(
            InputObjectTypeDefinitionNode,
            parse_definition(InputObjectTypeDefinitionNode, cls.__schema__),
        )

        out_names: Dict[str, str] = getattr(cls, "__out_names__") or {}

        fields: List[InputValueDefinitionNode] = []
        for field in definition.fields:
            fields.append(
                InputValueDefinitionNode(
                    name=field.name,
                    description=field.description,
                    directives=field.directives,
                    type=field.type,
                    default_value=field.default_value,
                )
            )

            field_name = field.name.value
            if field_name not in out_names:
                out_names[field_name] = convert_graphql_name_to_python(field_name)

        return GraphQLInputModel(
            name=definition.name.value,
            ast_type=InputObjectTypeDefinitionNode,
            ast=InputObjectTypeDefinitionNode(
                name=NameNode(value=definition.name.value),
                fields=tuple(fields),
            ),
            out_type=cls.create_from_data,
            out_names=out_names,
        )

    @classmethod
    def __get_graphql_model_without_schema__(
        cls, metadata: GraphQLMetadata, name: str
    ) -> "GraphQLInputModel":
        type_hints = cls.__annotations__  # pylint: disable=no-member
        fields_instances: Dict[str, GraphQLInputField] = {
            attr_name: getattr(cls, attr_name)
            for attr_name in dir(cls)
            if isinstance(getattr(cls, attr_name), GraphQLInputField)
        }

        fields_ast: List[InputValueDefinitionNode] = []
        out_names: Dict[str, str] = {}

        for hint_name, hint_type in type_hints.items():
            if hint_name.startswith("__"):
                continue

            cls_attr = getattr(cls, hint_name, None)
            default_name = convert_python_name_to_graphql(hint_name)

            if isinstance(cls_attr, GraphQLInputField):
                fields_ast.append(
                    get_field_node_from_type_hint(
                        cls,
                        metadata,
                        cls_attr.name or default_name,
                        cls_attr.graphql_type or hint_type,
                        cls_attr.description,
                        cls_attr.default_value,
                    )
                )
                out_names[cls_attr.name or default_name] = hint_name
                fields_instances.pop(hint_name, None)
            elif not callable(cls_attr):
                fields_ast.append(
                    get_field_node_from_type_hint(
                        cls,
                        metadata,
                        default_name,
                        hint_type,
                        None,
                        cls_attr,
                    )
                )
                out_names[default_name] = hint_name

        for attr_name, field_instance in fields_instances.items():
            default_name = convert_python_name_to_graphql(attr_name)
            fields_ast.append(
                get_field_node_from_type_hint(
                    cls,
                    metadata,
                    field_instance.name or default_name,
                    field_instance.graphql_type,
                    field_instance.description,
                    field_instance.default_value,
                )
            )
            out_names[field_instance.name or default_name] = attr_name

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
            out_type=cls.create_from_data,
            out_names=out_names,
        )

    @classmethod
    def __get_graphql_types__(
        cls, _: "GraphQLMetadata"
    ) -> Iterable[Union[Type["GraphQLType"], Type[Enum]]]:
        """Returns iterable with GraphQL types associated with this type"""
        types: List[Union[Type["GraphQLType"], Type[Enum]]] = [cls]

        for attr_name in dir(cls):
            cls_attr = getattr(cls, attr_name)
            if isinstance(cls_attr, GraphQLInputField):
                if cls_attr.graphql_type:
                    field_graphql_type = get_graphql_type(cls_attr.graphql_type)
                    if field_graphql_type and field_graphql_type not in types:
                        types.append(field_graphql_type)

        type_hints = cls.__annotations__  # pylint: disable=no-member
        for hint_name, hint_type in type_hints.items():
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
        graphql_type: Optional[Any] = None,
        description: Optional[str] = None,
        default_value: Optional[Any] = None,
    ) -> Any:
        """Shortcut for GraphQLInputField()"""
        return GraphQLInputField(
            name=name,
            graphql_type=graphql_type,
            description=description,
            default_value=default_value,
        )


def get_field_node_from_type_hint(
    parent_type: Type[GraphQLInput],
    metadata: GraphQLMetadata,
    field_name: str,
    field_type: Any,
    field_description: Optional[str] = None,
    field_default_value: Optional[Any] = None,
) -> InputValueDefinitionNode:
    if field_default_value is not None:
        default_value = get_value_node(field_default_value)
    else:
        default_value = None

    return InputValueDefinitionNode(
        description=get_description_node(field_description),
        name=NameNode(value=field_name),
        type=get_type_node(metadata, field_type, parent_type),
        default_value=default_value,
    )
