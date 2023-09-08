# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_description_validator_raises_error_for_type_with_two_descriptions 1'] = "Class 'CustomType' defines description in both '__description__' and '__schema__' attributes."
