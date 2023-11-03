# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_object_type_validation_fails_for_attr_and_field_with_same_graphql_name 1'] = "Class 'CustomType' defines multiple fields with GraphQL name 'userId'."

snapshots['test_object_type_validation_fails_for_field_with_multiple_args 1'] = "Class 'CustomType' defines multiple resolvers for field 'lorem'."

snapshots['test_object_type_validation_fails_for_field_with_multiple_descriptions 1'] = "Class 'CustomType' defines multiple descriptions for field 'hello'."

snapshots['test_object_type_validation_fails_for_invalid_alias 1'] = "Class 'CustomType' defines an alias for an undefined field 'invalid'. (Valid fields: 'hello')"

snapshots['test_object_type_validation_fails_for_invalid_schema_alias 1'] = "Class 'CustomType' defines an alias for an undefined field 'invalid'. (Valid fields: 'hello')"

snapshots['test_object_type_validation_fails_for_invalid_type_schema 1'] = "Class 'CustomType' defines '__schema__' attribute with declaration for an invalid GraphQL type. ('ScalarTypeDefinitionNode' != 'ObjectTypeDefinitionNode')"

snapshots['test_object_type_validation_fails_for_missing_field_resolver_arg 1'] = "Class 'CustomType' defines 'hello' field with extra configuration for 'invalid' argument thats not defined on the resolver function. (expected one of: 'name')"

snapshots['test_object_type_validation_fails_for_missing_resolver_arg 1'] = "Class 'CustomType' defines 'resolve_hello' resolver with extra configuration for 'invalid' argument thats not defined on the resolver function. (expected one of: 'name')"

snapshots['test_object_type_validation_fails_for_multiple_attrs_with_same_graphql_name 1'] = "Class 'CustomType' defines multiple fields with GraphQL name 'userId'."

snapshots['test_object_type_validation_fails_for_multiple_field_resolvers 1'] = "Class 'CustomType' defines multiple resolvers for field 'hello'."

snapshots['test_object_type_validation_fails_for_multiple_fields_with_same_graphql_name 1'] = "Class 'CustomType' defines multiple fields with GraphQL name 'hello'."

snapshots['test_object_type_validation_fails_for_multiple_schema_field_resolvers 1'] = "Class 'CustomType' defines multiple resolvers for field 'hello'."

snapshots['test_object_type_validation_fails_for_names_not_matching 1'] = "Class 'CustomType' defines both '__graphql_name__' and '__schema__' attributes, but names in those don't match. ('Lorem' != 'Custom')"

snapshots['test_object_type_validation_fails_for_resolver_alias 1'] = "Class 'CustomType' defines an alias for a field 'hello' that already has a custom resolver."

snapshots['test_object_type_validation_fails_for_schema_field_with_arg_double_description 1'] = "Class 'CustomType' defines duplicate descriptions for 'name' argument of the 'hello' field."

snapshots['test_object_type_validation_fails_for_schema_field_with_arg_name 1'] = "Class 'CustomType' defines 'name' option for 'name' argument of the 'hello' field. This is not supported for types defining '__schema__'."

snapshots['test_object_type_validation_fails_for_schema_field_with_arg_type 1'] = "Class 'CustomType' defines 'type' option for 'name' argument of the 'hello' field. This is not supported for types defining '__schema__'."

snapshots['test_object_type_validation_fails_for_schema_field_with_invalid_arg_name 1'] = "Class 'CustomType' defines options for 'other' argument of the 'hello' field that doesn't exist."

snapshots['test_object_type_validation_fails_for_schema_field_with_multiple_descriptions 1'] = "Class 'CustomType' defines multiple descriptions for field 'hello'."

snapshots['test_object_type_validation_fails_for_schema_missing_fields 1'] = "Class 'CustomType' defines '__schema__' attribute with declaration for an object type without any fields. "

snapshots['test_object_type_validation_fails_for_schema_resolver_alias 1'] = "Class 'CustomType' defines an alias for a field 'hello' that already has a custom resolver."

snapshots['test_object_type_validation_fails_for_schema_with_field_instance 1'] = "Class 'CustomType' defines 'GraphQLObjectField' instance. This is not supported for types defining '__schema__'."

snapshots['test_object_type_validation_fails_for_two_descriptions 1'] = "Class 'CustomType' defines description in both '__description__' and '__schema__' attributes."

snapshots['test_object_type_validation_fails_for_undefined_attr_resolver 1'] = "Class 'QueryType' defines resolver for an undefined attribute 'other'. (Valid attrs: 'hello')"

snapshots['test_object_type_validation_fails_for_undefined_field_resolver 1'] = "Class 'QueryType' defines resolver for an undefined field 'other'. (Valid fields: 'hello')"

snapshots['test_object_type_validation_fails_for_undefined_field_resolver_arg 1'] = "Class 'CustomType' defines 'hello' field with extra configuration for 'invalid' argument thats not defined on the resolver function. (function accepts no extra arguments)"

snapshots['test_object_type_validation_fails_for_undefined_resolver_arg 1'] = "Class 'CustomType' defines 'resolve_hello' resolver with extra configuration for 'invalid' argument thats not defined on the resolver function. (function accepts no extra arguments)"

snapshots['test_object_type_validation_fails_for_unsupported_resolver_arg_default 1'] = "Class 'QueryType' defines default value for 'name' argument of the 'hello' field that can't be represented in GraphQL schema."

snapshots['test_object_type_validation_fails_for_unsupported_resolver_arg_default_option 1'] = "Class 'QueryType' defines default value for 'name' argument of the 'hello' field that can't be represented in GraphQL schema."

snapshots['test_object_type_validation_fails_for_unsupported_schema_resolver_arg_default 1'] = "Class 'QueryType' defines default value for 'name' argument of the 'hello' field that can't be represented in GraphQL schema."

snapshots['test_object_type_validation_fails_for_unsupported_schema_resolver_arg_option_default 1'] = "Class 'QueryType' defines default value for 'name' argument of the 'hello' field that can't be represented in GraphQL schema."
