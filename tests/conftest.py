"""Pytest fixtures for OpenDerisk CLI tests."""

import os
import tempfile
from pathlib import Path
from typing import Generator

import pytest

from openderisk_cli.config import OpenDeriskConfig


@pytest.fixture
def sample_config() -> OpenDeriskConfig:
    """Create a sample configuration for testing."""
    return OpenDeriskConfig()


@pytest.fixture
def temp_config_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for config files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_config_file(temp_config_dir: Path) -> Path:
    """Create a temporary config file path."""
    return temp_config_dir / ".openderisk" / "config.yaml"


@pytest.fixture
def clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Clean environment variables that affect config."""
    env_vars = [
        "OPENDERISK_BASE_URL",
        "OPENDERISK_TIMEOUT",
        "OPENDERISK_OUTPUT_FORMAT",
    ]
    for var in env_vars:
        monkeypatch.delenv(var, raising=False)
