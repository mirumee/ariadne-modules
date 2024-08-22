from typing import Any, Dict, List, Optional, cast

from graphql import (
    FieldDefinitionNode,
    InputValueDefinitionNode,
    NameNode,
    NamedTypeNode,
    ObjectTypeDefinitionNode,
    StringValueNode,
)

from ariadne.types import Resolver, Subscriber

from ..base_object_type import (
    GraphQLFieldData,
    GraphQLObjectData,
    validate_object_type_with_schema,
    validate_object_type_without_schema,
)

from ..types import GraphQLClassType

from ..base_object_type import GraphQLBaseObject


from ..utils import parse_definition
from ..base import GraphQLMetadata, GraphQLModel
from ..description import get_description_node
from ..object_type import (
    GraphQLObjectResolver,
    GraphQLObjectSource,
    GraphQLObjectFieldArg,
    get_field_args_from_resolver,
    get_field_args_from_subscriber,
    get_field_args_out_names,
    get_field_node_from_obj_field,
    object_subscriber,
    update_field_args_options,
)
from ..value import get_value_node
from .models import GraphQLSubscriptionModel


class GraphQLSubscription(GraphQLBaseObject):
    __valid_type__ = ObjectTypeDefinitionNode
    __graphql_type__ = GraphQLClassType.SUBSCRIPTION
    __abstract__: bool = True
    __description__: Optional[str] = None

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
    def __get_graphql_model_with_schema__(cls) -> "GraphQLModel":
        definition = cast(
            ObjectTypeDefinitionNode,
            parse_definition(ObjectTypeDefinitionNode, cls.__schema__),
        )

        descriptions: Dict[str, StringValueNode] = {}
        args_descriptions: Dict[str, Dict[str, StringValueNode]] = {}
        args_defaults: Dict[str, Dict[str, Any]] = {}
        resolvers: Dict[str, Resolver] = {}
        subscribers: Dict[str, Subscriber] = {}

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
            if isinstance(cls_attr, GraphQLObjectSource):
                subscribers[cls_attr.field] = cls_attr.subscriber
                description_node = get_description_node(cls_attr.description)
                if description_node:
                    descriptions[cls_attr.field] = description_node

                field_args = get_field_args_from_subscriber(cls_attr.subscriber)
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

        return GraphQLSubscriptionModel(
            name=definition.name.value,
            ast_type=ObjectTypeDefinitionNode,
            ast=ObjectTypeDefinitionNode(
                name=NameNode(value=definition.name.value),
                fields=tuple(fields),
                interfaces=definition.interfaces,
            ),
            resolvers=resolvers,
            subscribers=subscribers,
            aliases=getattr(cls, "__aliases__", {}),
            out_names={},
        )

    @classmethod
    def __get_graphql_model_without_schema__(
        cls, metadata: GraphQLMetadata, name: str
    ) -> "GraphQLModel":
        type_data = cls.get_graphql_object_data(metadata)
        type_aliases = getattr(cls, "__aliases__", None) or {}

        fields_ast: List[FieldDefinitionNode] = []
        resolvers: Dict[str, Resolver] = {}
        subscribers: Dict[str, Subscriber] = {}
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

            if field.subscriber and field.name:
                subscribers[field.name] = field.subscriber

            if field.args and field.name:
                out_names[field.name] = get_field_args_out_names(field.args)

        interfaces_ast: List[NamedTypeNode] = []
        for interface_name in type_data.interfaces:
            interfaces_ast.append(NamedTypeNode(name=NameNode(value=interface_name)))

        return GraphQLSubscriptionModel(
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
            subscribers=subscribers,
        )

    @staticmethod
    def source(
        field: str,
        graphql_type: Optional[Any] = None,
        args: Optional[Dict[str, GraphQLObjectFieldArg]] = None,
        description: Optional[str] = None,
    ):
        """Shortcut for object_resolver()"""
        return object_subscriber(
            args=args,
            field=field,
            graphql_type=graphql_type,
            description=description,
        )

    @classmethod
    def _collect_inherited_objects(cls):
        return [
            inherited_obj
            for inherited_obj in cls.__mro__[1:]
            if getattr(inherited_obj, "__graphql_type__", None)
            == GraphQLClassType.SUBSCRIPTION
            and not getattr(inherited_obj, "__abstract__", True)
        ]

    @classmethod
    def create_graphql_object_data_without_schema(cls) -> GraphQLObjectData:
        fields_data = GraphQLFieldData()
        inherited_objects = list(reversed(cls._collect_inherited_objects()))

        for inherited_obj in inherited_objects:
            fields_data.type_hints.update(inherited_obj.__annotations__)
            fields_data.aliases.update(getattr(inherited_obj, "__aliases__", {}))

        cls._process_type_hints_and_aliases(fields_data)

        for inherited_obj in inherited_objects:
            cls._process_class_attributes(inherited_obj, fields_data)
        cls._process_class_attributes(cls, fields_data)

        return GraphQLObjectData(
            fields=cls._build_fields(fields_data=fields_data),
            interfaces=[],
        )
