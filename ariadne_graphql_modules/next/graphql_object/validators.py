from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type, Union, cast

from graphql import FieldDefinitionNode, ObjectTypeDefinitionNode, TypeDefinitionNode

from ..convert_name import convert_python_name_to_graphql
from .object_field import (
    GraphQLObjectField,
    GraphQLObjectFieldArg,
    GraphQLObjectResolver,
    GraphQLObjectSource,
)
from .utils import (
    get_field_args_from_resolver,
    get_field_args_from_subscriber,
)
from ..validators import validate_description, validate_name
from ..value import get_value_node
from ...utils import parse_definition

if TYPE_CHECKING:
    from .object_type import GraphQLObject


@dataclass
class GraphQLObjectValidationData:
    aliases: Dict[str, str]
    fields_attrs: List[str]
    fields_instances: Dict[str, GraphQLObjectField]
    resolvers_instances: Dict[str, GraphQLObjectResolver]
    sources_instances: Dict[str, GraphQLObjectSource]


def validate_object_type_with_schema(
    cls: Type["GraphQLObject"],
    valid_type: Type[TypeDefinitionNode] = ObjectTypeDefinitionNode,
) -> Dict[str, Any]:
    definition = cast(
        ObjectTypeDefinitionNode, parse_definition(valid_type, cls.__schema__)
    )

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
    source_fields: List[str] = []
    valid_fields: str = ""

    for attr_name in dir(cls):
        cls_attr = getattr(cls, attr_name)
        if isinstance(cls_attr, GraphQLObjectField):
            raise ValueError(
                f"Class '{cls.__name__}' defines 'GraphQLObjectField' instance. "
                "This is not supported for types defining '__schema__'."
            )

        if isinstance(cls_attr, GraphQLObjectResolver):
            if cls_attr.field not in field_names:
                valid_fields = "', '".join(sorted(field_names))
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

                    if arg_options.name:
                        raise ValueError(
                            f"Class '{cls.__name__}' defines 'name' option for "
                            f"'{arg_name}' argument of the '{cls_attr.field}' field. "
                            "This is not supported for types defining '__schema__'."
                        )

                    if arg_options.field_type:
                        raise ValueError(
                            f"Class '{cls.__name__}' defines 'type' option for "
                            f"'{arg_name}' argument of the '{cls_attr.field}' field. "
                            "This is not supported for types defining '__schema__'."
                        )

                    if arg_options.description and field_args[arg_name].description:
                        raise ValueError(
                            f"Class '{cls.__name__}' defines duplicate descriptions "
                            f"for '{arg_name}' argument "
                            f"of the '{cls_attr.field}' field."
                        )

                    validate_field_arg_default_value(
                        cls, cls_attr.field, arg_name, arg_options.default_value
                    )

            resolver_args = get_field_args_from_resolver(cls_attr.resolver)
            for arg_name, arg_obj in resolver_args.items():
                validate_field_arg_default_value(
                    cls, cls_attr.field, arg_name, arg_obj.default_value
                )
        if isinstance(cls_attr, GraphQLObjectSource):
            if cls_attr.field not in field_names:
                valid_fields = "', '".join(sorted(field_names))
                raise ValueError(
                    f"Class '{cls.__name__}' defines source for an undefined "
                    f"field '{cls_attr.field}'. (Valid fields: '{valid_fields}')"
                )

            if cls_attr.field in source_fields:
                raise ValueError(
                    f"Class '{cls.__name__}' defines multiple sources for field "
                    f"'{cls_attr.field}'."
                )

            source_fields.append(cls_attr.field)

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

                    if arg_options.name:
                        raise ValueError(
                            f"Class '{cls.__name__}' defines 'name' option for "
                            f"'{arg_name}' argument of the '{cls_attr.field}' field. "
                            "This is not supported for types defining '__schema__'."
                        )

                    if arg_options.field_type:
                        raise ValueError(
                            f"Class '{cls.__name__}' defines 'type' option for "
                            f"'{arg_name}' argument of the '{cls_attr.field}' field. "
                            "This is not supported for types defining '__schema__'."
                        )

                    if arg_options.description and field_args[arg_name].description:
                        raise ValueError(
                            f"Class '{cls.__name__}' defines duplicate descriptions "
                            f"for '{arg_name}' argument "
                            f"of the '{cls_attr.field}' field."
                        )

                    validate_field_arg_default_value(
                        cls, cls_attr.field, arg_name, arg_options.default_value
                    )

            subscriber_args = get_field_args_from_subscriber(cls_attr.subscriber)
            for arg_name, arg_obj in subscriber_args.items():
                validate_field_arg_default_value(
                    cls, cls_attr.field, arg_name, arg_obj.default_value
                )

    aliases: Dict[str, str] = getattr(cls, "__aliases__", None) or {}
    validate_object_aliases(cls, aliases, field_names, fields_resolvers)

    return get_object_type_with_schema_kwargs(cls, aliases, field_names)


def validate_object_type_without_schema(cls: Type["GraphQLObject"]) -> Dict[str, Any]:
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
    validate_object_subscribers(cls, data.fields_attrs, data.sources_instances)
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
    cls: Type["GraphQLObject"],
    fields_attrs: List[str],
    fields_instances: Dict[str, GraphQLObjectField],
):
    graphql_names: List[str] = []
    for attr_name in fields_attrs:
        if attr_name in fields_instances and fields_instances[attr_name].name:
            attr_graphql_name = fields_instances[attr_name].name
        else:
            attr_graphql_name = convert_python_name_to_graphql(attr_name)

        if not attr_graphql_name:
            raise ValueError(
                f"Field '{attr_name}' in class '{cls.__name__}' has "
                "an invalid or empty GraphQL name."
            )

        if attr_graphql_name in graphql_names:
            raise ValueError(
                f"Class '{cls.__name__}' defines multiple fields with GraphQL "
                f"name '{attr_graphql_name}'."
            )
        graphql_names.append(attr_graphql_name)


def validate_object_resolvers(
    cls: Type["GraphQLObject"],
    fields_names: List[str],
    fields_instances: Dict[str, GraphQLObjectField],
    resolvers_instances: Dict[str, GraphQLObjectResolver],
):
    resolvers_fields: List[str] = []

    for field_attr, field in fields_instances.items():
        if field.resolver:
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

        field_instance: Optional[GraphQLObjectField] = fields_instances.get(
            resolver.field
        )
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


def validate_object_subscribers(
    cls: Type["GraphQLObject"],
    fields_names: List[str],
    sources_instances: Dict[str, GraphQLObjectSource],
):
    source_fields: List[str] = []

    for key, source in sources_instances.items():
        if not isinstance(source.field, str):
            raise ValueError(f"The field name for {key} must be a string.")
        if source.field not in fields_names:
            valid_fields: str = "', '".join(sorted(fields_names))
            raise ValueError(
                f"Class '{cls.__name__}' defines source for an undefined "
                f"field '{source.field}'. (Valid fields: '{valid_fields}')"
            )
        if source.field in source_fields:
            raise ValueError(
                f"Class '{cls.__name__}' defines multiple sources for field "
                f"'{source.field}'."
            )

        source_fields.append(source.field)

        if source.description is not None and not isinstance(source.description, str):
            raise ValueError(f"The description for {key} must be a string if provided.")

        if source.args is not None:
            if not isinstance(source.args, dict):
                raise ValueError(
                    f"The args for {key} must be a dictionary if provided."
                )
            for arg_name, arg_info in source.args.items():
                if not isinstance(arg_info, GraphQLObjectFieldArg):
                    raise ValueError(
                        f"Argument {arg_name} for {key} must "
                        "have a GraphQLObjectFieldArg as its info."
                    )


def validate_object_fields_args(cls: Type["GraphQLObject"]):
    for field_name in dir(cls):
        field_instance = getattr(cls, field_name)
        if (
            isinstance(field_instance, (GraphQLObjectField, GraphQLObjectResolver))
            and field_instance.resolver
        ):
            validate_object_field_args(cls, field_name, field_instance)


def validate_object_field_args(
    cls: Type["GraphQLObject"],
    field_name: str,
    field_instance: Union["GraphQLObjectField", "GraphQLObjectResolver"],
):
    if field_instance.resolver:
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
            cls, field_name, arg_name, arg_options.default_value
        )


def validate_object_aliases(
    cls: Type["GraphQLObject"],
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


def validate_field_arg_default_value(
    cls: Type["GraphQLObject"], field_name: str, arg_name: str, default_value: Any
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


def get_object_type_validation_data(
    cls: Type["GraphQLObject"],
) -> GraphQLObjectValidationData:
    fields_attrs: List[str] = [
        attr_name for attr_name in cls.__annotations__ if not attr_name.startswith("__")
    ]

    fields_instances: Dict[str, GraphQLObjectField] = {}
    resolvers_instances: Dict[str, GraphQLObjectResolver] = {}
    sources_instances: Dict[str, GraphQLObjectSource] = {}

    for attr_name in dir(cls):
        if attr_name.startswith("__"):
            continue

        cls_attr = getattr(cls, attr_name)
        if isinstance(cls_attr, GraphQLObjectResolver):
            resolvers_instances[attr_name] = cls_attr
            if attr_name in fields_attrs:
                fields_attrs.remove(attr_name)

        if isinstance(cls_attr, GraphQLObjectSource):
            sources_instances[attr_name] = cls_attr
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
        sources_instances=sources_instances,
    )


def get_object_type_kwargs(
    cls: Type["GraphQLObject"],
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
    cls: Type["GraphQLObject"],
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
