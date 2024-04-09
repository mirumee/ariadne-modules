# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_missing_type_in_schema 1'] = "Types {'Comment'} are defined in __types__ but not present in the __schema__."

snapshots['test_missing_type_in_types 1'] = "Types {'Comment'} are present in the __schema__ but not defined in __types__."
