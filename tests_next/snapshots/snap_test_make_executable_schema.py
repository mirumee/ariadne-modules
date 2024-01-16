# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_make_executable_schema_raises_error_if_called_without_any_types 1'] = "'make_executable_schema' was called without any GraphQL types."

snapshots['test_multiple_roots_fail_validation_if_merge_roots_is_disabled 1'] = "Types 'SecondRoot' and '<class 'tests_next.test_make_executable_schema.test_multiple_roots_fail_validation_if_merge_roots_is_disabled.<locals>.FirstRoot'>' both define GraphQL type with name 'Query'."

snapshots['test_schema_validation_fails_if_lazy_type_doesnt_exist 1'] = "Unknown type 'Missing'."
