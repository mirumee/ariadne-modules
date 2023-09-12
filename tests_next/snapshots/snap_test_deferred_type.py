# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_deferred_raises_error_for_invalid_relative_path 1'] = "'...types' points outside of the 'lorem' package."
