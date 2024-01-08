# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_multiple_roots_fail_validation_if_merge_roots_is_disabled 1'] = "Types 'SecondRoot' and '<class 'tests_next.test_make_executable_schema.test_multiple_roots_fail_validation_if_merge_roots_is_disabled.<locals>.FirstRoot'>' both define GraphQL type with name 'Query'."
