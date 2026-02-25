"""MCP CLI commands."""

import json
import sys
from typing import Optional

import click
from rich.console import Console

from openderisk_cli.client.mcp import McpClient
from openderisk_cli.config import get_config
from openderisk_cli.exceptions import OpenDeriskError
from openderisk_cli.utils.decorators import verbose_option
from openderisk_cli.utils.output import format_output

console = Console()
console_err = Console(stderr=True)


def get_mcp_client() -> McpClient:
    """Get MCP client."""
    config = get_config()
    return McpClient.from_config(config)


@click.group()
def mcp():
    """MCP management commands."""
    pass


@mcp.command("list")
@click.option(
    "--format", "output_format", default="table", type=click.Choice(["table", "json", "yaml"])
)
@click.option("--page", "-p", default=1, help="Page number")
@click.option("--page-size", "-s", default=20, help="Page size")
@verbose_option
@click.pass_context
def list_servers(ctx, verbose: int, output_format: str, page: int, page_size: int):
    """List MCP servers.

    Examples:
        openderisk mcp list
        openderisk mcp list --format json
        openderisk mcp list -p 2 -s 10
    """
    try:
        client = get_mcp_client()
        servers = client.list_servers(page=page, page_size=page_size)

        if not servers:
            console.print("[yellow]No MCP servers found.[/yellow]")
            return

        # Convert to dict for output
        servers_data = [server.model_dump() for server in servers]

        console.print(
            format_output(
                servers_data,
                output_format,
                columns=["mcp_code", "name", "type", "description", "available"],
                headers={
                    "mcp_code": "MCP Code",
                    "name": "Name",
                    "type": "Type",
                    "description": "Description",
                    "available": "Available",
                },
            )
        )
    except OpenDeriskError as e:
        console_err.print(f"[red]Error:[/red] {e.message}")
        if e.suggestion:
            console_err.print(f"[dim]Suggestion: {e.suggestion}[/dim]")
        sys.exit(1)


@mcp.command()
@click.option("--name", "-n", required=True, help="MCP server name")
@click.option(
    "--type", "-t", "mcp_type", default="sse", type=click.Choice(["sse", "stdio"]), help="MCP type"
)
@click.option("--description", "-d", help="MCP description")
@click.option("--sse-url", help="SSE URL (for SSE type)")
@click.option("--stdio-cmd", help="Stdio command (for stdio type)")
@click.option("--sse-headers", help="SSE headers as JSON string")
@click.option("--token", help="Token for authentication")
@click.option("--author", help="Author name")
@click.option("--email", help="Author email")
@click.option("--version", help="Version")
@click.option("--category", help="Category")
@verbose_option
@click.pass_context
def create(
    ctx,
    verbose: int,
    name: str,
    mcp_type: str,
    description: Optional[str],
    sse_url: Optional[str],
    stdio_cmd: Optional[str],
    sse_headers: Optional[str],
    token: Optional[str],
    author: Optional[str],
    email: Optional[str],
    version: Optional[str],
    category: Optional[str],
):
    """Create MCP server.

    Examples:
        openderisk mcp create --name my-mcp --sse-url http://localhost:8080/sse
        openderisk mcp create -n my-mcp -t stdio --stdio-cmd "python server.py"
    """
    try:
        client = get_mcp_client()

        # Parse sse_headers if provided
        headers_dict = None
        if sse_headers:
            headers_dict = json.loads(sse_headers)

        server = client.create_server(
            name=name,
            mcp_type=mcp_type,
            description=description,
            sse_url=sse_url,
            stdio_cmd=stdio_cmd,
            sse_headers=headers_dict,
            token=token,
            author=author,
            email=email,
            version=version,
            category=category,
        )

        console.print(f"[green]✓[/green] Created MCP server: {server.name}")
        console.print(f"  MCP Code: {server.mcp_code}")
        if server.description:
            console.print(f"  Description: {server.description}")

    except json.JSONDecodeError as e:
        console_err.print(f"[red]Error:[/red] Invalid JSON for sse-headers: {e}")
        sys.exit(1)
    except OpenDeriskError as e:
        console_err.print(f"[red]Error:[/red] {e.message}")
        sys.exit(1)


@mcp.command()
@click.argument("mcp_code")
@verbose_option
@click.pass_context
def delete(ctx, verbose: int, mcp_code: str):
    """Delete MCP server.

    Examples:
        openderisk mcp delete mcp-xxx
    """
    try:
        client = get_mcp_client()
        success = client.delete_server(mcp_code)

        if success:
            console.print(f"[green]✓[/green] Deleted MCP server: {mcp_code}")
        else:
            console.print(f"[yellow]Warning:[/yellow] Failed to delete MCP server: {mcp_code}")

    except OpenDeriskError as e:
        console_err.print(f"[red]Error:[/red] {e.message}")
        sys.exit(1)


@mcp.command()
@click.argument("name")
@verbose_option
@click.pass_context
def tools(ctx, verbose: int, name: str):
    """List tools for MCP server.

    Examples:
        openderisk mcp tools my-mcp
    """
    try:
        client = get_mcp_client()
        tools_list = client.list_tools(name=name)

        if not tools_list:
            console.print(f"[yellow]No tools found for MCP server: {name}[/yellow]")
            return

        tools_data = [tool.model_dump() for tool in tools_list]

        console.print(
            format_output(
                tools_data,
                "table",
                columns=["name", "description"],
                headers={
                    "name": "Tool Name",
                    "description": "Description",
                },
            )
        )

    except OpenDeriskError as e:
        console_err.print(f"[red]Error:[/red] {e.message}")
        sys.exit(1)


@mcp.command("exec")
@click.option("--mcp-name", "-m", required=True, help="MCP server name")
@click.option("--tool-name", "-t", required=True, help="Tool name")
@click.option("--params", "-p", help="Tool parameters as JSON string")
@click.option("--params-file", type=click.Path(exists=True), help="Parameters file (JSON)")
@verbose_option
@click.pass_context
def exec_tool(
    ctx,
    verbose: int,
    mcp_name: str,
    tool_name: str,
    params: Optional[str],
    params_file: Optional[str],
):
    """Execute MCP tool.

    Examples:
        openderisk mcp exec -m my-mcp -t my_tool -p '{"arg": "value"}'
        openderisk mcp exec -m my-mcp -t my_tool --params-file params.json
    """
    try:
        client = get_mcp_client()

        # Get parameters
        tool_params = {}
        if params_file:
            with open(params_file, "r") as f:
                tool_params = json.load(f)
        elif params:
            tool_params = json.loads(params)

        result = client.run_tool(
            name=mcp_name,
            tool_name=tool_name,
            arguments=tool_params,
        )

        console.print("[green]✓[/green] Success")
        if result:
            console.print(format_output(result, "json"))

    except json.JSONDecodeError as e:
        console_err.print(f"[red]Error:[/red] Invalid JSON parameters: {e}")
        sys.exit(1)
    except OpenDeriskError as e:
        console_err.print(f"[red]Error:[/red] {e.message}")
        sys.exit(1)
