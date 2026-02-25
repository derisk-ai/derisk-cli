"""Common CLI decorators."""

import logging

import click


def setup_logging(level: str = "info") -> None:
    """Setup logging configuration."""
    log_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def verbose_option(f):
    """Add -v/-vv verbose option to a command/group with automatic logging setup.

    Usage:
        @click.group()
        @verbose_option
        @click.pass_context
        def my_cmd(ctx, verbose):
            pass
    """

    def callback(ctx, param, value):
        # Avoid setting up logging multiple times if parent already did it
        if hasattr(ctx, "obj") and ctx.obj and ctx.obj.get("_logging_setup"):
            return value

        if value == 1:
            setup_logging(level="info")
        elif value >= 2:
            setup_logging(level="debug")

        # Mark logging as set up
        if ctx.obj is None:
            ctx.obj = {}
        ctx.obj["_logging_setup"] = True
        ctx.obj["verbose"] = value
        return value

    return click.option(
        "-v",
        "--verbose",
        count=True,
        default=0,
        help="Verbose output (-v for info, -vv for debug)",
        callback=callback,
        is_eager=True,  # Process before other options
        expose_value=True,
    )(f)
