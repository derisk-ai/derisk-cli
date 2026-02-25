"""MCP API client."""

from typing import Any, Dict, List, Optional

from openderisk_cli.client.base import OpenDeriskClient
from openderisk_cli.models.mcp import McpCreateRequest, McpServer, McpTool


class McpClient(OpenDeriskClient):
    """Client for MCP APIs."""

    def list_servers(
        self,
        page: int = 1,
        page_size: int = 20,
    ) -> List[McpServer]:
        """List MCP servers.

        Args:
            page: Page number
            page_size: Page size

        Returns:
            List of MCP servers
        """
        response = self.http_client.post(
            "/api/v1/serve/mcp/query_fuzzy",
            json={},
            params={"page": page, "page_size": page_size},
        )

        # Handle response structure
        if response.get("success") and "data" in response:
            data = response["data"]
            if isinstance(data, dict) and "items" in data:
                items = data["items"]
            else:
                items = data if isinstance(data, list) else []
        else:
            items = response if isinstance(response, list) else []

        return [McpServer(**item) for item in items]

    def get_server(self, mcp_code: str) -> Optional[McpServer]:
        """Get MCP server details.

        Args:
            mcp_code: MCP server code

        Returns:
            MCP server details
        """
        response = self.http_client.post(
            "/api/v1/serve/mcp/query",
            json={"mcp_code": mcp_code},
        )

        if response.get("success") and response.get("data"):
            return McpServer(**response["data"])
        return None

    def create_server(
        self,
        name: str,
        mcp_type: str = "sse",
        description: Optional[str] = None,
        sse_url: Optional[str] = None,
        stdio_cmd: Optional[str] = None,
        sse_headers: Optional[Dict[str, str]] = None,
        token: Optional[str] = None,
        author: Optional[str] = None,
        email: Optional[str] = None,
        version: Optional[str] = None,
        category: Optional[str] = None,
    ) -> McpServer:
        """Create MCP server.

        Args:
            name: MCP server name
            mcp_type: MCP type (sse or stdio)
            description: MCP description
            sse_url: SSE URL for SSE type
            stdio_cmd: Stdio command for stdio type
            sse_headers: SSE headers
            token: Token for authentication
            author: Author name
            email: Author email
            version: Version
            category: Category

        Returns:
            Created MCP server
        """
        request = McpCreateRequest(
            name=name,
            type=mcp_type,
            description=description,
            sse_url=sse_url,
            stdio_cmd=stdio_cmd,
            sse_headers=sse_headers,
            token=token,
            author=author,
            email=email,
            version=version,
            category=category,
        )

        response = self.http_client.post(
            "/api/v1/serve/mcp/create",
            json=request.model_dump(exclude_none=True),
        )

        if response.get("success") and response.get("data"):
            return McpServer(**response["data"])
        raise Exception(response.get("err_msg", "Failed to create MCP server"))

    def delete_server(self, mcp_code: str) -> bool:
        """Delete MCP server.

        Args:
            mcp_code: MCP server code

        Returns:
            True if deleted successfully
        """
        response = self.http_client.post(
            "/api/v1/serve/mcp/delete",
            json={"mcp_code": mcp_code},
        )
        return response.get("success", False)

    def list_tools(
        self,
        name: str,
        sse_url: Optional[str] = None,
        sse_headers: Optional[Dict[str, str]] = None,
    ) -> List[McpTool]:
        """List tools for MCP server.

        Args:
            name: MCP server name
            sse_url: SSE URL (optional)
            sse_headers: SSE headers (optional)

        Returns:
            List of MCP tools
        """
        request = {"name": name}
        if sse_url:
            request["sse_url"] = sse_url
        if sse_headers:
            request["sse_headers"] = sse_headers

        response = self.http_client.post(
            "/api/v1/serve/mcp/tool/list",
            json=request,
        )

        if response.get("success") and response.get("data"):
            items = response["data"]
            return [McpTool(**item) for item in items]
        return []

    def run_tool(
        self,
        name: str,
        tool_name: str,
        arguments: Optional[Dict[str, Any]] = None,
        sse_url: Optional[str] = None,
        sse_headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """Run MCP tool.

        Args:
            name: MCP server name
            tool_name: Tool name
            arguments: Tool arguments
            sse_url: SSE URL (optional)
            sse_headers: SSE headers (optional)

        Returns:
            Tool execution result
        """
        request = {
            "name": name,
            "params": {
                "name": tool_name,
                "arguments": arguments or {},
            },
        }
        if sse_url:
            request["sse_url"] = sse_url
        if sse_headers:
            request["sse_headers"] = sse_headers

        response = self.http_client.post(
            "/api/v1/serve/mcp/tool/run",
            json=request,
        )

        if response.get("success"):
            return response.get("data")
        raise Exception(response.get("err_msg", "Failed to run tool"))

    def fuzzy_search(
        self,
        filter_text: str,
        page: int = 1,
        page_size: int = 20,
    ) -> List[McpServer]:
        """Fuzzy search MCP servers.

        Args:
            filter_text: Filter text
            page: Page number
            page_size: Page size

        Returns:
            List of matching MCP servers
        """
        response = self.http_client.post(
            "/api/v1/serve/mcp/query_fuzzy",
            json={"filter": filter_text},
            params={"page": page, "page_size": page_size},
        )

        if response.get("success") and "data" in response:
            data = response["data"]
            if isinstance(data, dict) and "items" in data:
                items = data["items"]
            else:
                items = data if isinstance(data, list) else []
        else:
            items = []

        return [McpServer(**item) for item in items]
