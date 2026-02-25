"""Config CLI commands."""

import sys
from pathlib import Path

import click
from rich.console import Console

from openderisk_cli.config import OpenDeriskConfig, get_config
from openderisk_cli.exceptions import ConfigError
from openderisk_cli.utils.output import format_output

console = Console()
console_err = Console(stderr=True)


@click.group()
def config_cmd():
    """Configuration management commands."""
    pass


@config_cmd.command()
@click.option("--base-url", help="OpenDerisk platform base URL")
@click.option("--global", "global_config", is_flag=True, help="Create global config")
def init(base_url: str, global_config: bool):
    """Initialize configuration file.

    Examples:
        openderisk config init
        openderisk config init --base-url http://localhost:7777
        openderisk config init --global
    """
    config = OpenDeriskConfig()

    if base_url:
        config.api.base_url = base_url

    try:
        config.save(global_config=global_config)
        path = (
            Path.home() / ".openderisk/config.yaml"
            if global_config
            else Path(".openderisk/config.yaml")
        )
        console.print(f"[green]✓[/green] Configuration created at: {path}")
    except Exception as e:
        console_err.print(f"[red]Error:[/red] Failed to create configuration: {e}")
        sys.exit(1)


@config_cmd.command()
@click.option(
    "--format", "output_format", default="table", type=click.Choice(["table", "json", "yaml"])
)
def show(output_format: str):
    """Show current configuration.

    Examples:
        openderisk config show
        openderisk config show --format json
    """
    try:
        config = get_config()

        # Convert config to dict for display
        config_dict = config.model_dump()

        if output_format == "yaml":
            console.print(format_output(config_dict, "yaml"))
        elif output_format == "json":
            console.print(format_output(config_dict, "json"))
        else:
            console.print("[bold]API Configuration:[/bold]")
            console.print(f"  Base URL: {config.api.base_url}")
            console.print(f"  Timeout: {config.api.timeout}")

            console.print("\n[bold]Defaults:[/bold]")
            console.print(f"  Output Format: {config.defaults.output_format}")

    except Exception as e:
        console_err.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@config_cmd.command()
@click.argument("key")
@click.argument("value")
@click.option("--global", "global_config", is_flag=True, help="Set in global config")
def set(key: str, value: str, global_config: bool):
    """Set configuration value.

    Examples:
        openderisk config set api.base_url http://localhost:7777
        openderisk config set api.timeout 60 --global
    """
    # Load existing config
    if global_config:
        config_path = Path.home() / ".openderisk/config.yaml"
    else:
        config_path = Path(".openderisk/config.yaml")

    try:
        if config_path.exists():
            config = OpenDeriskConfig.load(config_path)
        else:
            config = OpenDeriskConfig()

        # Parse value
        parsed_value = _parse_config_value(value)

        # Set value
        config.set(key, parsed_value)

        # Save
        config.save(path=config_path)
        console.print(f"[green]✓[/green] Set {key} = {parsed_value}")

    except ConfigError as e:
        console_err.print(f"[red]Error:[/red] {e.message}")
        sys.exit(1)


@config_cmd.command()
@click.argument("key")
def get(key: str):
    """Get configuration value.

    Examples:
        openderisk config get api.base_url
    """
    try:
        config = get_config()
        value = config.get(key)

        if value is None:
            console_err.print(f"[yellow]Key '{key}' not found[/yellow]")
            sys.exit(1)

        console.print(value)

    except Exception as e:
        console_err.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


def _parse_config_value(value: str):
    """Parse configuration value to appropriate type."""
    # Try integer
    try:
        return int(value)
    except ValueError:
        pass

    # Try float
    try:
        return float(value)
    except ValueError:
        pass

    # Try boolean
    if value.lower() in ("true", "yes", "1"):
        return True
    if value.lower() in ("false", "no", "0"):
        return False

    # Return as string
    return value
