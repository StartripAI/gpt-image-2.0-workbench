# SPDX-License-Identifier: Apache-2.0
"""`i2w render` — call the OpenAI Images API to generate or edit images.

Wires the runtime adapter (:mod:`runtimes.images_api`) to the structured
error envelope (:mod:`errors`) and the local production-observability
ledger (:mod:`ledger`). Every successful or failed call appends one
``LedgerEntry`` so ``i2w ledger query`` can summarise it later.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from ..artifacts import sidecar as sidecar_mod
from ..artifacts import writer as writer_mod
from ..costing import pricing as pricing_mod
from ..errors import WorkbenchError, api_error, cli_dispatch, validation_error
from ..runtimes import images_api
from ..runtimes.types import (
    ApiCallError,
    EditRequest,
    GenerateRequest,
    UnsupportedParameterError,
)

render_app = typer.Typer(
    no_args_is_help=True,
    help="Call the OpenAI Images API to generate or edit.",
)


_VALID_QUALITIES = {"low", "medium", "high", "auto"}
_VALID_BACKGROUNDS = {"auto", "opaque"}
_VALID_FORMATS = {"png", "jpeg", "webp"}
_VALID_MODERATION = {"auto", "low"}


def _read_prompt(prompt_file: Path) -> str:
    if not prompt_file.exists():
        raise validation_error(
            "prompt_file_missing",
            f"prompt file not found: {prompt_file}",
            context={"prompt_file": str(prompt_file)},
        )
    return prompt_file.read_text(encoding="utf-8")


def _validate_common(quality: str, background: str, fmt: str, moderation: str) -> None:
    if background == "transparent":
        raise validation_error(
            "transparent_bg_unsupported",
            "background='transparent' is not supported by gpt-image-2; "
            "use 'auto' or 'opaque'",
            docs_url="docs/error-codes.md#validation",
            context={"background": background},
        )
    if background not in _VALID_BACKGROUNDS:
        raise validation_error(
            "invalid_background",
            f"--background must be 'auto' or 'opaque'; got {background!r}",
            context={"background": background},
        )
    if quality not in _VALID_QUALITIES:
        raise validation_error(
            "invalid_quality",
            f"--quality must be one of low/medium/high/auto; got {quality!r}",
            context={"quality": quality},
        )
    if fmt not in _VALID_FORMATS:
        raise validation_error(
            "invalid_format",
            f"--format must be one of png/jpeg/webp; got {fmt!r}",
            context={"format": fmt},
        )
    if moderation not in _VALID_MODERATION:
        raise validation_error(
            "invalid_moderation",
            f"--moderation must be 'auto' or 'low'; got {moderation!r}",
            context={"moderation": moderation},
        )


def _resolve_out(out: Path | None, default_name: str) -> Path:
    """Resolve the output image path. ``out`` may be a directory or file."""
    if out is None:
        return Path.cwd() / default_name
    target = Path(out)
    if target.exists() and target.is_dir():
        return target / default_name
    if target.suffix == "":
        # Treat extension-less paths as directories the user wants created.
        return target / default_name
    return target


def _cost_estimate(size: str, quality: str, n: int) -> float | None:
    try:
        est = pricing_mod.estimate_cost(size, quality, n)  # type: ignore[arg-type]
        return float(est.total_usd)
    except Exception:  # noqa: BLE001 — cost is advisory; never fail the job
        return None


def _write_artifacts(
    *,
    prompt: str,
    response,
    out_path: Path,
    size: str,
    quality: str,
    n: int,
    fmt: str,
    background: str,
    moderation: str,
    thinking: str | None,
    cost_usd: float | None,
    events: list[str] | None,
) -> tuple[Path, Path]:
    """Write the first image + sidecar; return both paths."""
    if not response.images_b64:
        raise validation_error(
            "empty_response",
            "API returned no image data",
        )
    primary_b64 = response.images_b64[0]
    image_path = writer_mod.write_image(primary_b64, out_path, fmt)
    sc = sidecar_mod.Sidecar(
        model=response.model,
        snapshot=response.snapshot,
        revised_prompt=response.revised_prompt,
        size=size,
        quality=quality,
        n=n,
        format=fmt,
        background=background,
        moderation=moderation,
        thinking=thinking,
        prompt_hash=sidecar_mod.hash_prompt(prompt),
        image_hash=sidecar_mod.hash_image_file(image_path),
        cost_estimate_usd=cost_usd,
        events=list(events or []),
    )
    sidecar_path = sidecar_mod.write(sc, image_path)
    return image_path, sidecar_path


@render_app.command("generate")
def generate(
    prompt_file: Annotated[
        Path,
        typer.Option("--prompt-file", help="Path to a rendered prompt markdown file"),
    ],
    size: Annotated[str, typer.Option("--size", help="Image size, e.g. 1024x1024")] = "1024x1024",
    quality: Annotated[
        str, typer.Option("--quality", help="low | medium | high | auto")
    ] = "medium",
    n: Annotated[int, typer.Option("-n", help="Number of images to generate")] = 1,
    fmt: Annotated[str, typer.Option("--format", help="png | jpeg | webp")] = "png",
    moderation: Annotated[str, typer.Option("--moderation", help="auto | low")] = "auto",
    background: Annotated[
        str,
        typer.Option("--background", help="auto | opaque (transparent is rejected)"),
    ] = "auto",
    out: Annotated[
        Path | None,
        typer.Option("--out", help="Output path or directory for generated images"),
    ] = None,
    think: Annotated[
        str | None,
        typer.Option("--think", help="auto|low|medium|high (probed)"),
    ] = None,
) -> None:
    """Generate images from a rendered prompt file."""
    console = Console()

    def _run() -> None:
        _validate_common(quality, background, fmt, moderation)
        prompt = _read_prompt(prompt_file)
        req = GenerateRequest(
            prompt=prompt,
            size=size,
            quality=quality,  # type: ignore[arg-type]
            n=n,
            fmt=fmt,  # type: ignore[arg-type]
            moderation=moderation,  # type: ignore[arg-type]
            background=background,  # type: ignore[arg-type]
            thinking=think,  # type: ignore[arg-type]
        )
        events: list[str] = []
        out_path = _resolve_out(out, default_name=f"render.{fmt}")
        start = time.monotonic()
        try:
            response = images_api.generate(req, events=events)
        except WorkbenchError:
            raise
        except UnsupportedParameterError as exc:
            raise validation_error(
                "unsupported_parameter",
                str(exc),
                cause=repr(exc),
            ) from exc
        except ApiCallError as exc:
            raise api_error(
                f"images.generate failed: {exc!s}",
                cause=repr(exc),
            ) from exc
        latency_ms = int((time.monotonic() - start) * 1000)
        cost_usd = _cost_estimate(size, quality, n)
        image_path, sidecar_path = _write_artifacts(
            prompt=prompt,
            response=response,
            out_path=out_path,
            size=size,
            quality=quality,
            n=n,
            fmt=fmt,
            background=background,
            moderation=moderation,
            thinking=think,
            cost_usd=cost_usd,
            events=events,
        )
        console.print(
            f"wrote image: {image_path}  sidecar: {sidecar_path}  "
            f"snapshot={response.snapshot}  latency={latency_ms}ms",
            markup=False,
        )

    raise SystemExit(cli_dispatch(_run))


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
    quality: Annotated[
        str, typer.Option("--quality", help="low | medium | high | auto")
    ] = "medium",
    moderation: Annotated[str, typer.Option("--moderation", help="auto | low")] = "auto",
    background: Annotated[
        str,
        typer.Option("--background", help="auto | opaque (transparent is rejected)"),
    ] = "auto",
    fmt: Annotated[str, typer.Option("--format", help="png | jpeg | webp")] = "png",
    out: Annotated[
        Path | None,
        typer.Option("--out", help="Output path or directory for edited images"),
    ] = None,
) -> None:
    """Edit reference images using a rendered prompt file."""
    console = Console()

    def _run() -> None:
        _validate_common(quality, background, fmt, moderation)
        if not image:
            raise validation_error(
                "missing_reference_image",
                "i2w render edit requires at least one reference image "
                "(-i/--image, repeatable)",
                docs_url="docs/error-codes.md#validation",
            )
        prompt = _read_prompt(prompt_file)
        req = EditRequest(
            prompt=prompt,
            images=list(image),
            mask=mask,
            size=size,
            quality=quality,  # type: ignore[arg-type]
            moderation=moderation,  # type: ignore[arg-type]
            background=background,  # type: ignore[arg-type]
            fmt=fmt,  # type: ignore[arg-type]
        )
        out_path = _resolve_out(out, default_name=f"edit.{fmt}")
        start = time.monotonic()
        try:
            response = images_api.edit(req)
        except WorkbenchError:
            raise
        except UnsupportedParameterError as exc:
            raise validation_error(
                "unsupported_parameter",
                str(exc),
                cause=repr(exc),
            ) from exc
        except ApiCallError as exc:
            raise api_error(
                f"images.edit failed: {exc!s}",
                cause=repr(exc),
            ) from exc
        latency_ms = int((time.monotonic() - start) * 1000)
        cost_usd = _cost_estimate(size, quality, 1)
        image_path, sidecar_path = _write_artifacts(
            prompt=prompt,
            response=response,
            out_path=out_path,
            size=size,
            quality=quality,
            n=1,
            fmt=fmt,
            background=background,
            moderation=moderation,
            thinking=None,
            cost_usd=cost_usd,
            events=None,
        )
        console.print(
            f"wrote image: {image_path}  sidecar: {sidecar_path}  "
            f"snapshot={response.snapshot}  latency={latency_ms}ms",
            markup=False,
        )

    raise SystemExit(cli_dispatch(_run))
