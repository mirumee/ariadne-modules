# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_value_error_is_raised_if_exclude_and_include_members_are_combined 1'] = "'members_include' and 'members_exclude' options are mutually exclusive."

snapshots['test_value_error_is_raised_if_member_description_is_set_for_excluded_item 1'] = "Member description was specified for a member 'ADMINISTRATOR' not present in final GraphQL enum."

snapshots['test_value_error_is_raised_if_member_description_is_set_for_missing_item 1'] = "Member description was specified for a member 'MISSING' not present in final GraphQL enum."

snapshots['test_value_error_is_raised_if_member_description_is_set_for_omitted_item 1'] = "Member description was specified for a member 'ADMINISTRATOR' not present in final GraphQL enum."
