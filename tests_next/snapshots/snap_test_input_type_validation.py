# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_input_type_validation_fails_for_duplicate_schema_out_name 1'] = "Class 'CustomType' defines multiple fields with an outname 'ok' in it's '__out_names__' attribute."

snapshots['test_input_type_validation_fails_for_invalid_schema_out_name 1'] = "Class 'CustomType' defines an outname for 'invalid' field in it's '__out_names__' attribute which is not defined in '__schema__'."

snapshots['test_input_type_validation_fails_for_invalid_type_schema 1'] = "Class 'CustomType' defines '__schema__' attribute with declaration for an invalid GraphQL type. ('ScalarTypeDefinitionNode' != 'InputObjectTypeDefinitionNode')"

snapshots['test_input_type_validation_fails_for_names_not_matching 1'] = "Class 'CustomType' defines both '__graphql_name__' and '__schema__' attributes, but names in those don't match. ('Lorem' != 'Custom')"

snapshots['test_input_type_validation_fails_for_out_names_without_schema 1'] = "Class 'CustomType' defines '__out_names__' attribute. This is not supported for types not defining '__schema__'."

snapshots['test_input_type_validation_fails_for_schema_missing_fields 1'] = "Class 'CustomType' defines '__schema__' attribute with declaration for an input type without any fields. "

snapshots['test_input_type_validation_fails_for_two_descriptions 1'] = "Class 'CustomType' defines description in both '__description__' and '__schema__' attributes."

snapshots['test_input_type_validation_fails_for_unsupported_attr_default 1'] = "Class 'QueryType' defines default value for the 'attr' field that can't be represented in GraphQL schema."

snapshots['test_input_type_validation_fails_for_unsupported_field_default_option 1'] = "Class 'QueryType' defines default value for the 'attr' field that can't be represented in GraphQL schema."
