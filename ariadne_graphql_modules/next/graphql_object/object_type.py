from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Type,
    Union,
    cast,
)

from ariadne.types import Resolver, Subscriber
from graphql import (
    FieldDefinitionNode,
    InputValueDefinitionNode,
    NameNode,
    NamedTypeNode,
    ObjectTypeDefinitionNode,
    StringValueNode,
)

from .object_field import (
    GraphQLObjectField,
    GraphQLObjectFieldArg,
    GraphQLObjectResolver,
    GraphQLObjectSource,
    object_field,
    object_resolver,
)
from .object_model import GraphQLObjectModel
from .utils import (
    get_field_args_from_resolver,
    get_field_args_from_subscriber,
    get_field_args_out_names,
    get_field_node_from_obj_field,
    update_field_args_options,
)

from ...utils import parse_definition
from ..base import GraphQLMetadata, GraphQLModel, GraphQLType
from ..convert_name import convert_python_name_to_graphql
from ..description import get_description_node
from ..typing import get_graphql_type
from .validators import (
    validate_object_type_with_schema,
    validate_object_type_without_schema,
)
from ..value import get_value_node


@dataclass(frozen=True)
class GraphQLObjectData:
    fields: Dict[str, "GraphQLObjectField"]
    interfaces: List[str]


class GraphQLObject(GraphQLType):
    __kwargs__: Dict[str, Any]
    __abstract__: bool = True
    __schema__: Optional[str]
    __description__: Optional[str]
    __aliases__: Optional[Dict[str, str]]
    __requires__: Optional[Iterable[Union[Type[GraphQLType], Type[Enum]]]]
    __implements__: Optional[Iterable[Type[GraphQLType]]]

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
            valid_type = getattr(cls, "__valid_type__", ObjectTypeDefinitionNode)
            cls.__kwargs__ = validate_object_type_with_schema(cls, valid_type)
        else:
            cls.__kwargs__ = validate_object_type_without_schema(cls)

    @classmethod
    def __get_graphql_model__(cls, metadata: GraphQLMetadata) -> "GraphQLModel":
        name = cls.__get_graphql_name__()
        metadata.set_graphql_name(cls, name)

        if getattr(cls, "__schema__", None):
            return cls.__get_graphql_model_with_schema__()

        return cls.__get_graphql_model_without_schema__(metadata, name)

    @classmethod
    def __get_graphql_model_with_schema__(cls) -> "GraphQLModel":
        definition = cast(
            ObjectTypeDefinitionNode,
            parse_definition(ObjectTypeDefinitionNode, cls.__schema__),
        )

        descriptions: Dict[str, StringValueNode] = {}
        args_descriptions: Dict[str, Dict[str, StringValueNode]] = {}
        args_defaults: Dict[str, Dict[str, Any]] = {}
        resolvers: Dict[str, Resolver] = {}
        out_names: Dict[str, Dict[str, str]] = {}

        for attr_name in dir(cls):
            cls_attr = getattr(cls, attr_name)
            if isinstance(cls_attr, GraphQLObjectResolver):
                resolvers[cls_attr.field] = cls_attr.resolver
                description_node = get_description_node(cls_attr.description)
                if description_node:
                    descriptions[cls_attr.field] = description_node

                field_args = get_field_args_from_resolver(cls_attr.resolver)
                if field_args:
                    args_descriptions[cls_attr.field] = {}
                    args_defaults[cls_attr.field] = {}

                    final_args = update_field_args_options(field_args, cls_attr.args)

                    for arg_name, arg_options in final_args.items():
                        arg_description = get_description_node(arg_options.description)
                        if arg_description:
                            args_descriptions[cls_attr.field][
                                arg_name
                            ] = arg_description

                        arg_default = arg_options.default_value
                        if arg_default is not None:
                            args_defaults[cls_attr.field][arg_name] = get_value_node(
                                arg_default
                            )

        fields: List[FieldDefinitionNode] = []
        for field in definition.fields:
            field_args_descriptions = args_descriptions.get(field.name.value, {})
            field_args_defaults = args_defaults.get(field.name.value, {})

            args: List[InputValueDefinitionNode] = []
            for arg in field.arguments:
                arg_name = arg.name.value
                args.append(
                    InputValueDefinitionNode(
                        description=(
                            arg.description or field_args_descriptions.get(arg_name)
                        ),
                        name=arg.name,
                        directives=arg.directives,
                        type=arg.type,
                        default_value=(
                            arg.default_value or field_args_defaults.get(arg_name)
                        ),
                    )
                )

            fields.append(
                FieldDefinitionNode(
                    name=field.name,
                    description=(
                        field.description or descriptions.get(field.name.value)
                    ),
                    directives=field.directives,
                    arguments=tuple(args),
                    type=field.type,
                )
            )

        return GraphQLObjectModel(
            name=definition.name.value,
            ast_type=ObjectTypeDefinitionNode,
            ast=ObjectTypeDefinitionNode(
                name=NameNode(value=definition.name.value),
                fields=tuple(fields),
                interfaces=definition.interfaces,
            ),
            resolvers=resolvers,
            aliases=getattr(cls, "__aliases__", {}),
            out_names=out_names,
        )

    @classmethod
    def __get_graphql_model_without_schema__(
        cls, metadata: GraphQLMetadata, name: str
    ) -> "GraphQLModel":
        type_data = get_graphql_object_data(metadata, cls)
        type_aliases = getattr(cls, "__aliases__", {})

        fields_ast: List[FieldDefinitionNode] = []
        resolvers: Dict[str, Resolver] = {}
        aliases: Dict[str, str] = {}
        out_names: Dict[str, Dict[str, str]] = {}

        for attr_name, field in type_data.fields.items():
            fields_ast.append(get_field_node_from_obj_field(cls, metadata, field))

            if attr_name in type_aliases and field.name:
                aliases[field.name] = type_aliases[attr_name]
            elif field.name and attr_name != field.name and not field.resolver:
                aliases[field.name] = attr_name

            if field.resolver and field.name:
                resolvers[field.name] = field.resolver

            if field.args and field.name:
                out_names[field.name] = get_field_args_out_names(field.args)

        interfaces_ast: List[NamedTypeNode] = []
        for interface_name in type_data.interfaces:
            interfaces_ast.append(NamedTypeNode(name=NameNode(value=interface_name)))

        return GraphQLObjectModel(
            name=name,
            ast_type=ObjectTypeDefinitionNode,
            ast=ObjectTypeDefinitionNode(
                name=NameNode(value=name),
                description=get_description_node(
                    getattr(cls, "__description__", None),
                ),
                fields=tuple(fields_ast),
                interfaces=tuple(interfaces_ast),
            ),
            resolvers=resolvers,
            aliases=aliases,
            out_names=out_names,
        )

    @classmethod
    def __get_graphql_types__(
        cls, metadata: "GraphQLMetadata"
    ) -> Iterable[Union[Type["GraphQLType"], Type[Enum]]]:
        """Returns iterable with GraphQL types associated with this type"""
        if getattr(cls, "__schema__", None):
            return cls.__get_graphql_types_with_schema__(metadata)

        return cls.__get_graphql_types_without_schema__(metadata)

    @classmethod
    def __get_graphql_types_with_schema__(
        cls, _: "GraphQLMetadata"
    ) -> Iterable[Type["GraphQLType"]]:
        types: List[Type["GraphQLType"]] = [cls]
        types.extend(getattr(cls, "__requires__", []))
        types.extend(getattr(cls, "__implements__", []))
        return types

    @classmethod
    def __get_graphql_types_without_schema__(
        cls, metadata: "GraphQLMetadata"
    ) -> Iterable[Union[Type["GraphQLType"], Type[Enum]]]:
        types: List[Union[Type["GraphQLType"], Type[Enum]]] = [cls]
        type_data = get_graphql_object_data(metadata, cls)

        for field in type_data.fields.values():
            field_type = get_graphql_type(field.field_type)
            if field_type and field_type not in types:
                types.append(field_type)

            if field.args:
                for field_arg in field.args.values():
                    field_arg_type = get_graphql_type(field_arg.field_type)
                    if field_arg_type and field_arg_type not in types:
                        types.append(field_arg_type)

        return types

    @staticmethod
    def field(
        f: Optional[Resolver] = None,
        *,
        name: Optional[str] = None,
        graphql_type: Optional[Any] = None,
        args: Optional[Dict[str, GraphQLObjectFieldArg]] = None,
        description: Optional[str] = None,
        default_value: Optional[Any] = None,
    ) -> Any:
        """Shortcut for object_field()"""
        return object_field(
            f,
            args=args,
            name=name,
            graphql_type=graphql_type,
            description=description,
            default_value=default_value,
        )

    @staticmethod
    def resolver(
        field: str,
        graphql_type: Optional[Any] = None,
        args: Optional[Dict[str, GraphQLObjectFieldArg]] = None,
        description: Optional[str] = None,
    ):
        """Shortcut for object_resolver()"""
        return object_resolver(
            args=args,
            field=field,
            graphql_type=graphql_type,
            description=description,
        )

    @staticmethod
    def argument(
        name: Optional[str] = None,
        description: Optional[str] = None,
        graphql_type: Optional[Any] = None,
        default_value: Optional[Any] = None,
    ) -> GraphQLObjectFieldArg:
        return GraphQLObjectFieldArg(
            name=name,
            out_name=None,
            field_type=graphql_type,
            description=description,
            default_value=default_value,
        )


def get_graphql_object_data(
    metadata: GraphQLMetadata, cls: Type[GraphQLObject]
) -> GraphQLObjectData:
    try:
        return metadata.get_data(cls)
    except KeyError as exc:
        if getattr(cls, "__schema__", None):
            raise NotImplementedError(
                "'get_graphql_object_data' is not supported for "
                "objects with '__schema__'."
            ) from exc
        object_data = create_graphql_object_data_without_schema(cls)

        metadata.set_data(cls, object_data)
        return object_data


def create_graphql_object_data_without_schema(
    cls: Type["GraphQLObject"],
) -> GraphQLObjectData:
    fields_types: Dict[str, str] = {}
    fields_names: Dict[str, str] = {}
    fields_descriptions: Dict[str, str] = {}
    fields_args: Dict[str, Dict[str, GraphQLObjectFieldArg]] = {}
    fields_resolvers: Dict[str, Resolver] = {}
    fields_subscribers: Dict[str, Subscriber] = {}
    fields_defaults: Dict[str, Any] = {}
    fields_order: List[str] = []

    type_hints = cls.__annotations__

    aliases: Dict[str, str] = getattr(cls, "__aliases__", None) or {}
    aliases_targets: List[str] = list(aliases.values())

    interfaces: List[str] = [
        interface.__name__ for interface in getattr(cls, "__implements__", [])
    ]

    for attr_name, attr_type in type_hints.items():
        if attr_name.startswith("__"):
            continue

        if attr_name in aliases_targets:
            # Alias target is not included in schema
            # unless its explicit field
            cls_attr = getattr(cls, attr_name, None)
            if not isinstance(cls_attr, GraphQLObjectField):
                continue

        fields_order.append(attr_name)

        fields_names[attr_name] = convert_python_name_to_graphql(attr_name)
        fields_types[attr_name] = attr_type

    for attr_name in dir(cls):
        if attr_name.startswith("__"):
            continue

        cls_attr = getattr(cls, attr_name)
        if isinstance(cls_attr, GraphQLObjectField):
            if attr_name not in fields_order:
                fields_order.append(attr_name)

            fields_names[attr_name] = cls_attr.name or convert_python_name_to_graphql(
                attr_name
            )

            if cls_attr.field_type:
                fields_types[attr_name] = cls_attr.field_type
            if cls_attr.description:
                fields_descriptions[attr_name] = cls_attr.description
            if cls_attr.resolver:
                fields_resolvers[attr_name] = cls_attr.resolver
                field_args = get_field_args_from_resolver(cls_attr.resolver)
                if field_args:
                    fields_args[attr_name] = update_field_args_options(
                        field_args, cls_attr.args
                    )
            if cls_attr.default_value:
                fields_defaults[attr_name] = cls_attr.default_value

        elif isinstance(cls_attr, GraphQLObjectResolver):
            if cls_attr.field_type and cls_attr.field not in fields_types:
                fields_types[cls_attr.field] = cls_attr.field_type
            if cls_attr.description:
                fields_descriptions[cls_attr.field] = cls_attr.description
            fields_resolvers[cls_attr.field] = cls_attr.resolver
            field_args = get_field_args_from_resolver(cls_attr.resolver)
            if field_args and not fields_args.get(cls_attr.field):
                fields_args[cls_attr.field] = update_field_args_options(
                    field_args, cls_attr.args
                )
        elif isinstance(cls_attr, GraphQLObjectSource):
            if cls_attr.field_type and cls_attr.field not in fields_types:
                fields_types[cls_attr.field] = cls_attr.field_type
            if cls_attr.description:
                fields_descriptions[cls_attr.field] = cls_attr.description
            fields_subscribers[cls_attr.field] = cls_attr.subscriber
            field_args = get_field_args_from_subscriber(cls_attr.subscriber)
            if field_args:
                fields_args[cls_attr.field] = update_field_args_options(
                    field_args, cls_attr.args
                )

        elif attr_name not in aliases_targets and not callable(cls_attr):
            fields_defaults[attr_name] = cls_attr

    fields: Dict[str, "GraphQLObjectField"] = {}
    for field_name in fields_order:
        fields[field_name] = GraphQLObjectField(
            name=fields_names[field_name],
            description=fields_descriptions.get(field_name),
            field_type=fields_types[field_name],
            args=fields_args.get(field_name),
            resolver=fields_resolvers.get(field_name),
            subscriber=fields_subscribers.get(field_name),
            default_value=fields_defaults.get(field_name),
        )

    return GraphQLObjectData(fields=fields, interfaces=interfaces)
