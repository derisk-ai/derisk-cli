"""Configuration management for OpenDerisk CLI."""

import os
from pathlib import Path
from typing import Any, Optional

import yaml
from pydantic import BaseModel, Field


class ApiConfig(BaseModel):
    """API configuration."""

    base_url: str = "http://localhost:7777"
    timeout: int = 30
    retry_max_attempts: int = 3
    retry_backoff_factor: float = 0.5


class DefaultsConfig(BaseModel):
    """Default settings."""

    output_format: str = "table"


class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: str = "info"
    file: str = "~/.openderisk/logs/openderisk-cli.log"
    max_size: str = "10MB"
    max_files: int = 5


class OpenDeriskConfig(BaseModel):
    """Main configuration class."""

    version: str = "1.0"
    api: ApiConfig = Field(default_factory=ApiConfig)
    defaults: DefaultsConfig = Field(default_factory=DefaultsConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "OpenDeriskConfig":
        """Load configuration from file.

        Args:
            config_path: Explicit configuration file path.
                        If not provided, searches in default locations.

        Returns:
            OpenDeriskConfig instance
        """
        if config_path:
            if config_path.exists():
                return cls._load_from_file(config_path)
            return cls()

        # Search in default locations
        search_paths = [
            Path(".openderisk/config.yaml"),
            Path(".openderisk/config.yml"),
            Path.home() / ".openderisk/config.yaml",
            Path.home() / ".openderisk/config.yml",
        ]

        for path in search_paths:
            if path.exists():
                return cls._load_from_file(path)

        # Return default configuration
        return cls()

    @classmethod
    def _load_from_file(cls, path: Path) -> "OpenDeriskConfig":
        """Load configuration from YAML file."""
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return cls(**data)

    def save(self, path: Optional[Path] = None, global_config: bool = False) -> None:
        """Save configuration to file.

        Args:
            path: Explicit configuration file path.
            global_config: If True, save to global config location.
        """
        if path is None:
            if global_config:
                path = Path.home() / ".openderisk/config.yaml"
            else:
                path = Path(".openderisk/config.yaml")

        # Ensure directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(self.model_dump(), f, default_flow_style=False, sort_keys=False)

    def get_env_overrides(self) -> None:
        """Apply environment variable overrides."""
        if base_url := os.getenv("OPENDERISK_BASE_URL"):
            self.api.base_url = base_url
        if timeout := os.getenv("OPENDERISK_TIMEOUT"):
            self.api.timeout = int(timeout)
        if output_format := os.getenv("OPENDERISK_OUTPUT_FORMAT"):
            self.defaults.output_format = output_format

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation key.

        Args:
            key: Dot-notation key (e.g., 'api.base_url')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split(".")
        value = self.model_dump()
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any) -> None:
        """Set configuration value by dot-notation key.

        Args:
            key: Dot-notation key (e.g., 'api.base_url')
            value: Value to set
        """
        keys = key.split(".")
        current = self
        for k in keys[:-1]:
            current = getattr(current, k)
        setattr(current, keys[-1], value)


def get_config(config_path: Optional[Path] = None) -> OpenDeriskConfig:
    """Get configuration instance with environment overrides applied.

    Args:
        config_path: Optional explicit configuration file path.

    Returns:
        OpenDeriskConfig instance
    """
    config = OpenDeriskConfig.load(config_path)
    config.get_env_overrides()
    return config
