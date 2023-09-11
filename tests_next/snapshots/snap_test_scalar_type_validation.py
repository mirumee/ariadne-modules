# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_scalar_type_validation_fails_for_invalid_type_schema 1'] = "Class 'CustomScalar' defines '__schema__' attribute with declaration for an invalid GraphQL type. ('ObjectTypeDefinitionNode' != 'ScalarTypeDefinitionNode')"

snapshots['test_scalar_type_validation_fails_for_name_mismatch_between_schema_and_attr 1'] = "Class 'CustomScalar' defines both '__graphql_name__' and '__schema__' attributes, but names in those don't match. ('Date' != 'Custom')"

snapshots['test_scalar_type_validation_fails_for_two_descriptions 1'] = "Class 'CustomScalar' defines description in both '__description__' and '__schema__' attributes."
