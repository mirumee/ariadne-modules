# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_interface_no_interface_in_schema 1'] = "Unknown type 'BaseInterface'."

snapshots['test_interface_with_different_types 1'] = '''Query root type must be provided.

Interface field UserInterface.score expects type String! but User.score is type Int!.'''
