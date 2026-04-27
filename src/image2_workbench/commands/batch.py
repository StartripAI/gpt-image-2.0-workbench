# SPDX-License-Identifier: Apache-2.0
"""`i2w batch` — sweep a template across quality tiers and variable matrices."""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

batch_app = typer.Typer(
    no_args_is_help=True,
    help="Run batch sweeps across quality tiers and variable matrices.",
)


@batch_app.command("sweep")
def sweep(
    template: Annotated[str, typer.Option("--template", help="Template id to sweep")],
    vars: Annotated[Path, typer.Option("--vars", help="YAML vars file (may contain matrix lists)")],
    quality: Annotated[
        str,
        typer.Option("--quality", help="Comma-separated: low,medium,high"),
    ] = "low,medium",
) -> None:
    """Sweep a template across the requested quality tiers."""
    console = Console()
    console.print(
        f"[unimplemented] batch sweep template={template} vars={vars} quality={quality}",
        markup=False,
    )
