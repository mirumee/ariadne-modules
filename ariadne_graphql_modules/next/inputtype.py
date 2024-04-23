from copy import deepcopy
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
from .value import get_value_from_node, get_value_node


class GraphQLInput(GraphQLType):
    __kwargs__: Dict[str, Any]
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
        type_hints = cls.__annotations__
        fields_instances: Dict[str, GraphQLInputField] = {}

        for attr_name in dir(cls):
            cls_attr = getattr(cls, attr_name)
            if isinstance(cls_attr, GraphQLInputField):
                fields_instances[attr_name] = cls_attr

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
                        cls_attr.type or hint_type,
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

        for attr_name, field_instance in fields_instances:
            default_name = convert_python_name_to_graphql(hint_name)
            fields_ast.append(
                get_field_node_from_type_hint(
                    cls,
                    metadata,
                    field_instance.name or default_name,
                    field_instance.type,
                    field_instance.description,
                    field_instance.default_value,
                )
            )
            out_names[cls_attr.name or default_name] = hint_name

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
        type: Optional[Any] = None,
        description: Optional[str] = None,
        default_value: Optional[Any] = None,
    ):
        """Shortcut for GraphQLInputField()"""
        return GraphQLInputField(
            name=name,
            type=type,
            description=description,
            default_value=default_value,
        )


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


def validate_input_type_with_schema(cls: Type[GraphQLInput]) -> Dict[str, Any]:
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

    return get_input_type_with_schema_kwargs(cls, definition, out_names)


def get_input_type_with_schema_kwargs(
    cls: Type[GraphQLInput],
    definition: InputObjectTypeDefinitionNode,
    out_names: Dict[str, str],
) -> Dict[str, Any]:
    kwargs: Dict[str, Any] = {}
    for field in definition.fields:
        try:
            python_name = out_names[field.name.value]
        except KeyError:
            python_name = convert_graphql_name_to_python(field.name.value)

        attr_default_value = getattr(cls, python_name, None)
        if attr_default_value is not None and not callable(attr_default_value):
            default_value = attr_default_value
        elif field.default_value:
            default_value = get_value_from_node(field.default_value)
        else:
            default_value = None

        kwargs[python_name] = default_value

    return kwargs


def validate_input_type(cls: Type[GraphQLInput]) -> Dict[str, Any]:
    if cls.__out_names__:
        raise ValueError(
            f"Class '{cls.__name__}' defines '__out_names__' attribute. "
            "This is not supported for types not defining '__schema__'."
        )

    return get_input_type_kwargs(cls)


def get_input_type_kwargs(cls: Type[GraphQLInput]) -> Dict[str, Any]:
    kwargs: Dict[str, Any] = {}

    for attr_name in cls.__annotations__:
        if attr_name.startswith("__"):
            continue

        attr_value = getattr(cls, attr_name, None)
        if isinstance(attr_value, GraphQLInputField):
            validate_field_default_value(cls, attr_name, attr_value.default_value)
            kwargs[attr_name] = attr_value.default_value
        elif not callable(attr_value):
            validate_field_default_value(cls, attr_name, attr_value)
            kwargs[attr_name] = attr_value

    return kwargs


def validate_field_default_value(
    cls: Type[GraphQLInput], field_name: str, default_value: Any
):
    if default_value is None:
        return

    try:
        get_value_node(default_value)
    except TypeError as e:
        raise TypeError(
            f"Class '{cls.__name__}' defines default value "
            f"for the '{field_name}' field that can't be "
            "represented in GraphQL schema."
        ) from e
