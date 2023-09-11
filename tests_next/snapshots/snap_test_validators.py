# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_description_validator_raises_error_for_type_with_two_descriptions 1'] = "Class 'CustomType' defines description in both '__description__' and '__schema__' attributes."

snapshots['test_name_validator_raises_error_for_name_and_definition_mismatch 1'] = "Class 'CustomType' defines both '__graphql_name__' and '__schema__' attributes, but names in those don't match. ('Example' != 'Custom')"
