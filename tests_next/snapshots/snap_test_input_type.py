# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_input_type_instance_with_invalid_attrs_raising_error 1'] = "SearchInput.__init__() got an unexpected keyword argument 'invalid'. Valid keyword arguments: 'query', 'age'"

snapshots['test_schema_input_type_instance_with_invalid_attrs_raising_error 1'] = "SearchInput.__init__() got an unexpected keyword argument 'invalid'. Valid keyword arguments: 'query', 'age'"
