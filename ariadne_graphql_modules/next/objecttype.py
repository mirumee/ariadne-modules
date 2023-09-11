from inspect import signature
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Type,
    cast,
    get_type_hints,
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
    ObjectTypeDefinitionNode,
    StringValueNode,
)

from ..utils import parse_definition
from .base import GraphQLModel, GraphQLType
from .convert_name import convert_python_name_to_graphql
from .typing import get_graphql_type, get_type_node
from .validators import validate_description


class GraphQLObject(GraphQLType):
    __abstract__: bool = True
    __schema__: Optional[str]
    __description__: Optional[str]
    __aliases__: Optional[Dict[str, str]]

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        if cls.__dict__.get("__abstract__"):
            return

        cls.__abstract__ = False

        if cls.__dict__.get("__schema__"):
            validate_object_type_with_schema(cls)
        else:
            validate_object_type(cls)

    @classmethod
    def __get_graphql_model__(cls) -> "GraphQLModel":
        name = cls.__get_graphql_name__()

        if getattr(cls, "__schema__", None):
            return cls.__get_graphql_model_with_schema__(name)

        return cls.__get_graphql_model_without_schema__(name)

    @classmethod
    def __get_graphql_model_with_schema__(cls, name: str) -> "GraphQLModel":
        definition = cast(
            ObjectTypeDefinitionNode,
            parse_definition(ObjectTypeDefinitionNode, cls.__schema__),
        )

        resolvers: Dict[str, Resolver] = {}
        out_names: Dict[str, Dict[str, str]] = {}

        for attr_name in dir(cls):
            cls_attr = getattr(cls, attr_name)
            if isinstance(cls_attr, GraphQLObjectResolver):
                resolvers[cls_attr.field] = cls_attr.resolver

        return GraphQLObjectModel(
            name=definition.name.value,
            ast=ObjectTypeDefinitionNode(
                name=NameNode(value=definition.name.value),
                fields=definition.fields,
            ),
            resolvers=resolvers,
            aliases=getattr(cls, "__aliases__", {}),
            out_names=out_names,
        )

    @classmethod
    def __get_graphql_model_without_schema__(cls, name: str) -> "GraphQLModel":
        type_hints = get_type_hints(cls)
        fields_args_options: Dict[str, dict] = {}
        fields_descriptions: Dict[str, str] = {}
        fields_resolvers: Dict[str, Resolver] = {}
        fields_instances: Dict[str, GraphQLObjectField] = {}

        for attr_name in dir(cls):
            cls_attr = getattr(cls, attr_name)
            if isinstance(cls_attr, GraphQLObjectField):
                fields_instances[attr_name] = cls_attr
                if cls_attr.args:
                    fields_args_options[attr_name] = cls_attr.args
                if cls_attr.description:
                    fields_descriptions[attr_name] = cls_attr.description
            if isinstance(cls_attr, GraphQLObjectResolver):
                fields_resolvers[cls_attr.field] = cls_attr.resolver
                if cls_attr.args:
                    fields_args_options[cls_attr.field] = cls_attr.args
                if cls_attr.description:
                    fields_descriptions[cls_attr.field] = cls_attr.description

        fields_ast: List[FieldDefinitionNode] = []
        resolvers: Dict[str, Resolver] = {}
        out_names: Dict[str, Dict[str, str]] = {}

        for hint_name, hint_type in type_hints.items():
            if hint_name.startswith("__"):
                continue

            if hint_name in fields_instances:
                continue

            hint_field_name = convert_python_name_to_graphql(hint_name)

            if hint_name in fields_resolvers:
                resolvers[hint_field_name] = fields_resolvers[hint_name]
                field_args = get_field_args_from_resolver(resolvers[hint_field_name])
                if field_args:
                    if fields_args_options.get(hint_field_name):
                        update_args_options(
                            field_args, fields_args_options[hint_field_name]
                        )

                    out_names[hint_field_name] = get_field_args_out_names(field_args)
            else:
                field_args = {}

            fields_ast.append(
                get_field_node_from_type_hint(
                    hint_field_name,
                    hint_type,
                    field_args,
                    fields_descriptions.get(hint_name),
                )
            )

        for attr_name, attr_field in fields_instances.items():
            field_instance = GraphQLObjectField(
                name=attr_field.name or convert_python_name_to_graphql(attr_name),
                description=attr_field.description
                or fields_descriptions.get(attr_name),
                type=attr_field.type or type_hints.get(attr_name),
                resolver=attr_field.resolver,
            )

            if field_instance.type is None:
                raise ValueError(
                    f"Unable to find return type for field '{field_instance.name}'. "
                    "Either add a return type annotation on it's resolver or specify "
                    "return type explicitly via 'type=...' option."
                )

            field_resolver: Optional[Resolver] = None
            if field_instance.resolver:
                field_resolver = field_instance.resolver
            elif attr_name in fields_resolvers:
                field_resolver = fields_resolvers[attr_name]

            field_args = {}
            if field_resolver:
                resolvers[field_instance.name] = field_resolver
                field_args = get_field_args_from_resolver(field_resolver)
                if field_instance.name in fields_args_options:
                    update_args_options(
                        field_args, fields_args_options[field_instance.name]
                    )

            fields_ast.append(get_field_node_from_obj_field(field_instance, field_args))

            if field_args:
                out_names[field_instance.name] = get_field_args_out_names(field_args)

        object_description = getattr(cls, "__description__", None)
        if object_description:
            description = StringValueNode(value=object_description)
        else:
            description = None

        return GraphQLObjectModel(
            name=name,
            ast=ObjectTypeDefinitionNode(
                name=NameNode(value=name),
                description=description,
                fields=tuple(fields_ast),
            ),
            resolvers=resolvers,
            aliases=getattr(cls, "__aliases__", {}),
            out_names=out_names,
        )

    @classmethod
    def __get_graphql_types__(cls) -> Iterable["GraphQLType"]:
        """Returns iterable with GraphQL types associated with this type"""
        types: List[GraphQLType] = [cls]

        for attr_name in dir(cls):
            cls_attr = getattr(cls, attr_name)
            if isinstance(cls_attr, GraphQLObjectField):
                if cls_attr.type:
                    field_graphql_type = get_graphql_type(cls_attr.type)
                    if field_graphql_type and field_graphql_type not in types:
                        types.append(field_graphql_type)

        type_hints = get_type_hints(cls)
        for hint_type in type_hints.values():
            hint_graphql_type = get_graphql_type(hint_type)
            if hint_graphql_type and hint_graphql_type not in types:
                types.append(hint_graphql_type)

        return types

    @staticmethod
    def field(
        f: Optional[Resolver] = None,
        *,
        name: Optional[str] = None,
        type: Optional[Any] = None,
        args: Optional[Dict[str, dict]] = None,
        description: Optional[str] = None,
    ):
        """Shortcut for object_field()"""
        return object_field(
            f,
            args=args,
            name=name,
            type=type,
            description=description,
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
    ) -> dict:
        options: dict = {}
        if name:
            options["name"] = name
        if description:
            options["description"] = description
        if type:
            options["type"] = type
        return options


def validate_object_type(cls: Type[GraphQLObject]):
    attrs_names: List[str] = [
        attr_name for attr_name in get_type_hints(cls) if not attr_name.startswith("__")
    ]
    resolvers_names: List[str] = []

    for attr_name in dir(cls):
        cls_attr = getattr(cls, attr_name)
        if isinstance(cls_attr, GraphQLObjectField):
            if cls_attr not in attrs_names:
                attrs_names.append(cls_attr)
        if isinstance(cls_attr, GraphQLObjectResolver):
            resolvers_names.append(cls_attr.field)

    for resolver_for in resolvers_names:
        if resolver_for not in attrs_names:
            valid_fields: str = "', '".join(sorted(attrs_names))
            raise ValueError(
                f"Class '{cls.__name__}' defines resolver for an undefined "
                f"attribute '{resolver_for}'. (Valid attrs: '{valid_fields}')"
            )


def validate_object_type_with_schema(cls: Type[GraphQLObject]):
    definition = parse_definition(ObjectTypeDefinitionNode, cls.__schema__)

    if not isinstance(definition, ObjectTypeDefinitionNode):
        raise ValueError(
            f"Class '{cls.__name__}' defines '__schema__' attribute "
            "with declaration for an invalid GraphQL type. "
            f"('{definition.__class__.__name__}' != "
            f"'{ObjectTypeDefinitionNode.__name__}')"
        )

    field_names: List[str] = [f.name.value for f in definition.fields]
    for attr_name in dir(cls):
        cls_attr = getattr(cls, attr_name)
        if isinstance(cls_attr, GraphQLObjectResolver):
            if cls_attr.field not in field_names:
                valid_fields: str = "', '".join(sorted(field_names))
                raise ValueError(
                    f"Class '{cls.__name__}' defines resolver for an undefined "
                    f"field '{cls_attr.field}'. (Valid fields: '{valid_fields}')"
                )

    validate_description(cls, definition)


class GraphQLObjectField:
    name: Optional[str]
    description: Optional[str]
    type: Optional[Any]
    args: Optional[Dict[str, dict]]
    resolver: Optional[Resolver]

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        type: Optional[Any] = None,
        args: Optional[Dict[str, dict]] = None,
        resolver: Optional[Resolver] = None,
    ):
        self.name = name
        self.description = description
        self.type = type
        self.args = args
        self.resolver = resolver


def object_field(
    f: Optional[Resolver] = None,
    *,
    args: Optional[Dict[str, dict]] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    type: Optional[Any] = None,
):
    def object_field_factory(f: Optional[Resolver]) -> GraphQLObjectField:
        field_name: Optional[str] = None
        field_type: Any = None

        if name:
            field_name = name

        if type:
            field_type = type
        elif f:
            field_type = get_field_type_from_resolver(f)

        return GraphQLObjectField(
            name=field_name,
            description=description,
            type=field_type,
            args=args,
            resolver=f,
        )

    if f is not None:
        return object_field_factory(f)

    return object_field_factory


def get_field_type_from_resolver(resolver: Resolver) -> Any:
    return get_type_hints(resolver).get("return")


class GraphQLObjectResolver:
    resolver: Resolver
    field: str
    description: Optional[str]
    args: Optional[Dict[str, dict]]
    type: Optional[Any]

    def __init__(
        self,
        resolver: Resolver,
        field: str,
        *,
        description: Optional[str] = None,
        args: Optional[Dict[str, dict]] = None,
        type: Optional[Any] = None,
    ):
        self.args = args
        self.description = description
        self.resolver = resolver
        self.field = field
        self.type = type


def object_resolver(
    field: str,
    type: Optional[Any] = None,
    args: Optional[Dict[str, dict]] = None,
    description: Optional[str] = None,
):
    def object_resolver_factory(f: Optional[Resolver]) -> GraphQLObjectResolver:
        field_type: Any = None

        if field:
            field_name = field
        elif f.__name__ != "<lambda>":
            field_name = convert_python_name_to_graphql(f.__name__)

        if type:
            field_type = type
        else:
            field_type = get_field_type_from_resolver(f)

        return GraphQLObjectResolver(
            args=args,
            description=description,
            resolver=f,
            field=field_name,
            type=field_type,
        )

    return object_resolver_factory


class GraphQLObjectModel(GraphQLModel):
    ast_type = ObjectTypeDefinitionNode
    resolvers: Dict[str, Resolver]
    aliases: Dict[str, str]
    out_names: Dict[str, Dict[str, str]]

    def __init__(
        self,
        name: str,
        ast: ObjectTypeDefinitionNode,
        resolvers: Dict[str, Resolver],
        aliases: Dict[str, str],
        out_names: Dict[str, Dict[str, str]],
    ):
        self.name = name
        self.ast = ast
        self.resolvers = resolvers
        self.aliases = aliases
        self.out_names = out_names

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


def get_field_node_from_type_hint(
    field_name: str,
    field_type: Any,
    field_args: Any,
    field_description: Optional[str] = None,
) -> FieldDefinitionNode:
    if field_description:
        description = StringValueNode(value=field_description)
    else:
        description = None

    return FieldDefinitionNode(
        description=description,
        name=NameNode(value=field_name),
        type=get_type_node(field_type),
        arguments=get_field_args_nodes_from_obj_field_args(field_args),
    )


def get_field_node_from_obj_field(
    field: GraphQLObjectField,
    field_args: Any,
) -> FieldDefinitionNode:
    if field.description:
        description = StringValueNode(value=field.description)
    else:
        description = None

    return FieldDefinitionNode(
        description=description,
        name=NameNode(value=field.name),
        type=get_type_node(field.type),
        arguments=get_field_args_nodes_from_obj_field_args(field_args),
    )


class GraphQLObjectFieldArg:
    name: Optional[str]
    out_name: Optional[str]
    description: Optional[str]
    type: Optional[Any]

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        out_name: Optional[str] = None,
        description: Optional[str] = None,
        type: Optional[Any] = None,
    ):
        self.name = name
        self.out_name = out_name
        self.description = description
        self.type = type


def get_field_args_from_resolver(
    resolver: Resolver,
) -> Dict[str, GraphQLObjectFieldArg]:
    resolver_signature = signature(resolver)
    type_hints = get_type_hints(resolver)
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
                f"Resolver function '{resolver_signature}' should accept at least 'obj' and 'info' positional arguments."
            )

        field_args_start = 2

    args_parameters = tuple(resolver_signature.parameters.items())[field_args_start:]
    if not args_parameters:
        return field_args

    for param_name, param in args_parameters:
        field_args[param_name] = GraphQLObjectFieldArg(
            name=convert_python_name_to_graphql(param_name),
            out_name=param_name,
            type=type_hints.get(param_name),
        )

    return field_args


def get_field_args_out_names(
    field_args: Dict[str, GraphQLObjectFieldArg]
) -> Dict[str, str]:
    out_names: Dict[str, str] = {}
    for field_arg in field_args.values():
        out_names[field_arg.name] = field_arg.out_name
    return out_names


def get_field_args_nodes_from_obj_field_args(
    field_args: Dict[str, GraphQLObjectFieldArg]
) -> Tuple[InputValueDefinitionNode]:
    return tuple(
        get_field_arg_node_from_obj_field_arg(field_arg)
        for field_arg in field_args.values()
    )


def get_field_arg_node_from_obj_field_arg(
    field_arg: GraphQLObjectFieldArg,
) -> InputValueDefinitionNode:
    if field_arg.description:
        description = StringValueNode(value=field_arg.description)
    else:
        description = None

    return InputValueDefinitionNode(
        description=description,
        name=NameNode(value=field_arg.name),
        type=get_type_node(field_arg.type),
    )


def update_args_options(
    resolver_args: Dict[str, GraphQLObjectFieldArg],
    args_options: Optional[Dict[str, dict]],
):
    if not args_options:
        return

    for arg_name, arg_options in args_options.items():
        resolver_arg = resolver_args[arg_name]
        if arg_options.get("name"):
            resolver_arg.name = arg_options["name"]
        if arg_options.get("description"):
            resolver_arg.description = arg_options["description"]
        if arg_options.get("type"):
            resolver_arg.type = arg_options["type"]
