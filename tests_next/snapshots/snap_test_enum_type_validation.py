# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_enum_type_validation_fails_for_empty_enum 1'] = "Class 'UserLevel' defines '__schema__' attribute that doesn't declare any enum members."

snapshots['test_enum_type_validation_fails_for_invalid_members 1'] = "Class 'UserLevel' '__members__' attribute is of unsupported type. Expected 'Dict[str, Any]', 'Type[Enum]' or List[str]. (found: '<class 'str'>')"

snapshots['test_enum_type_validation_fails_for_invalid_type_schema 1'] = "Class 'UserLevel' defines '__schema__' attribute with declaration for an invalid GraphQL type. ('ScalarTypeDefinitionNode' != 'EnumTypeDefinitionNode')"

snapshots['test_enum_type_validation_fails_for_missing_members 1'] = "Class 'UserLevel' '__members__' attribute is either missing or empty. Either define it or provide full SDL for this enum using the '__schema__' attribute."

snapshots['test_enum_type_validation_fails_for_name_mismatch_between_schema_and_attr 1'] = "Class 'UserLevel' defines both '__graphql_name__' and '__schema__' attributes, but names in those don't match. ('UserRank' != 'Custom')"

snapshots['test_enum_type_validation_fails_for_schema_and_members_dict_mismatch 1'] = "Class 'UserLevel' '__members__' is missing values for enum members defined in '__schema__'. (missing items: 'MEMBER')"

snapshots['test_enum_type_validation_fails_for_schema_and_members_duplicated_descriptions 1'] = "Class 'UserLevel' '__members_descriptions__' attribute defines descriptions for enum members that also have description in '__schema__' attribute. (members: 'MEMBER')"

snapshots['test_enum_type_validation_fails_for_schema_and_members_enum_mismatch 1'] = "Class 'UserLevel' '__members__' is missing values for enum members defined in '__schema__'. (missing items: 'MODERATOR')"

snapshots['test_enum_type_validation_fails_for_schema_and_members_list 1'] = "Class 'UserLevel' '__members__' attribute can't be a list when used together with '__schema__'."

snapshots['test_enum_type_validation_fails_for_schema_invalid_members_descriptions 1'] = "Class 'UserLevel' '__members_descriptions__' attribute defines descriptions for undefined enum members. (undefined members: 'INVALID')"

snapshots['test_enum_type_validation_fails_for_two_descriptions 1'] = "Class 'UserLevel' defines description in both '__description__' and '__schema__' attributes."
