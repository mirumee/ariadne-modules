from unittest.mock import Mock

import pytest

from ariadne_graphql_modules.next import deferred


def test_deferred_returns_deferred_type_with_abs_path():
    deferred_type = deferred("tests_next.types")
    assert deferred_type.path == "tests_next.types"


def test_deferred_returns_deferred_type_with_relative_path():
    class MockType:
        deferred_type = deferred(".types")

    assert MockType.deferred_type.path == "tests_next.types"


def test_deferred_returns_deferred_type_with_higher_level_relative_path(monkeypatch):
    frame_mock = Mock(f_globals={"__package__": "lorem.ipsum"})
    monkeypatch.setattr(
        "ariadne_graphql_modules.next.deferredtype.sys._getframe",
        Mock(return_value=frame_mock),
    )

    class MockType:
        deferred_type = deferred("..types")

    assert MockType.deferred_type.path == "lorem.types"


def test_deferred_raises_error_for_invalid_relative_path(monkeypatch, snapshot):
    frame_mock = Mock(f_globals={"__package__": "lorem"})
    monkeypatch.setattr(
        "ariadne_graphql_modules.next.deferredtype.sys._getframe",
        Mock(return_value=frame_mock),
    )

    with pytest.raises(ValueError) as exc_info:

        class MockType:
            deferred_type = deferred("...types")

    snapshot.assert_match(str(exc_info.value))
