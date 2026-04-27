# SPDX-License-Identifier: Apache-2.0
"""`i2w preflight` — validate a prompt before render.

The public CLI supports both forms:

- ``i2w preflight prompt.md``
- ``i2w preflight run prompt.md`` (legacy-compatible)
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from ..errors import WorkbenchError, cli_dispatch, moderation_blocked, validation_error
from ..ledger import LedgerEntry, append_entry
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


def _append_ledger(entry: LedgerEntry) -> None:
    try:
        append_entry(entry)
    except Exception:  # noqa: BLE001
        pass


def _normalize_prompt_file(
    ctx: typer.Context,
    prompt_file: Path | None,
) -> Path:
    args = [str(arg) for arg in ctx.args]
    if prompt_file is not None and str(prompt_file) == "run":
        if not args:
            raise validation_error(
                "prompt_file_missing",
                "i2w preflight run requires a prompt file",
            )
        prompt_file = Path(args.pop(0))
    if args:
        raise validation_error(
            "unexpected_args",
            "unexpected positional arguments: " + " ".join(args),
            context={"args": args},
        )
    if prompt_file is None:
        raise validation_error(
            "prompt_file_missing",
            "i2w preflight requires a prompt file",
        )
    return prompt_file


def preflight_command(
    ctx: typer.Context,
    prompt_file: Annotated[
        Path | None,
        typer.Argument(help="Path to a rendered prompt markdown file"),
    ] = None,
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
    template_id: Annotated[
        str | None,
        typer.Option("--template-id", help="Template id for ledger grouping"),
    ] = None,
    input_fidelity: Annotated[
        str | None,
        typer.Option(
            "--input-fidelity",
            help="Rejected for gpt-image-2; included for preflight diagnostics",
        ),
    ] = None,
) -> None:
    """Read a prompt file, run local checks plus optional moderation, exit clearly."""
    console = Console()

    def _run() -> None:
        start = time.monotonic()
        resolved_prompt_file: Path | None = None
        try:
            resolved_prompt_file = _normalize_prompt_file(ctx, prompt_file)
            if not resolved_prompt_file.exists():
                raise validation_error(
                    "prompt_file_missing",
                    f"prompt file not found: {resolved_prompt_file}",
                    context={"prompt_file": str(resolved_prompt_file)},
                )
            prompt = resolved_prompt_file.read_text(encoding="utf-8")
            extra_params = (
                {"input_fidelity": input_fidelity}
                if input_fidelity is not None
                else None
            )
            result = run_preflight(
                prompt,
                size=size,
                quality=quality,
                background=background,
                output_format=output_format,
                output_compression=output_compression,
                extra_params=extra_params,
                skip_moderation_api=skip_moderation_api,
            )
            _print_result(console, result, resolved_prompt_file)

            if result.moderation_flagged:
                raise moderation_blocked(
                    "prompt was flagged by /v1/moderations",
                    context={"categories": result.moderation_categories},
                )
            if result.blockers:
                first_code = (
                    result.blocker_codes[0]
                    if result.blocker_codes
                    else "validation_failed"
                )
                raise validation_error(
                    first_code,
                    result.blockers[0],
                    context={
                        "blocker_codes": result.blocker_codes,
                        "blockers": result.blockers,
                    },
                )

            _append_ledger(
                LedgerEntry(
                    kind="preflight",
                    template_id=template_id,
                    status="ok",
                    latency_ms=int((time.monotonic() - start) * 1000),
                    size=size,
                    quality=quality,
                    n=1,
                    extra={
                        "prompt_file": str(resolved_prompt_file),
                        "skipped_moderation": result.skipped_moderation,
                    },
                )
            )
        except WorkbenchError as wb:
            _append_ledger(
                LedgerEntry(
                    kind="preflight",
                    template_id=template_id,
                    status="error",
                    latency_ms=int((time.monotonic() - start) * 1000),
                    size=size,
                    quality=quality,
                    n=1,
                    error_code=wb.envelope.code,
                    error_exit_code=int(wb.envelope.exit_code),
                    extra=(
                        {"prompt_file": str(resolved_prompt_file)}
                        if resolved_prompt_file is not None
                        else {}
                    ),
                )
            )
            raise

    raise SystemExit(cli_dispatch(_run))


preflight_app = typer.Typer(
    name="preflight",
    help="Pre-flight check before render: validate parameters and pre-moderation.",
    no_args_is_help=True,
    add_completion=False,
)
preflight_app.command(
    name="run",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)(preflight_command)
