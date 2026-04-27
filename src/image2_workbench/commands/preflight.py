# SPDX-License-Identifier: Apache-2.0
"""`i2w preflight` — pre-flight check before render.

Validates parameters and runs the moderation API as a cheap predictor that
the prompt would not be blocked. Exit codes mirror :mod:`errors`:

- 0 (OK):                 preflight passed
- 3 (MODERATION_BLOCKED): /v1/moderations flagged the prompt
- 4 (VALIDATION):         local parameter blockers
"""
from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from ..errors import ExitCode, moderation_blocked, validation_error
from ..runtimes.preflight import preflight as run_preflight


def _print_result(console: Console, result, prompt_file: Path) -> None:
    console.print(f"preflight for {prompt_file}", markup=False)
    console.print(f"  passed: {result.passed}", markup=False)
    console.print(
        f"  skipped_moderation: {result.skipped_moderation}", markup=False
    )
    if result.moderation_flagged:
        console.print(
            f"  moderation_flagged: True  categories={result.moderation_categories}",
            markup=False,
        )
    if result.blockers:
        console.print("  blockers:", markup=False)
        for code, msg in zip(result.blocker_codes, result.blockers, strict=False):
            console.print(f"    - [{code}] {msg}", markup=False)
    if result.warnings:
        console.print("  warnings:", markup=False)
        for warn in result.warnings:
            console.print(f"    - {warn}", markup=False)


def run(
    prompt_file: Annotated[
        Path, typer.Argument(help="Path to a rendered prompt markdown file")
    ],
    size: Annotated[str, typer.Option("--size")] = "1024x1024",
    quality: Annotated[str, typer.Option("--quality")] = "medium",
    background: Annotated[str, typer.Option("--background")] = "auto",
    output_format: Annotated[
        str, typer.Option("--format", help="png | jpeg | webp")
    ] = "png",
    output_compression: Annotated[
        int | None, typer.Option("--compression")
    ] = None,
    skip_moderation_api: Annotated[
        bool, typer.Option("--no-moderation-api")
    ] = False,
) -> None:
    """Read ``prompt_file``, run preflight, print the result.

    Exits 0 on success, 4 on local validation blockers, 3 on moderation
    blocks. The function writes a single concise summary to stdout.
    """
    console = Console()
    if not prompt_file.exists():
        envelope = validation_error(
            "prompt_file_missing",
            f"prompt file not found: {prompt_file}",
        ).envelope
        console.print(
            f"exit {int(envelope.exit_code)} ({envelope.exit_code.name}) "
            f"{envelope.code}: {envelope.message}",
            markup=False,
        )
        raise typer.Exit(code=int(ExitCode.VALIDATION))

    prompt = prompt_file.read_text(encoding="utf-8")
    result = run_preflight(
        prompt,
        size=size,
        quality=quality,
        background=background,
        output_format=output_format,
        output_compression=output_compression,
        skip_moderation_api=skip_moderation_api,
    )
    _print_result(console, result, prompt_file)

    if result.moderation_flagged:
        envelope = moderation_blocked(
            "prompt was flagged by /v1/moderations",
            context={"categories": result.moderation_categories},
        ).envelope
        console.print(
            f"exit {int(envelope.exit_code)} ({envelope.exit_code.name}) "
            f"{envelope.code}: {envelope.message}",
            markup=False,
        )
        raise typer.Exit(code=int(ExitCode.MODERATION_BLOCKED))

    if result.blockers:
        first_code = result.blocker_codes[0] if result.blocker_codes else "validation_failed"
        envelope = validation_error(
            first_code,
            result.blockers[0],
        ).envelope
        console.print(
            f"exit {int(envelope.exit_code)} ({envelope.exit_code.name}) "
            f"{envelope.code}: {envelope.message}",
            markup=False,
        )
        raise typer.Exit(code=int(ExitCode.VALIDATION))

    raise typer.Exit(code=int(ExitCode.OK))


# Build a Typer app whose root invokes ``run`` directly. Using a single
# command (not a TyperGroup) ensures positional + option parsing works even
# when no subcommand is supplied.
preflight_app = typer.Typer(
    name="preflight",
    help="Pre-flight check before render: validate parameters and pre-moderation.",
    add_completion=False,
)
preflight_app.command(name="run")(run)


# Convenience: also expose the run as the default callback so callers can do
# `preflight_app(["file.md"])` without the explicit `run` subcommand.
@preflight_app.callback(invoke_without_command=True)
def _default(ctx: typer.Context) -> None:
    """If no subcommand is supplied, fall back to printing help."""
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(code=0)
