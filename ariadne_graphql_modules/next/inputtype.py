from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Type, cast

from ariadne import InputType as InputTypeBindable
from graphql import (
    GraphQLSchema,
    InputObjectTypeDefinitionNode,
    InputValueDefinitionNode,
    NameNode,
)

from ..utils import parse_definition
from .base import GraphQLMetadata, GraphQLModel, GraphQLType
from .convert_name import (
    convert_graphql_name_to_python,
    convert_python_name_to_graphql,
)
from .description import get_description_node
from .typing import get_graphql_type, get_type_node
from .validators import validate_description, validate_name


class GraphQLInput(GraphQLType):
    __kwargs__: List[str]
    __out_names__: Optional[Dict[str, str]] = None

    def __init__(self, **kwargs: Any):
        for kwarg in self.__kwargs__:
            setattr(self, kwarg, kwargs.get(kwarg))

        for kwarg in kwargs:
            if kwarg not in self.__kwargs__:
                valid_kwargs = "', '".join(self.__kwargs__)
                raise TypeError(
                    f"{type(self).__name__}.__init__() got an unexpected "
                    f"keyword argument '{kwarg}'. "
                    f"Valid keyword arguments: '{valid_kwargs}'"
                )

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
    def create_from_data(cls, data: Dict[str, Any]) -> "GraphQLInput":
        return cls(**data)

    @classmethod
    def __get_graphql_model__(cls, metadata: GraphQLMetadata) -> "GraphQLModel":
        name = cls.__get_graphql_name__()
        metadata.set_graphql_name(cls, name)

        if getattr(cls, "__schema__", None):
            return cls.__get_graphql_model_with_schema__(metadata, name)

        return cls.__get_graphql_model_without_schema__(metadata, name)

    @classmethod
    def __get_graphql_model_with_schema__(
        cls, metadata: GraphQLMetadata, name: str
    ) -> "GraphQLInputModel":
        definition = cast(
            InputObjectTypeDefinitionNode,
            parse_definition(InputObjectTypeDefinitionNode, cls.__schema__),
        )

        out_names: Dict[str, str] = {}
        if getattr(cls, "__out_names__"):
            out_names.update(cls.__out_names__)

        fields: List[InputValueDefinitionNode] = []
        for field in definition.fields:
            fields.append(
                InputValueDefinitionNode(
                    name=field.name,
                    description=(field.description),
                    directives=field.directives,
                    type=field.type,
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
                    cls,
                    metadata,
                    hint_field_name,
                    hint_type,
                    fields_descriptions.get(hint_name),
                )
            )

            out_names[hint_field_name] = hint_name

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
    definition = cast(
        InputObjectTypeDefinitionNode,
        parse_definition(InputObjectTypeDefinitionNode, cls.__schema__),
    )

    if not isinstance(definition, InputObjectTypeDefinitionNode):
        raise ValueError(
            f"Class '{cls.__name__}' defines '__schema__' attribute "
            "with declaration for an invalid GraphQL type. "
            f"('{definition.__class__.__name__}' != "
            f"'{InputObjectTypeDefinitionNode.__name__}')"
        )

    validate_name(cls, definition)
    validate_description(cls, definition)

    if not definition.fields:
        raise ValueError(
            f"Class '{cls.__name__}' defines '__schema__' attribute "
            "with declaration for an input type without any fields. "
        )

    fields_names: List[str] = [field.name.value for field in definition.fields]
    used_out_names: List[str] = []

    out_names: Dict[str, str] = getattr(cls, "__out_names__", {}) or {}
    for field_name, out_name in out_names.items():
        if field_name not in fields_names:
            raise ValueError(
                f"Class '{cls.__name__}' defines an outname for '{field_name}' "
                "field in it's '__out_names__' attribute which is not defined "
                "in '__schema__'."
            )

        if out_name in used_out_names:
            raise ValueError(
                f"Class '{cls.__name__}' defines multiple fields with an outname "
                f"'{out_name}' in it's '__out_names__' attribute."
            )

        used_out_names.append(out_name)

    cls.__kwargs__ = get_input_type_with_schema_kwargs(cls, definition, out_names)


def get_input_type_with_schema_kwargs(
    cls: Type[GraphQLInput],
    definition: InputObjectTypeDefinitionNode,
    out_names: Dict[str, str],
) -> List[str]:
    kwargs: List[str] = []
    for field in definition.fields:
        try:
            kwargs.append(out_names[field.name.value])
        except KeyError:
            kwargs.append(convert_graphql_name_to_python(field.name.value))
    return kwargs


def validate_input_type(cls: Type[GraphQLInput]):
    if cls.__out_names__:
        raise ValueError(
            f"Class '{cls.__name__}' defines '__out_names__' attribute. "
            "This is not supported for types not defining '__schema__'."
        )

    cls.__kwargs__ = get_input_type_kwargs(cls)


def get_input_type_kwargs(cls: Type[GraphQLInput]) -> List[str]:
    fields: List[str] = []

    for attr_name in cls.__annotations__:
        if attr_name.startswith("__"):
            continue

        attr_value = getattr(cls, attr_name, None)
        if attr_value is None or isinstance(attr_value, GraphQLInputField):
            fields.append(attr_name)

    return fields


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
    parent_type: GraphQLInput,
    metadata: GraphQLMetadata,
    field_name: str,
    field_type: Any,
    field_description: Optional[str] = None,
) -> InputValueDefinitionNode:
    return InputValueDefinitionNode(
        description=get_description_node(field_description),
        name=NameNode(value=field_name),
        type=get_type_node(metadata, field_type, parent_type),
        default_value=None,
    )
