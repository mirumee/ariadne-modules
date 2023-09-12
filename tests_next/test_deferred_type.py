import pytest

from ariadne_graphql_modules.next import deferred


def test_deferred_returns_deferred_type_with_abs_path():
    deferred_type = deferred("tests_next.types")
    assert deferred_type.path == "tests_next.types"


def test_deferred_returns_deferred_type_with_relative_path():
    class MockType:
        deferred_type = deferred(".types")

    assert MockType.deferred_type.path == "tests_next.types"
