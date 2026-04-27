# SPDX-License-Identifier: Apache-2.0
"""`i2w render` — call the OpenAI Images API to generate or edit images."""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

render_app = typer.Typer(
    no_args_is_help=True,
    help="Call the OpenAI Images API to generate or edit.",
)


@render_app.command("generate")
def generate(
    prompt_file: Annotated[
        Path,
        typer.Option("--prompt-file", help="Path to a rendered prompt markdown file"),
    ],
    size: Annotated[str, typer.Option("--size", help="Image size, e.g. 1024x1024")] = "1024x1024",
    quality: Annotated[str, typer.Option("--quality", help="low | medium | high")] = "medium",
    n: Annotated[int, typer.Option("-n", help="Number of images to generate")] = 1,
    fmt: Annotated[str, typer.Option("--format", help="png | jpeg | webp")] = "png",
    moderation: Annotated[str, typer.Option("--moderation", help="auto | low")] = "auto",
    out: Annotated[
        Path | None,
        typer.Option("--out", help="Output directory for generated images"),
    ] = None,
    think: Annotated[
        str | None,
        typer.Option("--think", help="auto|low|medium|high (probed)"),
    ] = None,
) -> None:
    """Generate images from a rendered prompt file."""
    console = Console()
    console.print(
        f"[unimplemented] render generate prompt_file={prompt_file} size={size} "
        f"quality={quality} n={n} format={fmt} moderation={moderation} out={out} "
        f"think={think}",
        markup=False,
    )


@render_app.command("edit")
def edit(
    prompt_file: Annotated[
        Path,
        typer.Option("--prompt-file", help="Path to a rendered prompt markdown file"),
    ],
    image: Annotated[
        list[Path],
        typer.Option("-i", "--image", help="Reference image; repeatable"),
    ] = [],  # noqa: B006 — Typer repeatable Option requires a mutable default
    mask: Annotated[
        Path | None,
        typer.Option("-m", "--mask", help="Optional mask image (PNG with alpha)"),
    ] = None,
    size: Annotated[str, typer.Option("--size", help="Image size, e.g. 1024x1024")] = "1024x1024",
    quality: Annotated[str, typer.Option("--quality", help="low | medium | high")] = "medium",
    moderation: Annotated[str, typer.Option("--moderation", help="auto | low")] = "auto",
    out: Annotated[
        Path | None,
        typer.Option("--out", help="Output directory for edited images"),
    ] = None,
) -> None:
    """Edit reference images using a rendered prompt file."""
    console = Console()
    console.print(
        f"[unimplemented] render edit prompt_file={prompt_file} images={list(image)} "
        f"mask={mask} size={size} quality={quality} moderation={moderation} out={out}",
        markup=False,
    )
