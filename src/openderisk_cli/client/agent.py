"""Agent API client."""

from openderisk_cli.client.base import OpenDeriskClient
from openderisk_cli.models.app import GptsAppResponse


class AgentClient(OpenDeriskClient):
    """Client for Agent APIs."""

    def list_apps(
        self,
        page: int = 1,
        page_size: int = 100,
    ) -> GptsAppResponse:
        """Get list of apps (agent instances).

        Args:
            page: Page number
            page_size: Page size

        Returns:
            GptsAppResponse with app list
        """
        response = self.http_client.post(
            "/api/v1/app/list",
            json={"page": page, "page_size": page_size, "ignore_user": "true"},
        )

        if response.get("success") and response.get("data"):
            return GptsAppResponse(**response["data"])
        return GptsAppResponse()
