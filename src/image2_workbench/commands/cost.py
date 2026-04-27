# SPDX-License-Identifier: Apache-2.0
"""`i2w cost` — estimate Images API cost before rendering.

Subcommands:
    estimate  — single (size, quality, n) point estimate; with
                ``--token-estimate`` switch to the token-track estimator.
    compare   — print a Rich table with the cost matrix across cohorts of
                sizes and qualities.
    budget    — sum the cost of every entry in a YAML plan and report
                whether it fits under ``--max-usd``.

All subcommands route fatal errors through :func:`cli_dispatch` when
``image2_workbench.errors`` is available, falling back to bare typer
exits otherwise (so this module works whether or not Agent X1's
errors module has landed yet).
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

import typer
import yaml
from rich.console import Console
from rich.table import Table

from ..costing.pricing import (
    estimate_cost,
    estimate_dollar_cost,
    estimate_tokens,
)

# Soft import: Agent X1 owns errors.py. If it isn't present yet we
# emulate just enough to keep this CLI runnable for tests.
try:  # pragma: no cover — branch resolved by test environment
    from ..errors import ExitCode, cli_dispatch, validation_error
except ImportError:  # pragma: no cover
    ExitCode = None  # type: ignore[assignment]
    cli_dispatch = None  # type: ignore[assignment]
    validation_error = None  # type: ignore[assignment]


cost_app = typer.Typer(
    no_args_is_help=True,
    help="Estimate Images API cost for a planned render.",
)


def _exit_validation(message: str) -> typer.Exit:
    """Map a validation failure to ExitCode.VALIDATION (4) when available."""
    if ExitCode is not None:
        code = int(getattr(ExitCode, "VALIDATION", 4))
    else:
        code = 4
    typer.echo(message, err=True)
    return typer.Exit(code=code)


def _run_dispatched(fn: Any, *args: Any, **kwargs: Any) -> Any:
    """Route through cli_dispatch when X1's errors module is wired in."""
    if cli_dispatch is not None:
        return cli_dispatch(fn, *args, **kwargs)
    return fn(*args, **kwargs)


def _raise_validation(message: str):
    if validation_error is not None:
        raise validation_error("invalid_cost_request", message)
    raise _exit_validation(message)


def _split_csv(value: str) -> list[str]:
    return [v.strip() for v in value.split(",") if v.strip()]


@cost_app.command("estimate")
def estimate(
    size: Annotated[str, typer.Option("--size", help="Image size, e.g. 1024x1024")] = "1024x1024",
    quality: Annotated[
        str, typer.Option("--quality", help="low | medium | high | auto")
    ] = "medium",
    n: Annotated[int, typer.Option("-n", help="Number of images")] = 1,
    token_estimate: Annotated[
        bool,
        typer.Option(
            "--token-estimate",
            help="Use the token-level estimator (forecasts text-in / image-out tokens).",
        ),
    ] = False,
    prompt: Annotated[
        str,
        typer.Option(
            "--prompt",
            help="Prompt text for token-level estimation (used with --token-estimate).",
        ),
    ] = "",
    image_inputs: Annotated[
        int,
        typer.Option(
            "--image-inputs",
            help="Reference image count for edit jobs (token-level only).",
        ),
    ] = 0,
    thinking: Annotated[
        str | None,
        typer.Option("--thinking", help="auto | low | medium | high (token-level only)"),
    ] = None,
) -> None:
    """Estimate the cost of generating N images at the given size and quality."""
    console = Console()
    def _run() -> None:
        try:
            cost = estimate_cost(size=size, quality=quality, n=n)  # type: ignore[arg-type]
            token_est = None
            triangulated = None
            if token_estimate:
                token_est = estimate_tokens(
                    prompt=prompt,
                    size=size,
                    quality=quality,  # type: ignore[arg-type]
                    n=n,
                    image_inputs=image_inputs,
                    thinking=thinking,
                )
                triangulated = estimate_dollar_cost(token_est, size, quality, n)  # type: ignore[arg-type]
        except ValueError as exc:
            _raise_validation(str(exc))

        console.print(
            f"size={cost.size}  quality={cost.quality}  n={cost.n}",
            markup=False,
        )
        console.print(
            f"per_image=${cost.per_image_usd:.4f}  total=${cost.total_usd:.4f}",
            markup=False,
        )
        console.print(f"track={cost.track}", markup=False)
        if cost.note:
            console.print(f"note: {cost.note}", markup=False)

        if token_est is not None and triangulated is not None:
            console.print(
                (
                    f"token_estimate: text_in={token_est.text_tokens_in} "
                    f"image_in={token_est.image_tokens_in} "
                    f"image_out={token_est.image_tokens_out} "
                    f"thinking_overhead={token_est.thinking_overhead} "
                    f"total_tokens={token_est.total_tokens} "
                    f"track={token_est.track}"
                ),
                markup=False,
            )
            console.print(
                f"triangulated_total=${triangulated:.4f}",
                markup=False,
            )

    raise typer.Exit(code=int(_run_dispatched(_run)))


@cost_app.command("compare")
def compare(
    sizes: Annotated[
        str,
        typer.Option("--size", help="Comma-separated sizes"),
    ] = "1024x1024,1024x1536,1536x1024",
    qualities: Annotated[
        str,
        typer.Option("--quality", help="Comma-separated"),
    ] = "low,medium,high",
    n: Annotated[int, typer.Option("-n", help="Number of images per cell")] = 1,
) -> None:
    """Print a comparison matrix of (size x quality) costs."""
    console = Console()
    size_list = _split_csv(sizes)
    quality_list = _split_csv(qualities)
    if not size_list or not quality_list:
        raise _exit_validation("--size and --quality must each list >= 1 value")

    table = Table(title=f"Cost matrix (n={n})")
    table.add_column("size", justify="left")
    table.add_column("quality", justify="left")
    table.add_column("per_image_usd", justify="right")
    table.add_column("total_usd", justify="right")
    table.add_column("track", justify="left")

    grand_total = 0.0
    for size in size_list:
        for quality in quality_list:
            try:
                est = estimate_cost(size=size, quality=quality, n=n)
            except ValueError as exc:
                raise _exit_validation(f"invalid (size={size}, quality={quality}): {exc}") from exc
            table.add_row(
                size,
                quality,
                f"${est.per_image_usd:.4f}",
                f"${est.total_usd:.4f}",
                est.track,
            )
            grand_total += est.total_usd
    console.print(table)
    console.print(f"grand_total_usd=${grand_total:.4f}", markup=False)


@cost_app.command("budget")
def budget(
    plan: Annotated[
        Path,
        typer.Option("--plan", help="YAML plan file: list of {size, quality, n} entries"),
    ],
    max_usd: Annotated[
        float,
        typer.Option("--max-usd", help="Spending ceiling in USD"),
    ] = 10.0,
) -> None:
    """Sum the cost of all entries in the plan; exit 4 if over budget."""
    console = Console()
    if not plan.exists():
        raise _exit_validation(f"plan file not found: {plan}")

    try:
        with plan.open("r", encoding="utf-8") as fh:
            raw = yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        raise _exit_validation(f"plan {plan} is not valid YAML: {exc}") from exc

    if not isinstance(raw, list):
        raise _exit_validation(
            f"plan {plan} must be a YAML list of {{size, quality, n}} entries"
        )

    total = 0.0
    table = Table(title=f"Plan: {plan}")
    table.add_column("#", justify="right")
    table.add_column("size", justify="left")
    table.add_column("quality", justify="left")
    table.add_column("n", justify="right")
    table.add_column("subtotal_usd", justify="right")
    table.add_column("track", justify="left")

    for i, entry in enumerate(raw):
        if not isinstance(entry, dict):
            raise _exit_validation(
                f"plan entry {i} must be a mapping; got {type(entry).__name__}"
            )
        try:
            size = str(entry["size"])
            quality = str(entry["quality"])
            n = int(entry.get("n", 1))
        except (KeyError, TypeError, ValueError) as exc:
            raise _exit_validation(
                f"plan entry {i} missing required keys (size, quality[, n]): {exc}"
            ) from exc
        try:
            est = estimate_cost(size=size, quality=quality, n=n)  # type: ignore[arg-type]
        except ValueError as exc:
            raise _exit_validation(
                f"plan entry {i} invalid (size={size}, quality={quality}): {exc}"
            ) from exc
        total += est.total_usd
        table.add_row(
            str(i),
            size,
            quality,
            str(n),
            f"${est.total_usd:.4f}",
            est.track,
        )

    console.print(table)
    fits = total <= max_usd
    verdict = "OK" if fits else "OVER BUDGET"
    console.print(
        f"total=${total:.4f}  max_usd=${max_usd:.4f}  status={verdict}",
        markup=False,
    )
    if not fits:
        raise _exit_validation(
            f"plan total ${total:.4f} exceeds budget ${max_usd:.4f}"
        )


__all__ = ["cost_app"]
