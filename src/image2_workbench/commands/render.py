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
from pydantic import ValidationError as PydanticValidationError
from rich.console import Console

from ..artifacts import sidecar as sidecar_mod
from ..artifacts import writer as writer_mod
from ..costing import pricing as pricing_mod
from ..errors import WorkbenchError, api_error, cli_dispatch, validation_error
from ..ledger import LedgerEntry, append_entry
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
_VALID_THINKING = {"auto", "low", "medium", "high"}


def _read_prompt(prompt_file: Path) -> str:
    if not prompt_file.exists():
        raise validation_error(
            "prompt_file_missing",
            f"prompt file not found: {prompt_file}",
            context={"prompt_file": str(prompt_file)},
        )
    if not prompt_file.is_file():
        raise validation_error(
            "prompt_file_not_file",
            f"prompt file is not a file: {prompt_file}",
            context={"prompt_file": str(prompt_file)},
        )
    try:
        return prompt_file.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise validation_error(
            "prompt_file_unreadable",
            f"could not read prompt file: {prompt_file}",
            context={"prompt_file": str(prompt_file)},
            cause=repr(exc),
        ) from exc


def _validate_common(
    size: str,
    quality: str,
    background: str,
    fmt: str,
    moderation: str,
    thinking: str | None = None,
    input_fidelity: str | None = None,
) -> None:
    if input_fidelity is not None:
        raise validation_error(
            "input_fidelity_unsupported",
            "input_fidelity is not supported on gpt-image-2; remove the flag",
            docs_url="docs/error-codes.md#validation",
            context={"input_fidelity": input_fidelity},
        )
    if background == "transparent":
        raise validation_error(
            "transparent_bg_unsupported",
            "background='transparent' is not supported by gpt-image-2; "
            "use 'auto' or 'opaque'",
            docs_url="docs/error-codes.md#validation",
            context={"background": background},
        )
    try:
        images_api.validate_size(size)
    except UnsupportedParameterError as exc:
        raise validation_error(
            "unsupported_parameter",
            str(exc),
            cause=repr(exc),
        ) from exc
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
    if thinking is not None and thinking not in _VALID_THINKING:
        raise validation_error(
            "invalid_thinking",
            f"--think must be one of auto/low/medium/high; got {thinking!r}",
            context={"thinking": thinking},
        )


def _request_validation_error(exc: PydanticValidationError) -> WorkbenchError:
    return validation_error(
        "invalid_request",
        "render request options failed validation",
        detail=str(exc),
        cause=repr(exc),
    )


def _artifact_write_error(exc: Exception, target: Path) -> WorkbenchError:
    return api_error(
        f"artifact write failed for {target}: {exc}",
        code="artifact_write_failed",
        context={"path": str(target)},
        cause=repr(exc),
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


def _output_path_for_index(base: Path, index: int, total: int) -> Path:
    if total == 1:
        return base
    suffix = base.suffix or ".png"
    return base.with_name(f"{base.stem}_{index + 1:02d}{suffix}")


def _cost_estimate(size: str, quality: str, n: int) -> float | None:
    try:
        est = pricing_mod.estimate_cost(size, quality, n)  # type: ignore[arg-type]
        return float(est.total_usd)
    except Exception:  # noqa: BLE001 — cost is advisory; never fail the job
        return None


def _append_ledger(entry: LedgerEntry) -> None:
    try:
        append_entry(entry)
    except Exception:  # noqa: BLE001
        pass


def _append_error_ledger(
    *,
    kind: str,
    template_id: str | None,
    size: str,
    quality: str,
    n: int,
    latency_ms: int,
    error: WorkbenchError,
) -> None:
    _append_ledger(
        LedgerEntry(
            kind=kind,  # type: ignore[arg-type]
            template_id=template_id,
            status="error",
            size=size,
            quality=quality,
            n=n,
            latency_ms=latency_ms,
            error_code=error.envelope.code,
            error_exit_code=int(error.envelope.exit_code),
        )
    )


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
) -> list[tuple[Path, Path]]:
    """Write every returned image + sidecar; return all paths."""
    if not response.images_b64:
        raise validation_error(
            "empty_response",
            "API returned no image data",
        )
    paths: list[tuple[Path, Path]] = []
    total = len(response.images_b64)
    for idx, b64 in enumerate(response.images_b64):
        target = _output_path_for_index(out_path, idx, total)
        try:
            image_path = writer_mod.write_image(b64, target, fmt)
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
        except WorkbenchError:
            raise
        except Exception as exc:  # noqa: BLE001
            raise _artifact_write_error(exc, target) from exc
        paths.append((image_path, sidecar_path))
    return paths


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
    input_fidelity: Annotated[
        str | None,
        typer.Option(
            "--input-fidelity",
            help="Rejected for gpt-image-2; provided for explicit diagnostics",
        ),
    ] = None,
    template_id: Annotated[
        str | None,
        typer.Option("--template-id", help="Template id for ledger grouping"),
    ] = None,
) -> None:
    """Generate images from a rendered prompt file."""
    console = Console()

    def _run() -> None:
        start = time.monotonic()
        try:
            _validate_common(
                size,
                quality,
                background,
                fmt,
                moderation,
                think,
                input_fidelity,
            )
            prompt = _read_prompt(prompt_file)
            try:
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
            except PydanticValidationError as exc:
                raise _request_validation_error(exc) from exc
            events: list[str] = []
            out_path = _resolve_out(out, default_name=f"render.{fmt}")
            try:
                response = images_api.generate(req, events=events)
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
            paths = _write_artifacts(
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
            _append_ledger(
                LedgerEntry(
                    kind="generate",
                    template_id=template_id,
                    snapshot=response.snapshot,
                    status="ok",
                    latency_ms=latency_ms,
                    cost_usd=cost_usd,
                    size=size,
                    quality=quality,
                    n=n,
                )
            )
            for image_path, sidecar_path in paths:
                console.print(
                    f"wrote image: {image_path}  sidecar: {sidecar_path}  "
                    f"snapshot={response.snapshot}  latency={latency_ms}ms",
                    markup=False,
                )
        except WorkbenchError as wb:
            latency_ms = int((time.monotonic() - start) * 1000)
            _append_error_ledger(
                kind="generate",
                template_id=template_id,
                size=size,
                quality=quality,
                n=n,
                latency_ms=latency_ms,
                error=wb,
            )
            raise

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
    input_fidelity: Annotated[
        str | None,
        typer.Option(
            "--input-fidelity",
            help="Rejected for gpt-image-2; provided for explicit diagnostics",
        ),
    ] = None,
    out: Annotated[
        Path | None,
        typer.Option("--out", help="Output path or directory for edited images"),
    ] = None,
    template_id: Annotated[
        str | None,
        typer.Option("--template-id", help="Template id for ledger grouping"),
    ] = None,
) -> None:
    """Edit reference images using a rendered prompt file."""
    console = Console()

    def _run() -> None:
        start = time.monotonic()
        try:
            _validate_common(
                size,
                quality,
                background,
                fmt,
                moderation,
                input_fidelity=input_fidelity,
            )
            if not image:
                raise validation_error(
                    "missing_reference_image",
                    "i2w render edit requires at least one reference image "
                    "(-i/--image, repeatable)",
                    docs_url="docs/error-codes.md#validation",
                )
            for img in image:
                if not img.exists():
                    raise validation_error(
                        "input_image_missing",
                        f"input image not found: {img}",
                        docs_url="docs/error-codes.md#validation",
                        context={"image": str(img)},
                    )
                if not img.is_file():
                    raise validation_error(
                        "input_image_not_file",
                        f"input image is not a file: {img}",
                        docs_url="docs/error-codes.md#validation",
                        context={"image": str(img)},
                    )
            if mask is not None and not mask.exists():
                raise validation_error(
                    "mask_missing",
                    f"mask image not found: {mask}",
                    docs_url="docs/error-codes.md#validation",
                    context={"mask": str(mask)},
                )
            if mask is not None and not mask.is_file():
                raise validation_error(
                    "mask_not_file",
                    f"mask image is not a file: {mask}",
                    docs_url="docs/error-codes.md#validation",
                    context={"mask": str(mask)},
                )
            prompt = _read_prompt(prompt_file)
            try:
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
            except PydanticValidationError as exc:
                raise _request_validation_error(exc) from exc
            out_path = _resolve_out(out, default_name=f"edit.{fmt}")
            try:
                response = images_api.edit(req)
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
            paths = _write_artifacts(
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
            _append_ledger(
                LedgerEntry(
                    kind="edit",
                    template_id=template_id,
                    snapshot=response.snapshot,
                    status="ok",
                    latency_ms=latency_ms,
                    cost_usd=cost_usd,
                    size=size,
                    quality=quality,
                    n=1,
                )
            )
            for image_path, sidecar_path in paths:
                console.print(
                    f"wrote image: {image_path}  sidecar: {sidecar_path}  "
                    f"snapshot={response.snapshot}  latency={latency_ms}ms",
                    markup=False,
                )
        except WorkbenchError as wb:
            latency_ms = int((time.monotonic() - start) * 1000)
            _append_error_ledger(
                kind="edit",
                template_id=template_id,
                size=size,
                quality=quality,
                n=1,
                latency_ms=latency_ms,
                error=wb,
            )
            raise

    raise SystemExit(cli_dispatch(_run))
