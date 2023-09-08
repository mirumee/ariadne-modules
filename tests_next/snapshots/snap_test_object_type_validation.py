# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_object_type_validation_fails_for_invalid_type_schema 1'] = "Class 'CustomType' defines '__schema__' attribute with declaration for an invalid GraphQL type. ('ScalarTypeDefinitionNode' != 'ObjectTypeDefinitionNode')"

snapshots['test_object_type_validation_fails_for_two_descriptions 1'] = "Class 'CustomType' defines description in both '__description__' and '__schema__' attributes."

snapshots['test_object_type_validation_fails_for_undefined_attr_resolver 1'] = "Class 'QueryType' defines resolver for an undefined attribute 'other'. (Valid attrs: 'hello')"

snapshots['test_object_type_validation_fails_for_undefined_field_resolver 1'] = "Class 'QueryType' defines resolver for an undefined field 'other'. (Valid fields: 'hello')"
