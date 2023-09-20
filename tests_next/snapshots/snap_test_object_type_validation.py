# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_object_type_validation_fails_for_invalid_type_schema 1'] = "Class 'CustomType' defines '__schema__' attribute with declaration for an invalid GraphQL type. ('ScalarTypeDefinitionNode' != 'ObjectTypeDefinitionNode')"

snapshots['test_object_type_validation_fails_for_missing_field_resolver_arg 1'] = "Class 'CustomType' defines 'hello' field with extra configuration for 'invalid' argument thats not defined on the resolver function. (expected one of: 'name')"

snapshots['test_object_type_validation_fails_for_missing_resolver_arg 1'] = "Class 'CustomType' defines 'resolve_hello' resolver with extra configuration for 'invalid' argumentthats not defined on the resolver function. (expected one of: 'name')"

snapshots['test_object_type_validation_fails_for_names_not_matching 1'] = "Class 'CustomType' defines both '__graphql_name__' and '__schema__' attributes, but names in those don't match. ('Lorem' != 'Custom')"

snapshots['test_object_type_validation_fails_for_two_descriptions 1'] = "Class 'CustomType' defines description in both '__description__' and '__schema__' attributes."

snapshots['test_object_type_validation_fails_for_undefined_attr_resolver 1'] = "Class 'QueryType' defines resolver for an undefined attribute 'other'. (Valid attrs: 'hello')"

snapshots['test_object_type_validation_fails_for_undefined_field_resolver 1'] = "Class 'QueryType' defines resolver for an undefined field 'other'. (Valid fields: 'hello')"

snapshots['test_object_type_validation_fails_for_undefined_field_resolver_arg 1'] = "Class 'CustomType' defines 'hello' field with extra configuration for 'invalid' argument thats not defined on the resolver function. (function accepts no extra arguments)"

snapshots['test_object_type_validation_fails_for_undefined_resolver_arg 1'] = "Class 'CustomType' defines 'resolve_hello' resolver with extra configuration for 'invalid' argumentthats not defined on the resolver function. (function accepts no extra arguments)"
