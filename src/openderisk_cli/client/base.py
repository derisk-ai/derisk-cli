"""Base client for OpenDerisk API."""

from typing import Optional

from openderisk_cli.client.http import OpenDeriskHttpClient
from openderisk_cli.config import OpenDeriskConfig


class OpenDeriskClient:
    """Base client for OpenDerisk APIs.

    Note: OpenDerisk does not require authentication.
    """

    def __init__(
        self,
        http_client: OpenDeriskHttpClient,
        config: OpenDeriskConfig,
    ):
        self.http_client = http_client
        self.config = config

    @classmethod
    def from_config(
        cls,
        config: OpenDeriskConfig,
    ) -> "OpenDeriskClient":
        """Create client from config.

        Args:
            config: Configuration object

        Returns:
            Configured OpenDeriskClient
        """
        # Use config base_url
        base_url = config.api.base_url

        http_client = OpenDeriskHttpClient(
            base_url=base_url,
            timeout=config.api.timeout,
            config=config,
        )
        return cls(http_client, config)
