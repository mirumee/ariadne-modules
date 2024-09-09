from collections.abc import Iterable
from copy import deepcopy
from enum import Enum
from typing import (
    Any,
    Optional,
    Union,
)

from ariadne.types import Resolver
from graphql import (
    FieldDefinitionNode,
    InputValueDefinitionNode,
    StringValueNode,
)

from ariadne_graphql_modules.base import GraphQLMetadata, GraphQLType
from ariadne_graphql_modules.base_graphql_model import GraphQLModel
from ariadne_graphql_modules.base_object_type.graphql_field import (
    GraphQLClassData,
    GraphQLFieldData,
    GraphQLObjectData,
    GraphQLObjectField,
    GraphQLObjectFieldArg,
    GraphQLObjectResolver,
    GraphQLObjectSource,
    object_field,
    object_resolver,
)
from ariadne_graphql_modules.base_object_type.utils import (
    get_field_args_from_resolver,
    get_field_args_from_subscriber,
    get_field_args_out_names,
    get_field_node_from_obj_field,
    update_field_args_options,
)
from ariadne_graphql_modules.convert_name import convert_python_name_to_graphql
from ariadne_graphql_modules.description import get_description_node
from ariadne_graphql_modules.types import GraphQLClassType
from ariadne_graphql_modules.typing import get_graphql_type
from ariadne_graphql_modules.value import get_value_node


class GraphQLBaseObject(GraphQLType):
    __kwargs__: dict[str, Any]
    __abstract__: bool = True
    __schema__: Optional[str] = None
    __aliases__: Optional[dict[str, str]]
    __requires__: Optional[Iterable[Union[type[GraphQLType], type[Enum]]]]
    __graphql_type__ = GraphQLClassType.BASE

    def __init__(self, **kwargs: Any):
        default_values: dict[str, Any] = {}

        for inherited_obj in self._collect_inherited_objects():
            if hasattr(inherited_obj, "__kwargs__"):
                default_values.update(inherited_obj.__kwargs__)

        default_values.update(self.__kwargs__)

        for kwarg in kwargs:
            if kwarg not in default_values:
                valid_kwargs = "', '".join(default_values)
                raise TypeError(
                    f"{type(self).__name__}.__init__() got an unexpected "
                    f"keyword argument '{kwarg}'. "
                    f"Valid keyword arguments: '{valid_kwargs}'"
                )

        for kwarg, default in default_values.items():
            setattr(self, kwarg, kwargs.get(kwarg, deepcopy(default)))

    @classmethod
    def __get_graphql_model__(cls, metadata: GraphQLMetadata) -> "GraphQLModel":
        name = cls.__get_graphql_name__()
        metadata.set_graphql_name(cls, name)

        if getattr(cls, "__schema__", None):
            return cls.__get_graphql_model_with_schema__()

        return cls.__get_graphql_model_without_schema__(metadata, name)

    @classmethod
    def __get_graphql_model_with_schema__(cls) -> "GraphQLModel":
        raise NotImplementedError()

    @classmethod
    def __get_graphql_model_without_schema__(
        cls, metadata: GraphQLMetadata, name: str
    ) -> "GraphQLModel":
        raise NotImplementedError()

    @classmethod
    def _create_fields_and_resolvers_with_schema(
        cls, definition_fields: tuple["FieldDefinitionNode", ...]
    ) -> tuple[tuple[FieldDefinitionNode, ...], dict[str, Resolver]]:
        descriptions: dict[str, StringValueNode] = {}
        args_descriptions: dict[str, dict[str, StringValueNode]] = {}
        args_defaults: dict[str, dict[str, Any]] = {}
        resolvers: dict[str, Resolver] = {}

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

                        if arg_options.default_value is not None:
                            args_defaults[cls_attr.field][arg_name] = get_value_node(
                                arg_options.default_value
                            )

        fields: list[FieldDefinitionNode] = []
        for field in definition_fields:
            field_args_descriptions = args_descriptions.get(field.name.value, {})
            field_args_defaults = args_defaults.get(field.name.value, {})

            args: list[InputValueDefinitionNode] = []
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

        return tuple(fields), resolvers

    @classmethod
    def _process_graphql_fields(
        cls,
        metadata: GraphQLMetadata,
        type_data,
        type_aliases,
        object_model_data: GraphQLClassData,
    ):
        for attr_name, field in type_data.fields.items():
            object_model_data.fields_ast[attr_name] = get_field_node_from_obj_field(
                cls, metadata, field
            )

            if attr_name in type_aliases and field.name:
                object_model_data.aliases[field.name] = type_aliases[attr_name]
            elif field.name and attr_name != field.name and not field.resolver:
                object_model_data.aliases[field.name] = attr_name

            if field.resolver and field.name:
                object_model_data.resolvers[field.name] = field.resolver

            if field.args and field.name:
                object_model_data.out_names[field.name] = get_field_args_out_names(
                    field.args
                )

    @classmethod
    def __get_graphql_types__(
        cls, metadata: "GraphQLMetadata"
    ) -> Iterable[Union[type["GraphQLType"], type[Enum]]]:
        """Returns iterable with GraphQL types associated with this type"""
        if getattr(cls, "__schema__", None):
            return cls.__get_graphql_types_with_schema__(metadata)

        return cls.__get_graphql_types_without_schema__(metadata)

    @classmethod
    def __get_graphql_types_with_schema__(
        cls, _: "GraphQLMetadata"
    ) -> Iterable[type["GraphQLType"]]:
        types: list[type[GraphQLType]] = [cls]
        types.extend(getattr(cls, "__requires__", []))
        return types

    @classmethod
    def __get_graphql_types_without_schema__(
        cls, metadata: "GraphQLMetadata"
    ) -> Iterable[Union[type["GraphQLType"], type[Enum]]]:
        types: list[Union[type[GraphQLType], type[Enum]]] = [cls]
        type_data = cls.get_graphql_object_data(metadata)

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
        args: Optional[dict[str, GraphQLObjectFieldArg]] = None,
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
        args: Optional[dict[str, GraphQLObjectFieldArg]] = None,
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

    @classmethod
    def get_graphql_object_data(
        cls,
        metadata: GraphQLMetadata,
    ) -> GraphQLObjectData:
        try:
            return metadata.get_data(cls)
        except KeyError as exc:
            if getattr(cls, "__schema__", None):
                raise NotImplementedError(
                    "'get_graphql_object_data' is not supported for "
                    "objects with '__schema__'."
                ) from exc
            object_data = cls.create_graphql_object_data_without_schema()

            metadata.set_data(cls, object_data)
            return object_data

    @classmethod
    def create_graphql_object_data_without_schema(cls) -> GraphQLObjectData:
        raise NotImplementedError()

    @staticmethod
    def _build_fields(fields_data: GraphQLFieldData) -> dict[str, "GraphQLObjectField"]:
        fields = {}
        for field_name in fields_data.fields_order:
            fields[field_name] = GraphQLObjectField(
                name=fields_data.fields_names[field_name],
                description=fields_data.fields_descriptions.get(field_name),
                field_type=fields_data.fields_types.get(field_name),
                args=fields_data.fields_args.get(field_name),
                resolver=fields_data.fields_resolvers.get(field_name),
                subscriber=fields_data.fields_subscribers.get(field_name),
                default_value=fields_data.fields_defaults.get(field_name),
            )
        return fields

    @classmethod
    def _process_type_hints_and_aliases(cls, fields_data: GraphQLFieldData):
        fields_data.type_hints.update(cls.__annotations__)  # pylint: disable=no-member
        fields_data.aliases.update(getattr(cls, "__aliases__", None) or {})
        fields_data.aliases_targets = list(fields_data.aliases.values())

        for attr_name, attr_type in fields_data.type_hints.items():
            if attr_name.startswith("__"):
                continue

            if attr_name in fields_data.aliases_targets:
                cls_attr = getattr(cls, attr_name, None)
                if not isinstance(cls_attr, GraphQLObjectField):
                    continue

            fields_data.fields_order.append(attr_name)
            fields_data.fields_names[attr_name] = convert_python_name_to_graphql(
                attr_name
            )
            fields_data.fields_types[attr_name] = attr_type

    @staticmethod
    def _process_class_attributes(  # noqa: C901
        target_cls, fields_data: GraphQLFieldData
    ):
        for attr_name in dir(target_cls):
            if attr_name.startswith("__"):
                continue
            cls_attr = getattr(target_cls, attr_name)
            if isinstance(cls_attr, GraphQLObjectField):
                if attr_name not in fields_data.fields_order:
                    fields_data.fields_order.append(attr_name)

                fields_data.fields_names[attr_name] = (
                    cls_attr.name or convert_python_name_to_graphql(attr_name)
                )

                if cls_attr.field_type:
                    fields_data.fields_types[attr_name] = cls_attr.field_type
                if cls_attr.description:
                    fields_data.fields_descriptions[attr_name] = cls_attr.description
                if cls_attr.resolver:
                    resolver = cls_attr.resolver
                    if isinstance(resolver, staticmethod):
                        resolver = resolver.__func__  # type: ignore[attr-defined]
                    fields_data.fields_resolvers[attr_name] = resolver
                    field_args = get_field_args_from_resolver(resolver)
                    if field_args:
                        fields_data.fields_args[attr_name] = update_field_args_options(
                            field_args, cls_attr.args
                        )
                if cls_attr.default_value:
                    fields_data.fields_defaults[attr_name] = cls_attr.default_value
            elif isinstance(cls_attr, GraphQLObjectResolver):
                if (
                    cls_attr.field_type
                    and cls_attr.field not in fields_data.fields_types
                ):
                    fields_data.fields_types[cls_attr.field] = cls_attr.field_type
                if (
                    cls_attr.description
                    and cls_attr.field not in fields_data.fields_descriptions
                ):
                    fields_data.fields_descriptions[cls_attr.field] = (
                        cls_attr.description
                    )
                resolver = cls_attr.resolver
                if isinstance(resolver, staticmethod):
                    resolver = resolver.__func__  # type: ignore[attr-defined]
                fields_data.fields_resolvers[cls_attr.field] = resolver
                field_args = get_field_args_from_resolver(resolver)
                if field_args and not fields_data.fields_args.get(cls_attr.field):
                    fields_data.fields_args[cls_attr.field] = update_field_args_options(
                        field_args, cls_attr.args
                    )
            elif isinstance(cls_attr, GraphQLObjectSource):
                if (
                    cls_attr.field_type
                    and cls_attr.field not in fields_data.fields_types
                ):
                    fields_data.fields_types[cls_attr.field] = cls_attr.field_type
                if (
                    cls_attr.description
                    and cls_attr.field not in fields_data.fields_descriptions
                ):
                    fields_data.fields_descriptions[cls_attr.field] = (
                        cls_attr.description
                    )
                subscriber = cls_attr.subscriber
                if isinstance(subscriber, staticmethod):
                    subscriber = subscriber.__func__  # type: ignore[attr-defined]
                fields_data.fields_subscribers[cls_attr.field] = subscriber
                field_args = get_field_args_from_subscriber(subscriber)
                if field_args:
                    fields_data.fields_args[cls_attr.field] = update_field_args_options(
                        field_args, cls_attr.args
                    )

            elif attr_name not in fields_data.aliases_targets and not callable(
                cls_attr
            ):
                fields_data.fields_defaults[attr_name] = cls_attr

    @classmethod
    def _collect_inherited_objects(cls):
        raise NotImplementedError
