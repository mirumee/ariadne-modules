# pylint: disable=unused-variable
from unittest.mock import Mock

import pytest

from ariadne_graphql_modules import deferred
from ariadne_graphql_modules.deferredtype import (
    DeferredTypeData,
    _resolve_module_path_suffix,
)


def test_deferred_type_data():
    data = DeferredTypeData(path="some.module.path")
    assert data.path == "some.module.path"


def test_deferred_abs_path():
    deferred_type = deferred("tests.types")
    assert deferred_type.path == "tests.types"


def test_deferred_relative_path():
    class MockType:
        deferred_type = deferred(".types")

    assert MockType.deferred_type.path == "tests.types"


def test_deferred_returns_deferred_type_with_higher_level_relative_path(monkeypatch):
    frame_mock = Mock(f_globals={"__package__": "lorem.ipsum"})
    monkeypatch.setattr(
        "ariadne_graphql_modules.deferredtype.sys._getframe",
        Mock(return_value=frame_mock),
    )

    class MockType:
        deferred_type = deferred("..types")

    assert MockType.deferred_type.path == "lorem.types"


def test_deferred_raises_error_for_invalid_relative_path(monkeypatch, data_regression):
    frame_mock = Mock(f_globals={"__package__": "lorem"})
    monkeypatch.setattr(
        "ariadne_graphql_modules.deferredtype.sys._getframe",
        Mock(return_value=frame_mock),
    )

    with pytest.raises(ValueError) as exc_info:

        class MockType:
            deferred_type = deferred("...types")

    data_regression.check(str(exc_info.value))


def test_resolve_module_path_suffix():
    result = _resolve_module_path_suffix(".types", "current.package")
    assert result == "current.package.types"


def test_resolve_module_path_suffix_outside_package():
    with pytest.raises(ValueError):
        _resolve_module_path_suffix("...module", "current.package")
