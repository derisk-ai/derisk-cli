"""Tests for configuration management."""

from pathlib import Path

import pytest

from openderisk_cli.config import (
    ApiConfig,
    DefaultsConfig,
    LoggingConfig,
    OpenDeriskConfig,
    get_config,
)


class TestApiConfig:
    """Tests for ApiConfig."""

    def test_default_values(self) -> None:
        """Test default API configuration values."""
        config = ApiConfig()
        assert config.base_url == "http://localhost:7777"
        assert config.timeout == 30
        assert config.retry_max_attempts == 3
        assert config.retry_backoff_factor == 0.5

    def test_custom_values(self) -> None:
        """Test custom API configuration values."""
        config = ApiConfig(
            base_url="https://api.example.com",
            timeout=60,
            retry_max_attempts=5,
        )
        assert config.base_url == "https://api.example.com"
        assert config.timeout == 60
        assert config.retry_max_attempts == 5


class TestDefaultsConfig:
    """Tests for DefaultsConfig."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = DefaultsConfig()
        assert config.output_format == "table"


class TestLoggingConfig:
    """Tests for LoggingConfig."""

    def test_default_values(self) -> None:
        """Test default logging configuration values."""
        config = LoggingConfig()
        assert config.level == "info"
        assert "openderisk-cli.log" in config.file
        assert config.max_size == "10MB"
        assert config.max_files == 5


class TestOpenDeriskConfig:
    """Tests for OpenDeriskConfig."""

    def test_default_values(self, sample_config: OpenDeriskConfig) -> None:
        """Test default configuration values."""
        assert sample_config.version == "1.0"
        assert isinstance(sample_config.api, ApiConfig)
        assert isinstance(sample_config.defaults, DefaultsConfig)
        assert isinstance(sample_config.logging, LoggingConfig)

    def test_get_nested_value(self, sample_config: OpenDeriskConfig) -> None:
        """Test getting nested configuration values."""
        assert sample_config.get("api.base_url") == "http://localhost:7777"
        assert sample_config.get("api.timeout") == 30
        assert sample_config.get("defaults.output_format") == "table"
        assert sample_config.get("logging.level") == "info"

    def test_get_missing_value_with_default(self, sample_config: OpenDeriskConfig) -> None:
        """Test getting missing configuration values with default."""
        assert sample_config.get("nonexistent.key", "default") == "default"
        assert sample_config.get("api.nonexistent", 123) == 123

    def test_set_nested_value(self, sample_config: OpenDeriskConfig) -> None:
        """Test setting nested configuration values."""
        sample_config.set("api.base_url", "https://new.example.com")
        assert sample_config.api.base_url == "https://new.example.com"

        sample_config.set("api.timeout", 120)
        assert sample_config.api.timeout == 120

        sample_config.set("defaults.output_format", "json")
        assert sample_config.defaults.output_format == "json"

    def test_load_nonexistent_file(self) -> None:
        """Test loading configuration from nonexistent file returns defaults."""
        config = OpenDeriskConfig.load(Path("/nonexistent/path/config.yaml"))
        assert config.version == "1.0"
        assert config.api.base_url == "http://localhost:7777"

    def test_save_and_load(self, temp_config_file: Path) -> None:
        """Test saving and loading configuration."""
        config = OpenDeriskConfig()
        config.set("api.base_url", "https://saved.example.com")
        config.set("api.timeout", 45)

        config.save(temp_config_file)

        loaded_config = OpenDeriskConfig.load(temp_config_file)
        assert loaded_config.api.base_url == "https://saved.example.com"
        assert loaded_config.api.timeout == 45

    def test_model_dump(self, sample_config: OpenDeriskConfig) -> None:
        """Test model_dump returns correct dictionary."""
        data = sample_config.model_dump()
        assert "version" in data
        assert "api" in data
        assert "defaults" in data
        assert "logging" in data
        assert isinstance(data["api"], dict)


class TestGetConfig:
    """Tests for get_config function."""

    def test_returns_config_instance(self) -> None:
        """Test that get_config returns OpenDeriskConfig instance."""
        config = get_config()
        assert isinstance(config, OpenDeriskConfig)

    def test_with_custom_path(self, temp_config_file: Path) -> None:
        """Test get_config with custom path."""
        config = OpenDeriskConfig()
        config.set("api.base_url", "https://custom.example.com")
        config.save(temp_config_file)

        loaded_config = get_config(temp_config_file)
        assert loaded_config.api.base_url == "https://custom.example.com"

    def test_env_override_base_url(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test environment variable override for base URL."""
        monkeypatch.setenv("OPENDERISK_BASE_URL", "https://env.example.com")
        config = get_config()
        assert config.api.base_url == "https://env.example.com"

    def test_env_override_timeout(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test environment variable override for timeout."""
        monkeypatch.setenv("OPENDERISK_TIMEOUT", "90")
        config = get_config()
        assert config.api.timeout == 90

    def test_env_override_output_format(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test environment variable override for output format."""
        monkeypatch.setenv("OPENDERISK_OUTPUT_FORMAT", "json")
        config = get_config()
        assert config.defaults.output_format == "json"
