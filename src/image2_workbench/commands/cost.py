# SPDX-License-Identifier: Apache-2.0
"""`i2w cost` — estimate Images API cost before rendering."""

from typing import Annotated

import typer
from rich.console import Console

from ..costing.pricing import estimate_cost

cost_app = typer.Typer(
    no_args_is_help=True,
    help="Estimate Images API cost for a planned render.",
)


@cost_app.command("estimate")
def estimate(
    size: Annotated[str, typer.Option("--size", help="Image size, e.g. 1024x1024")] = "1024x1024",
    quality: Annotated[
        str, typer.Option("--quality", help="low | medium | high | auto")
    ] = "medium",
    n: Annotated[int, typer.Option("-n", help="Number of images")] = 1,
) -> None:
    """Estimate the cost of generating N images at the given size and quality."""
    console = Console()
    estimate_ = estimate_cost(size=size, quality=quality, n=n)
    console.print(
        f"size={estimate_.size}  quality={estimate_.quality}  n={estimate_.n}",
        markup=False,
    )
    console.print(
        f"per_image=${estimate_.per_image_usd:.4f}  total=${estimate_.total_usd:.4f}",
        markup=False,
    )
    console.print(f"track={estimate_.track}", markup=False)
    if estimate_.note:
        console.print(f"note: {estimate_.note}", markup=False)
