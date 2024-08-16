# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_arg_with_description_in_source_with_schema 1'] = "Class 'SubscriptionType' defines 'type' option for 'channel' argument of the 'messageAdded' field. This is not supported for types defining '__schema__'."

snapshots['test_arg_with_name_in_source_with_schema 1'] = "Class 'SubscriptionType' defines 'name' option for 'channel' argument of the 'messageAdded' field. This is not supported for types defining '__schema__'."

snapshots['test_arg_with_type_in_source_with_schema 1'] = "Class 'SubscriptionType' defines 'type' option for 'channel' argument of the 'messageAdded' field. This is not supported for types defining '__schema__'."

snapshots['test_description_not_str_without_schema 1'] = 'The description for message_added_generator must be a string if provided.'

snapshots['test_field_name_not_str_without_schema 1'] = 'The field name for message_added_generator must be a string.'

snapshots['test_invalid_arg_name_in_source_with_schema 1'] = "Class 'SubscriptionType' defines options for 'channelID' argument of the 'messageAdded' field that doesn't exist."

snapshots['test_multiple_descriptions_for_source_with_schema 1'] = "Class 'SubscriptionType' defines multiple descriptions for field 'messageAdded'."

snapshots['test_multiple_sourced_for_field_with_schema 1'] = "Class 'SubscriptionType' defines multiple sources for field 'messageAdded'."

snapshots['test_multiple_sources_without_schema 1'] = "Class 'SubscriptionType' defines multiple sources for field 'message_added'."

snapshots['test_source_args_field_arg_not_dict_without_schema 1'] = 'Argument channel for message_added_generator must have a GraphQLObjectFieldArg as its info.'

snapshots['test_source_args_not_dict_without_schema 1'] = 'The args for message_added_generator must be a dictionary if provided.'

snapshots['test_source_for_undefined_field_with_schema 1'] = "Class 'SubscriptionType' defines source for an undefined field 'message_added'. (Valid fields: 'messageAdded')"

snapshots['test_undefined_name_without_schema 1'] = "Class 'SubscriptionType' defines source for an undefined field 'messageAdded'. (Valid fields: 'message_added')"
