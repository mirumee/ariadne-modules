from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Type,
    cast,
    get_type_hints,
)

from ariadne import ObjectType as ObjectTypeBindable
from ariadne.types import Resolver
from graphql import (
    FieldDefinitionNode,
    GraphQLSchema,
    NameNode,
    ObjectTypeDefinitionNode,
)

from ..utils import parse_definition
from .base import GraphQLModel, GraphQLType
from .convert_name import convert_python_name_to_graphql
from .typing import get_graphql_type, get_type_node


class GraphQLObject(GraphQLType):
    __schema__: Optional[str]
    __requires__: Optional[Iterable[GraphQLType]]

    __abstract__: bool = True

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
            out_names=out_names,
        )

    @classmethod
    def __get_graphql_model_without_schema__(cls, name: str) -> "GraphQLModel":
        type_hints = get_type_hints(cls)
        fields_resolvers: Dict[str, Resolver] = {}
        fields_instances: Dict[str, GraphQLObjectField] = {}

        for attr_name in dir(cls):
            cls_attr = getattr(cls, attr_name)
            if isinstance(cls_attr, GraphQLObjectField):
                fields_instances[attr_name] = cls_attr
            if isinstance(cls_attr, GraphQLObjectResolver):
                fields_resolvers[cls_attr.field] = cls_attr.resolver

        fields_ast: List[FieldDefinitionNode] = []
        resolvers: Dict[str, Resolver] = {}
        out_names: Dict[str, Dict[str, str]] = {}

        for hint_name, hint_type in type_hints.items():
            if hint_name.startswith("__"):
                continue

            if hint_name in fields_instances:
                continue

            hint_field_name = convert_python_name_to_graphql(hint_name)

            fields_ast.append(get_field_node_from_type_hint(hint_field_name, hint_type))

            if hint_name in fields_resolvers:
                resolvers[hint_field_name] = fields_resolvers[hint_name]

        for attr_name, attr_field in fields_instances.items():
            field_instance = GraphQLObjectField(
                name=attr_field.name or convert_python_name_to_graphql(attr_name),
                type=attr_field.type or type_hints.get(attr_name),
                resolver=attr_field.resolver,
            )

            if field_instance.type is None:
                raise ValueError(
                    f"Unable to find return type for field '{field_instance.name}'. "
                    "Either add a return type annotation on it's resolver or specify "
                    "return type explicitly via 'type=...' option."
                )

            if field_instance.resolver:
                resolvers[field_instance.name] = field_instance.resolver
            elif attr_name in fields_resolvers:
                resolvers[field_instance.name] = fields_resolvers[attr_name]

            fields_ast.append(get_field_node_from_obj_field(field_instance))

        return GraphQLObjectModel(
            name=name,
            ast=ObjectTypeDefinitionNode(
                name=NameNode(value=name),
                fields=tuple(fields_ast),
            ),
            resolvers=resolvers,
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
    ):
        """Shortcut for object_field()"""
        return object_field(f, name=name, type=type)

    @staticmethod
    def resolver(
        field: str,
        type: Optional[Any] = None,
    ):
        """Shortcut for object_resolver()"""
        return object_resolver(field=field, type=type)


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


class GraphQLObjectField:
    def __init__(
        self,
        *,
        name: Optional[str] = None,
        type: Optional[Any] = None,
        resolver: Optional[Resolver] = None,
    ):
        self.name = name
        self.type = type
        self.resolver = resolver


def object_field(
    f: Optional[Resolver] = None,
    *,
    name: Optional[str] = None,
    type: Optional[Any] = None,
):
    def object_field_factory(f: Optional[Resolver]) -> GraphQLObjectField:
        field_name: Optional[str] = None
        field_type: Any = None

        if name:
            field_name = name
        elif f.__name__ != "<lambda>":
            field_name = convert_python_name_to_graphql(f.__name__)

        if type:
            field_type = type
        elif f:
            field_type = get_field_type_from_resolver(f)

        return GraphQLObjectField(
            resolver=f,
            name=field_name,
            type=field_type,
        )

    if f is not None:
        return object_field_factory(f)

    return object_field_factory


def get_field_type_from_resolver(resolver: Resolver) -> Any:
    return get_type_hints(resolver).get("return")


class GraphQLObjectResolver:
    def __init__(
        self,
        resolver: Resolver,
        field: str,
        *,
        type: Optional[Any] = None,
    ):
        self.resolver = resolver
        self.field = field
        self.type = type


def object_resolver(
    field: str,
    type: Optional[Any] = None,
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
            resolver=f,
            field=field_name,
            type=field_type,
        )

    return object_resolver_factory


class GraphQLObjectModel(GraphQLModel):
    ast_type = ObjectTypeDefinitionNode
    resolvers: Dict[str, Resolver]
    out_names: Dict[str, Dict[str, str]]

    def __init__(
        self,
        name: str,
        ast: ObjectTypeDefinitionNode,
        resolvers: Dict[str, Resolver],
        out_names: Dict[str, Dict[str, str]],
    ):
        self.name = name
        self.ast = ast
        self.resolvers = resolvers
        self.out_names = out_names

    def bind_to_schema(self, schema: GraphQLSchema):
        bindable = ObjectTypeBindable(self.name)

        for field, resolver in self.resolvers.items():
            bindable.set_field(field, resolver)

        bindable.bind_to_schema(schema)


def get_field_node_from_type_hint(
    field_name: str, field_type: Any
) -> FieldDefinitionNode:
    return FieldDefinitionNode(
        name=NameNode(value=field_name),
        type=get_type_node(field_type),
    )


def get_field_node_from_obj_field(field: GraphQLObjectField) -> FieldDefinitionNode:
    return FieldDefinitionNode(
        name=NameNode(value=field.name),
        type=get_type_node(field.type),
    )
