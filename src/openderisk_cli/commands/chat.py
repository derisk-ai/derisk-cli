"""Chat CLI commands."""

import sys
from typing import Optional

import click
from rich.console import Console

from openderisk_cli.client.chat import ChatClient
from openderisk_cli.config import get_config
from openderisk_cli.exceptions import OpenDeriskError
from openderisk_cli.utils.decorators import verbose_option
from openderisk_cli.utils.output import format_output

console = Console()
console_err = Console(stderr=True)


def get_chat_client() -> ChatClient:
    """Get chat client."""
    config = get_config()
    return ChatClient.from_config(config)


@click.group()
def chat():
    """Chat management commands."""
    pass


@chat.command()
@click.argument("message")
@click.option("--conv", "-c", "conv_uid", help="Conversation UID (continue existing conversation)")
@click.option("--model", "-m", "model_name", help="Model name")
@click.option("--app", "-a", "app_code", help="App code")
@click.option("--timeout", "-t", default=300, help="Timeout in seconds (default: 300)")
@verbose_option
@click.pass_context
def send(
    ctx,
    verbose: int,
    message: str,
    conv_uid: Optional[str],
    model_name: Optional[str],
    app_code: Optional[str],
    timeout: int,
):
    """Send a message and stream the response.

    Examples:
        openderisk chat "Hello, how are you?"
        openderisk chat -c conv-xxx "Continue our conversation"
        openderisk chat -m gpt-4 "Use a specific model"
    """
    try:
        client = get_chat_client()

        with console.status("[bold green]Waiting for response...[/bold green]", spinner="dots"):
            result = client.chat_async(
                user_input=message,
                conv_uid=conv_uid,
                app_code=app_code,
                model_name=model_name,
                timeout=timeout,
            )

        console.print(result)

    except OpenDeriskError as e:
        console_err.print(f"[red]Error:[/red] {e.message}")
        if e.suggestion:
            console_err.print(f"[dim]Suggestion: {e.suggestion}[/dim]")
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted[/yellow]")
        sys.exit(130)


@chat.command("list")
@click.option(
    "--format", "output_format", default="table", type=click.Choice(["table", "json", "yaml"])
)
@click.option("--page", "-p", default=1, help="Page number")
@click.option("--page-size", "-s", default=20, help="Page size")
@click.option("--user", "-u", "user_name", help="User name")
@verbose_option
@click.pass_context
def list_conversations(
    ctx, verbose: int, output_format: str, page: int, page_size: int, user_name: Optional[str]
):
    """List conversations.

    Examples:
        openderisk chat list
        openderisk chat list --format json
        openderisk chat list -u myuser
    """
    try:
        client = get_chat_client()
        conversations = client.list_conversations(
            user_name=user_name,
            page=page,
            page_size=page_size,
        )

        if not conversations:
            console.print("[yellow]No conversations found.[/yellow]")
            return

        # Convert to dict for output
        convs_data = [conv.model_dump() for conv in conversations]

        console.print(
            format_output(
                convs_data,
                output_format,
                columns=["conv_uid", "user_input", "app_code", "gmt_created"],
                headers={
                    "conv_uid": "Conv UID",
                    "user_input": "User Input",
                    "app_code": "App Code",
                    "gmt_created": "Created",
                },
            )
        )
    except OpenDeriskError as e:
        console_err.print(f"[red]Error:[/red] {e.message}")
        sys.exit(1)


@chat.command()
@click.argument("conv_uid")
@click.confirmation_option(prompt="Are you sure you want to delete this conversation?")
@verbose_option
@click.pass_context
def delete(ctx, verbose: int, conv_uid: str):
    """Delete conversation.

    Examples:
        openderisk chat delete conv-xxx
    """
    try:
        client = get_chat_client()
        success = client.delete_conversation(conv_uid)

        if success:
            console.print(f"[green]✓[/green] Deleted conversation: {conv_uid}")
        else:
            console.print(f"[yellow]Warning:[/yellow] Failed to delete conversation: {conv_uid}")

    except OpenDeriskError as e:
        console_err.print(f"[red]Error:[/red] {e.message}")
        sys.exit(1)


@chat.command("models")
@click.option(
    "--format", "output_format", default="table", type=click.Choice(["table", "json", "yaml"])
)
@verbose_option
@click.pass_context
def list_models(ctx, verbose: int, output_format: str):
    """List available models.

    Examples:
        openderisk chat models
        openderisk chat models --format json
    """
    try:
        client = get_chat_client()
        models = client.list_models()

        if not models:
            console.print("[yellow]No models available.[/yellow]")
            return

        models_data = [{"name": model.model_name} for model in models]

        console.print(
            format_output(
                models_data, output_format, columns=["name"], headers={"name": "Model Name"}
            )
        )
    except OpenDeriskError as e:
        console_err.print(f"[red]Error:[/red] {e.message}")
        sys.exit(1)
