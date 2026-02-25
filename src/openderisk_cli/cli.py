"""Main CLI entry point for OpenDerisk CLI."""

import sys
from pathlib import Path

import click
from rich.console import Console

from openderisk_cli import __version__
from openderisk_cli.commands.agent import agent
from openderisk_cli.commands.chat import chat
from openderisk_cli.commands.config import config_cmd
from openderisk_cli.commands.mcp import mcp
from openderisk_cli.config import get_config
from openderisk_cli.exceptions import OpenDeriskError

console = Console()
console_err = Console(stderr=True)


@click.group()
@click.version_option(version=__version__, prog_name="openderisk")
@click.option(
    "--config", "config_path", type=click.Path(exists=True), help="Path to configuration file"
)
@click.option("--base-url", help="OpenDerisk platform base URL (overrides config)")
@click.option(
    "--output-format",
    "output_format",
    type=click.Choice(["table", "json", "yaml"]),
    help="Output format (overrides config)",
)
@click.pass_context
def cli(ctx, config_path, base_url, output_format):
    """OpenDerisk CLI - Command line tool for OpenDerisk platform.

    Use this tool to manage MCP servers, have conversations with AI models,
    and manage configurations on the OpenDerisk platform.

    \b
    Examples:
        openderisk chat "Hello, how are you?"
        openderisk mcp list
        openderisk config show
    """
    # Ensure context object exists
    if ctx.obj is None:
        ctx.obj = {}

    # Load configuration
    try:
        config = get_config(Path(config_path) if config_path else None)

        # Apply CLI overrides
        if base_url:
            config.api.base_url = base_url
        if output_format:
            config.defaults.output_format = output_format

        ctx.obj["config"] = config

    except Exception as e:
        console_err.print(f"[red]Error loading configuration:[/red] {e}")
        sys.exit(1)


# Register command groups
cli.add_command(agent)
cli.add_command(chat)
cli.add_command(mcp)
cli.add_command(config_cmd, name="config")


def main():
    """Main entry point."""
    try:
        cli()
    except OpenDeriskError as e:
        console_err.print(f"[red]Error:[/red] {e.message}")
        if e.details:
            console_err.print(f"  Details: {e.details}")
        if e.suggestion:
            console_err.print(f"  [dim]Suggestion: {e.suggestion}[/dim]")
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted[/yellow]")
        sys.exit(130)
    except Exception as e:
        console_err.print(f"[red]Unexpected error:[/red] {e}")
        if "--verbose" in sys.argv or "-v" in sys.argv:
            import traceback

            console_err.print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
