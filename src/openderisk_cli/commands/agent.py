"""Agent CLI commands (simplified version)."""

import sys

import click
from rich.console import Console

from openderisk_cli.client.agent import AgentClient
from openderisk_cli.config import get_config
from openderisk_cli.exceptions import OpenDeriskError
from openderisk_cli.utils.decorators import verbose_option
from openderisk_cli.utils.output import format_output

console = Console()
console_err = Console(stderr=True)


def get_agent_client() -> AgentClient:
    """Get agent client."""
    config = get_config()
    return AgentClient.from_config(config)


@click.group()
def agent():
    """Agent management commands.

    Manage agent instances (apps) in OpenDerisk.
    """
    pass


@agent.command("list")
@click.option(
    "--format", "output_format", default="table", type=click.Choice(["table", "json", "yaml"])
)
@verbose_option
@click.pass_context
def list_agents(ctx, verbose: int, output_format: str):
    """List available agent instances.

    Examples:
        openderisk agent list
        openderisk agent list --format json
    """
    try:
        client = get_agent_client()
        response = client.list_apps()

        if not response.app_list:
            console.print("[yellow]No agents available.[/yellow]")
            return

        # Convert to list of dicts for output
        apps_data = [
            {
                "app_code": app.app_code or "",
                "app_name": app.app_name or "",
                "app_describe": app.app_describe or "",
                "team_mode": app.team_mode or "",
                "published": "Yes" if app.published else "No",
            }
            for app in response.app_list
        ]

        console.print(
            format_output(
                apps_data,
                output_format,
                columns=["app_code", "app_name", "app_describe", "team_mode", "published"],
                headers={
                    "app_code": "App Code",
                    "app_name": "Name",
                    "app_describe": "Description",
                    "team_mode": "Team Mode",
                    "published": "Published",
                },
            )
        )
    except OpenDeriskError as e:
        console_err.print(f"[red]Error:[/red] {e.message}")
        sys.exit(1)
