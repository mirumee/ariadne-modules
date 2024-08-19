from pathlib import Path
import pytest


@pytest.fixture(scope="session")
def datadir() -> Path:
    return Path(__file__).parent / "snapshots"


@pytest.fixture(scope="session")
def original_datadir() -> Path:
    return Path(__file__).parent / "snapshots"
