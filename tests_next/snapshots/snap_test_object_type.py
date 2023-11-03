# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_object_type_instance_with_invalid_attrs_raising_error 1'] = "CategoryType.__init__() got an unexpected keyword argument 'invalid'. Valid keyword arguments: 'name', 'posts'"

snapshots['test_object_type_with_schema_instance_with_invalid_attrs_raising_error 1'] = "CategoryType.__init__() got an unexpected keyword argument 'invalid'. Valid keyword arguments: 'name', 'posts'"
