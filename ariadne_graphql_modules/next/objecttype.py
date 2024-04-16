from copy import deepcopy
from dataclasses import dataclass, replace
from enum import Enum
from inspect import signature
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Type,
    Union,
    cast,
)

from ariadne import ObjectType as ObjectTypeBindable
from ariadne.types import Resolver
from graphql import (
    FieldDefinitionNode,
    GraphQLField,
    GraphQLObjectType,
    GraphQLSchema,
    InputValueDefinitionNode,
    NameNode,
    NamedTypeNode,
    ObjectTypeDefinitionNode,
    TypeDefinitionNode,
)

from ..utils import parse_definition
from .base import GraphQLMetadata, GraphQLModel, GraphQLType
from .convert_name import convert_python_name_to_graphql
from .description import get_description_node
from .typing import get_graphql_type, get_type_node
from .validators import validate_description, validate_name
from .value import get_value_node


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
            return cls.__get_graphql_model_with_schema__(metadata, name)

        return cls.__get_graphql_model_without_schema__(metadata, name)

    @classmethod
    def __get_graphql_model_with_schema__(
        cls, metadata: GraphQLMetadata, name: str
    ) -> "GraphQLObjectModel":
        definition = cast(
            ObjectTypeDefinitionNode,
            parse_definition(ObjectTypeDefinitionNode, cls.__schema__),
        )

        descriptions: Dict[str, str] = {}
        args_descriptions: Dict[str, Dict[str, str]] = {}
        args_defaults: Dict[str, Dict[str, Any]] = {}
        resolvers: Dict[str, Resolver] = {}
        out_names: Dict[str, Dict[str, str]] = {}

        for attr_name in dir(cls):
            cls_attr = getattr(cls, attr_name)
            if isinstance(cls_attr, GraphQLObjectResolver):
                resolvers[cls_attr.field] = cls_attr.resolver
                if cls_attr.description:
                    descriptions[cls_attr.field] = get_description_node(
                        cls_attr.description
                    )

                field_args = get_field_args_from_resolver(cls_attr.resolver)
                if field_args:
                    args_descriptions[cls_attr.field] = {}
                    args_defaults[cls_attr.field] = {}

                    final_args = update_field_args_options(field_args, cls_attr.args)

                    for arg_name, arg_options in final_args.items():
                        arg_description = get_description_node(arg_options.description)
                        if arg_description:
                            args_descriptions[cls_attr.field][arg_name] = (
                                arg_description
                            )

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
    ) -> "GraphQLObjectModel":
        type_data = get_graphql_object_data(metadata, cls)
        type_aliases = getattr(cls, "__aliases__", None) or {}

        fields_ast: List[FieldDefinitionNode] = []
        resolvers: Dict[str, Resolver] = {}
        aliases: Dict[str, str] = {}
        out_names: Dict[str, Dict[str, str]] = {}

        for attr_name, field in type_data.fields.items():
            fields_ast.append(get_field_node_from_obj_field(cls, metadata, field))

            if attr_name in type_aliases:
                aliases[field.name] = type_aliases[attr_name]
            elif attr_name != field.name:
                aliases[field.name] = attr_name

            if field.resolver:
                resolvers[field.name] = field.resolver

            if field.args:
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
    ) -> Iterable["GraphQLType"]:
        """Returns iterable with GraphQL types associated with this type"""
        if getattr(cls, "__schema__", None):
            return cls.__get_graphql_types_with_schema__(metadata)

        return cls.__get_graphql_types_without_schema__(metadata)

    @classmethod
    def __get_graphql_types_with_schema__(
        cls, metadata: "GraphQLMetadata"
    ) -> Iterable["GraphQLType"]:
        types: List[GraphQLType] = [cls]
        types.extend(getattr(cls, "__requires__", []))
        types.extend(getattr(cls, "__implements__", []))
        return types

    @classmethod
    def __get_graphql_types_without_schema__(
        cls, metadata: "GraphQLMetadata"
    ) -> Iterable["GraphQLType"]:
        types: List[GraphQLType] = [cls]
        type_data = get_graphql_object_data(metadata, cls)

        for field in type_data.fields.values():
            field_type = get_graphql_type(field.type)
            if field_type and field_type not in types:
                types.append(field_type)

            if field.args:
                for field_arg in field.args.values():
                    field_arg_type = get_graphql_type(field_arg.type)
                    if field_arg_type and field_arg_type not in types:
                        types.append(field_arg_type)

        return types

    @staticmethod
    def field(
        f: Optional[Resolver] = None,
        *,
        name: Optional[str] = None,
        type: Optional[Any] = None,
        args: Optional[Dict[str, dict]] = None,
        description: Optional[str] = None,
        default_value: Optional[Any] = None,
    ):
        """Shortcut for object_field()"""
        return object_field(
            f,
            args=args,
            name=name,
            type=type,
            description=description,
            default_value=default_value,
        )

    @staticmethod
    def resolver(
        field: str,
        type: Optional[Any] = None,
        args: Optional[Dict[str, dict]] = None,
        description: Optional[str] = None,
    ):
        """Shortcut for object_resolver()"""
        return object_resolver(
            args=args,
            field=field,
            type=type,
            description=description,
        )

    @staticmethod
    def argument(
        name: Optional[str] = None,
        description: Optional[str] = None,
        type: Optional[Any] = None,
        default_value: Optional[Any] = None,
    ) -> dict:
        options: dict = {}
        if name:
            options["name"] = name
        if description:
            options["description"] = description
        if type:
            options["type"] = type
        if default_value:
            options["default_value"] = default_value
        return options


@dataclass(frozen=True)
class GraphQLObjectData:
    fields: Dict[str, "GraphQLObjectField"]
    interfaces: List[str]


def get_graphql_object_data(
    metadata: GraphQLMetadata, cls: Type[GraphQLObject]
) -> GraphQLObjectData:
    try:
        return metadata.get_data(cls)
    except KeyError:
        if getattr(cls, "__schema__", None):
            raise NotImplementedError(
                "'get_graphql_object_data' is not supported for "
                "objects with '__schema__'."
            )
        else:
            object_data = create_graphql_object_data_without_schema(cls)

        metadata.set_data(cls, object_data)
        return object_data


def create_graphql_object_data_without_schema(
    cls: Type[GraphQLObject],
) -> GraphQLObjectData:
    fields_types: Dict[str, str] = {}
    fields_names: Dict[str, str] = {}
    fields_descriptions: Dict[str, str] = {}
    fields_args: Dict[str, Dict[str, GraphQLObjectFieldArg]] = {}
    fields_resolvers: Dict[str, Resolver] = {}
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

            if cls_attr.type and attr_name not in fields_types:
                fields_types[attr_name] = cls_attr.type
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
            if cls_attr.type and cls_attr.field not in fields_types:
                fields_types[cls_attr.field] = cls_attr.type
            if cls_attr.description:
                fields_descriptions[cls_attr.field] = cls_attr.description
            if cls_attr.resolver:
                fields_resolvers[cls_attr.field] = cls_attr.resolver
                field_args = get_field_args_from_resolver(cls_attr.resolver)
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
            type=fields_types[field_name],
            args=fields_args.get(field_name),
            resolver=fields_resolvers.get(field_name),
            default_value=fields_defaults.get(field_name),
        )

    return GraphQLObjectData(fields=fields, interfaces=interfaces)


class GraphQLObjectField:
    name: Optional[str]
    description: Optional[str]
    type: Optional[Any]
    args: Optional[Dict[str, dict]]
    resolver: Optional[Resolver]
    default_value: Optional[Any]

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        type: Optional[Any] = None,
        args: Optional[Dict[str, dict]] = None,
        resolver: Optional[Resolver] = None,
        default_value: Optional[Any] = None,
    ):
        self.name = name
        self.description = description
        self.type = type
        self.args = args
        self.resolver = resolver
        self.default_value = default_value

    def __call__(self, resolver: Resolver):
        """Makes GraphQLObjectField instances work as decorators."""
        self.resolver = resolver
        if not self.type:
            self.type = get_field_type_from_resolver(resolver)
        return self


def object_field(
    resolver: Optional[Resolver] = None,
    *,
    args: Optional[Dict[str, dict]] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    type: Optional[Any] = None,
    default_value: Optional[Any] = None,
) -> GraphQLObjectField:
    field_type: Any = type
    if not type and resolver:
        field_type = get_field_type_from_resolver(resolver)

    return GraphQLObjectField(
        name=name,
        description=description,
        type=field_type,
        args=args,
        resolver=resolver,
        default_value=default_value,
    )


def get_field_type_from_resolver(resolver: Resolver) -> Any:
    return resolver.__annotations__.get("return")


@dataclass(frozen=True)
class GraphQLObjectResolver:
    resolver: Resolver
    field: str
    description: Optional[str] = None
    args: Optional[Dict[str, dict]] = None
    type: Optional[Any] = None


def object_resolver(
    field: str,
    type: Optional[Any] = None,
    args: Optional[Dict[str, dict]] = None,
    description: Optional[str] = None,
):
    def object_resolver_factory(f: Optional[Resolver]) -> GraphQLObjectResolver:
        return GraphQLObjectResolver(
            args=args,
            description=description,
            resolver=f,
            field=field,
            type=type or get_field_type_from_resolver(f),
        )

    return object_resolver_factory


@dataclass(frozen=True)
class GraphQLObjectModel(GraphQLModel):
    resolvers: Dict[str, Resolver]
    aliases: Dict[str, str]
    out_names: Dict[str, Dict[str, str]]

    def bind_to_schema(self, schema: GraphQLSchema):
        bindable = ObjectTypeBindable(self.name)

        for field, resolver in self.resolvers.items():
            bindable.set_field(field, resolver)
        for alias, target in self.aliases.items():
            bindable.set_alias(alias, target)

        bindable.bind_to_schema(schema)

        graphql_type = cast(GraphQLObjectType, schema.get_type(self.name))
        for field_name, field_out_names in self.out_names.items():
            graphql_field = cast(GraphQLField, graphql_type.fields[field_name])
            for arg_name, out_name in field_out_names.items():
                graphql_field.args[arg_name].out_name = out_name


def get_field_node_from_obj_field(
    parent_type: GraphQLObject,
    metadata: GraphQLMetadata,
    field: GraphQLObjectField,
) -> FieldDefinitionNode:
    return FieldDefinitionNode(
        description=get_description_node(field.description),
        name=NameNode(value=field.name),
        type=get_type_node(metadata, field.type, parent_type),
        arguments=get_field_args_nodes_from_obj_field_args(metadata, field.args),
    )


@dataclass(frozen=True)
class GraphQLObjectFieldArg:
    name: Optional[str]
    out_name: Optional[str]
    type: Optional[Any]
    description: Optional[str] = None
    default_value: Optional[Any] = None


def get_field_args_from_resolver(
    resolver: Resolver,
) -> Dict[str, GraphQLObjectFieldArg]:
    resolver_signature = signature(resolver)
    type_hints = resolver.__annotations__
    type_hints.pop("return", None)

    field_args: Dict[str, GraphQLObjectFieldArg] = {}
    field_args_start = 0

    # Fist pass: (arg, *_, something, something) or (arg, *, something, something):
    for i, param in enumerate(resolver_signature.parameters.values()):
        param_repr = str(param)
        if param_repr.startswith("*") and not param_repr.startswith("**"):
            field_args_start = i + 1
            break
    else:
        if len(resolver_signature.parameters) < 2:
            raise TypeError(
                f"Resolver function '{resolver_signature}' should accept at least "
                "'obj' and 'info' positional arguments."
            )

        field_args_start = 2

    args_parameters = tuple(resolver_signature.parameters.items())[field_args_start:]
    if not args_parameters:
        return field_args

    for param_name, param in args_parameters:
        if param.default != param.empty:
            param_default = param.default
        else:
            param_default = None

        field_args[param_name] = GraphQLObjectFieldArg(
            name=convert_python_name_to_graphql(param_name),
            out_name=param_name,
            type=type_hints.get(param_name),
            default_value=param_default,
        )

    return field_args


def get_field_args_out_names(
    field_args: Dict[str, GraphQLObjectFieldArg],
) -> Dict[str, str]:
    out_names: Dict[str, str] = {}
    for field_arg in field_args.values():
        out_names[field_arg.name] = field_arg.out_name
    return out_names


def get_field_args_nodes_from_obj_field_args(
    metadata: GraphQLMetadata, field_args: Optional[Dict[str, GraphQLObjectFieldArg]]
) -> Optional[Tuple[InputValueDefinitionNode]]:
    if not field_args:
        return None

    return tuple(
        get_field_arg_node_from_obj_field_arg(metadata, field_arg)
        for field_arg in field_args.values()
    )


def get_field_arg_node_from_obj_field_arg(
    metadata: GraphQLMetadata,
    field_arg: GraphQLObjectFieldArg,
) -> InputValueDefinitionNode:
    if field_arg.default_value is not None:
        default_value = get_value_node(field_arg.default_value)
    else:
        default_value = None

    return InputValueDefinitionNode(
        description=get_description_node(field_arg.description),
        name=NameNode(value=field_arg.name),
        type=get_type_node(metadata, field_arg.type),
        default_value=default_value,
    )


def update_field_args_options(
    field_args: Dict[str, GraphQLObjectFieldArg],
    args_options: Optional[Dict[str, dict]],
) -> Dict[str, GraphQLObjectFieldArg]:
    if not args_options:
        return field_args

    updated_args: Dict[str, GraphQLObjectFieldArg] = {}
    for arg_name in field_args:
        arg_options = args_options.get(arg_name)
        if not arg_options:
            updated_args[arg_name] = field_args[arg_name]
            continue

        args_update = {}
        if arg_options.get("name"):
            args_update["name"] = arg_options["name"]
        if arg_options.get("description"):
            args_update["description"] = arg_options["description"]
        if arg_options.get("default_value") is not None:
            args_update["default_value"] = arg_options["default_value"]
        if arg_options.get("type"):
            args_update["type"] = arg_options["type"]

        if args_update:
            updated_args[arg_name] = replace(field_args[arg_name], **args_update)
        else:
            updated_args[arg_name] = field_args[arg_name]

    return updated_args


def validate_object_type_with_schema(
    cls: Type[GraphQLObject],
    valid_type: Type[TypeDefinitionNode] = ObjectTypeDefinitionNode,
) -> Dict[str, Any]:
    definition = parse_definition(valid_type, cls.__schema__)

    if not isinstance(definition, valid_type):
        raise ValueError(
            f"Class '{cls.__name__}' defines '__schema__' attribute "
            "with declaration for an invalid GraphQL type. "
            f"('{definition.__class__.__name__}' != "
            f"'{valid_type.__name__}')"
        )

    validate_name(cls, definition)
    validate_description(cls, definition)

    if not definition.fields:
        raise ValueError(
            f"Class '{cls.__name__}' defines '__schema__' attribute "
            "with declaration for an object type without any fields. "
        )

    field_names: List[str] = [f.name.value for f in definition.fields]
    field_definitions: Dict[str, FieldDefinitionNode] = {
        f.name.value: f for f in definition.fields
    }

    fields_resolvers: List[str] = []

    for attr_name in dir(cls):
        cls_attr = getattr(cls, attr_name)
        if isinstance(cls_attr, GraphQLObjectField):
            raise ValueError(
                f"Class '{cls.__name__}' defines 'GraphQLObjectField' instance. "
                "This is not supported for types defining '__schema__'."
            )

        if isinstance(cls_attr, GraphQLObjectResolver):
            if cls_attr.field not in field_names:
                valid_fields: str = "', '".join(sorted(field_names))
                raise ValueError(
                    f"Class '{cls.__name__}' defines resolver for an undefined "
                    f"field '{cls_attr.field}'. (Valid fields: '{valid_fields}')"
                )

            if cls_attr.field in fields_resolvers:
                raise ValueError(
                    f"Class '{cls.__name__}' defines multiple resolvers for field "
                    f"'{cls_attr.field}'."
                )

            fields_resolvers.append(cls_attr.field)

            if cls_attr.description and field_definitions[cls_attr.field].description:
                raise ValueError(
                    f"Class '{cls.__name__}' defines multiple descriptions "
                    f"for field '{cls_attr.field}'."
                )

            if cls_attr.args:
                field_args = {
                    arg.name.value: arg
                    for arg in field_definitions[cls_attr.field].arguments
                }

                for arg_name, arg_options in cls_attr.args.items():
                    if arg_name not in field_args:
                        raise ValueError(
                            f"Class '{cls.__name__}' defines options for '{arg_name}' "
                            f"argument of the '{cls_attr.field}' field "
                            "that doesn't exist."
                        )

                    if arg_options.get("name"):
                        raise ValueError(
                            f"Class '{cls.__name__}' defines 'name' option for "
                            f"'{arg_name}' argument of the '{cls_attr.field}' field. "
                            "This is not supported for types defining '__schema__'."
                        )

                    if arg_options.get("type"):
                        raise ValueError(
                            f"Class '{cls.__name__}' defines 'type' option for "
                            f"'{arg_name}' argument of the '{cls_attr.field}' field. "
                            "This is not supported for types defining '__schema__'."
                        )

                    if (
                        arg_options.get("description")
                        and field_args[arg_name].description
                    ):
                        raise ValueError(
                            f"Class '{cls.__name__}' defines duplicate descriptions "
                            f"for '{arg_name}' argument "
                            f"of the '{cls_attr.field}' field."
                        )

                    validate_field_arg_default_value(
                        cls, cls_attr.field, arg_name, arg_options.get("default_value")
                    )

            resolver_args = get_field_args_from_resolver(cls_attr.resolver)
            for arg_name, arg_obj in resolver_args.items():
                validate_field_arg_default_value(
                    cls, cls_attr.field, arg_name, arg_obj.default_value
                )

    aliases: Dict[str, str] = getattr(cls, "__aliases__", None) or {}
    validate_object_aliases(cls, aliases, field_names, fields_resolvers)

    return get_object_type_with_schema_kwargs(cls, aliases, field_names)


def validate_field_arg_default_value(
    cls: Type[GraphQLObject], field_name: str, arg_name: str, default_value: Any
):
    if default_value is None:
        return

    try:
        get_value_node(default_value)
    except TypeError as e:
        raise TypeError(
            f"Class '{cls.__name__}' defines default value "
            f"for '{arg_name}' argument "
            f"of the '{field_name}' field that can't be "
            "represented in GraphQL schema."
        ) from e


def validate_object_type_without_schema(cls: Type[GraphQLObject]) -> Dict[str, Any]:
    data = get_object_type_validation_data(cls)

    # Alias target is not present in schema as a field if its not an
    # explicit field (instance of GraphQLObjectField)
    for alias_target in data.aliases.values():
        if (
            alias_target in data.fields_attrs
            and alias_target not in data.fields_instances
        ):
            data.fields_attrs.remove(alias_target)

    # Validate GraphQL names for future type's fields and assert those are unique
    validate_object_unique_graphql_names(cls, data.fields_attrs, data.fields_instances)
    validate_object_resolvers(
        cls, data.fields_attrs, data.fields_instances, data.resolvers_instances
    )
    validate_object_fields_args(cls)

    # Gather names of field attrs with defined resolver
    fields_resolvers: List[str] = []
    for attr_name, field_instance in data.fields_instances.items():
        if field_instance.resolver:
            fields_resolvers.append(attr_name)
    for resolver_instance in data.resolvers_instances.values():
        fields_resolvers.append(resolver_instance.field)

    validate_object_aliases(cls, data.aliases, data.fields_attrs, fields_resolvers)

    return get_object_type_kwargs(cls, data.aliases)


def validate_object_unique_graphql_names(
    cls: Type[GraphQLObject],
    fields_attrs: List[str],
    fields_instances: Dict[str, GraphQLObjectField],
):
    graphql_names: List[str] = []
    for attr_name in fields_attrs:
        if attr_name in fields_instances and fields_instances[attr_name].name:
            attr_graphql_name = fields_instances[attr_name].name
        else:
            attr_graphql_name = convert_python_name_to_graphql(attr_name)

        if attr_graphql_name in graphql_names:
            raise ValueError(
                f"Class '{cls.__name__}' defines multiple fields with GraphQL "
                f"name '{attr_graphql_name}'."
            )

        graphql_names.append(attr_graphql_name)


def validate_object_resolvers(
    cls: Type[GraphQLObject],
    fields_names: List[str],
    fields_instances: Dict[str, GraphQLObjectField],
    resolvers_instances: Dict[str, GraphQLObjectResolver],
):
    resolvers_fields: List[str] = []

    for field_attr, field_instance in fields_instances.items():
        if field_instance.resolver:
            resolvers_fields.append(field_attr)

    for resolver in resolvers_instances.values():
        if resolver.field not in fields_names:
            valid_fields: str = "', '".join(sorted(fields_names))
            raise ValueError(
                f"Class '{cls.__name__}' defines resolver for an undefined "
                f"field '{resolver.field}'. (Valid fields: '{valid_fields}')"
            )

        if resolver.field in resolvers_fields:
            raise ValueError(
                f"Class '{cls.__name__}' defines multiple resolvers for field "
                f"'{resolver.field}'."
            )

        resolvers_fields.append(resolver.field)

        field_instance = fields_instances.get(resolver.field)
        if field_instance:
            if field_instance.description and resolver.description:
                raise ValueError(
                    f"Class '{cls.__name__}' defines multiple descriptions "
                    f"for field '{resolver.field}'."
                )

            if field_instance.args and resolver.args:
                raise ValueError(
                    f"Class '{cls.__name__}' defines multiple arguments options "
                    f"('args') for field '{resolver.field}'."
                )


def validate_object_fields_args(cls: Type[GraphQLObject]):
    for field_name in dir(cls):
        field_instance = getattr(cls, field_name)
        if (
            isinstance(field_instance, (GraphQLObjectField, GraphQLObjectResolver))
            and field_instance.resolver
        ):
            validate_object_field_args(cls, field_name, field_instance)


def validate_object_field_args(
    cls: Type[GraphQLObject],
    field_name: str,
    field_instance: Union["GraphQLObjectField", "GraphQLObjectResolver"],
):
    resolver_args = get_field_args_from_resolver(field_instance.resolver)
    if resolver_args:
        for arg_name, arg_obj in resolver_args.items():
            validate_field_arg_default_value(
                cls, field_name, arg_name, arg_obj.default_value
            )

    if not field_instance.args:
        return  # Skip extra logic for validating instance.args

    resolver_args_names = list(resolver_args.keys())
    if resolver_args_names:
        error_help = "expected one of: '%s'" % ("', '".join(resolver_args_names))
    else:
        error_help = "function accepts no extra arguments"

    for arg_name, arg_options in field_instance.args.items():
        if arg_name not in resolver_args_names:
            if isinstance(field_instance, GraphQLObjectField):
                raise ValueError(
                    f"Class '{cls.__name__}' defines '{field_name}' field "
                    f"with extra configuration for '{arg_name}' argument "
                    "thats not defined on the resolver function. "
                    f"({error_help})"
                )

            raise ValueError(
                f"Class '{cls.__name__}' defines '{field_name}' resolver "
                f"with extra configuration for '{arg_name}' argument "
                "thats not defined on the resolver function. "
                f"({error_help})"
            )

        validate_field_arg_default_value(
            cls, field_name, arg_name, arg_options.get("default_value")
        )


def validate_object_aliases(
    cls: Type[GraphQLObject],
    aliases: Dict[str, str],
    fields_names: List[str],
    fields_resolvers: List[str],
):
    for alias in aliases:
        if alias not in fields_names:
            valid_fields: str = "', '".join(sorted(fields_names))
            raise ValueError(
                f"Class '{cls.__name__}' defines an alias for an undefined "
                f"field '{alias}'. (Valid fields: '{valid_fields}')"
            )

        if alias in fields_resolvers:
            raise ValueError(
                f"Class '{cls.__name__}' defines an alias for a field "
                f"'{alias}' that already has a custom resolver."
            )


@dataclass
class GraphQLObjectValidationData:
    aliases: Dict[str, str]
    fields_attrs: List[str]
    fields_instances: Dict[str, GraphQLObjectField]
    resolvers_instances: Dict[str, GraphQLObjectResolver]


def get_object_type_validation_data(
    cls: Type[GraphQLObject],
) -> GraphQLObjectValidationData:
    fields_attrs: List[str] = [
        attr_name for attr_name in cls.__annotations__ if not attr_name.startswith("__")
    ]

    fields_instances: Dict[str, GraphQLObjectField] = {}
    resolvers_instances: Dict[str, GraphQLObjectResolver] = {}

    for attr_name in dir(cls):
        if attr_name.startswith("__"):
            continue

        cls_attr = getattr(cls, attr_name)
        if isinstance(cls_attr, GraphQLObjectResolver):
            resolvers_instances[attr_name] = cls_attr
            if attr_name in fields_attrs:
                fields_attrs.remove(attr_name)

        elif isinstance(cls_attr, GraphQLObjectField):
            fields_instances[attr_name] = cls_attr

            if attr_name not in fields_attrs:
                fields_attrs.append(attr_name)

        elif callable(attr_name):
            if attr_name in fields_attrs:
                fields_attrs.remove(attr_name)

    return GraphQLObjectValidationData(
        aliases=getattr(cls, "__aliases__", None) or {},
        fields_attrs=fields_attrs,
        fields_instances=fields_instances,
        resolvers_instances=resolvers_instances,
    )


def get_object_type_kwargs(
    cls: Type[GraphQLObject],
    aliases: Dict[str, str],
) -> Dict[str, Any]:
    kwargs: Dict[str, Any] = {}

    for attr_name in cls.__annotations__:
        if attr_name.startswith("__"):
            continue

        kwarg_name = aliases.get(attr_name, attr_name)
        kwarg_value = getattr(cls, kwarg_name, None)
        if isinstance(kwarg_value, GraphQLObjectField):
            kwargs[kwarg_name] = kwarg_value.default_value
        elif isinstance(kwarg_value, GraphQLObjectResolver):
            continue  # Skip resolver instances
        elif not callable(kwarg_value):
            kwargs[kwarg_name] = kwarg_value

    for attr_name in dir(cls):
        if attr_name.startswith("__") or attr_name in kwargs:
            continue

        kwarg_name = aliases.get(attr_name, attr_name)
        kwarg_value = getattr(cls, kwarg_name)
        if isinstance(kwarg_value, GraphQLObjectField):
            kwargs[kwarg_name] = kwarg_value.default_value
        elif not callable(kwarg_value):
            kwargs[kwarg_name] = kwarg_value

    return kwargs


def get_object_type_with_schema_kwargs(
    cls: Type[GraphQLObject],
    aliases: Dict[str, str],
    field_names: List[str],
) -> Dict[str, Any]:
    kwargs: Dict[str, Any] = {}

    for field_name in field_names:
        final_name = aliases.get(field_name, field_name)
        attr_value = getattr(cls, final_name, None)

        if isinstance(attr_value, GraphQLObjectField):
            kwargs[final_name] = attr_value.default_value
        elif not isinstance(attr_value, GraphQLObjectResolver) and not callable(
            attr_value
        ):
            kwargs[final_name] = attr_value

    return kwargs
