# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_missing_type_in_schema 1'] = "Types 'Comment', 'Post' are in '__types__' but not in '__schema__'."

snapshots['test_missing_type_in_types 1'] = "Types 'Comment' are in '__schema__' but not in '__types__'."
