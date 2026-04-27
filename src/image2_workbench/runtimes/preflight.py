# SPDX-License-Identifier: Apache-2.0
"""Pre-flight validation: cheap checks BEFORE the expensive image API call.

Two layers:
  1. Local validation (sizes, parameter compatibility, no transparent BG).
  2. /v1/moderations API call to predict whether the prompt would be blocked.

The function never raises: callers always receive a populated
:class:`PreflightResult`. Each blocker carries a stable ``code`` so downstream
tooling can map it to an exit code (see ``image2_workbench.errors``).
"""
from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

from ..compiler.validators import (
    BackgroundValidationError,
    FormatValidationError,
    SizeValidationError,
    UnsupportedParameterError,
    validate_background,
    validate_format_compression,
    validate_no_input_fidelity,
    validate_size,
)

if TYPE_CHECKING:
    from openai import OpenAI


class PreflightBlocker(BaseModel):
    """Stable, structured reason why preflight failed."""

    code: str
    message: str


class PreflightResult(BaseModel):
    """Outcome of running preflight checks before a render.

    ``passed`` is True only when there are zero blockers and (if moderation was
    consulted) the moderation API did not flag the prompt.
    """

    passed: bool
    blockers: list[str] = Field(default_factory=list)
    blocker_codes: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    moderation_flagged: bool = False
    moderation_categories: list[str] = Field(default_factory=list)
    estimated_tokens: int | None = None
    skipped_moderation: bool = False


def _add_blocker(
    blockers: list[str],
    blocker_codes: list[str],
    *,
    code: str,
    message: str,
) -> None:
    blockers.append(message)
    blocker_codes.append(code)


def _local_checks(
    *,
    size: str,
    quality: str,
    background: str,
    output_format: str,
    output_compression: int | None,
    extra_params: dict[str, Any] | None,
    blockers: list[str],
    blocker_codes: list[str],
    warnings: list[str],
) -> None:
    """Run all the local parameter checks; populate blockers/warnings in place."""
    # Background
    try:
        validate_background(background)
    except BackgroundValidationError as exc:
        if "transparent" in background.lower():
            _add_blocker(
                blockers, blocker_codes, code="transparent_bg", message=str(exc)
            )
        else:
            _add_blocker(
                blockers,
                blocker_codes,
                code="background_invalid",
                message=str(exc),
            )

    # input_fidelity (and other unsupported extras)
    if extra_params:
        try:
            validate_no_input_fidelity(extra_params)
        except UnsupportedParameterError as exc:
            _add_blocker(
                blockers,
                blocker_codes,
                code="input_fidelity_param",
                message=str(exc),
            )

    # Size
    try:
        width, height = validate_size(size)
    except SizeValidationError as exc:
        msg = str(exc)
        if "max edge" in msg or "above ceiling" in msg or "aspect ratio" in msg:
            code = "size_too_large"
        elif "below floor" in msg or "non-positive" in msg:
            code = "size_too_small"
        else:
            code = "size_invalid"
        _add_blocker(blockers, blocker_codes, code=code, message=msg)
    else:
        # Experimental size warning (4K-class) is informational, not blocking.
        from ..compiler.validators import is_experimental_size

        if is_experimental_size(width, height):
            warnings.append(
                f"size {size} is in the experimental band — generation may "
                "produce inconsistent quality"
            )

    # Format / compression compatibility
    try:
        validate_format_compression(output_format, output_compression)
    except FormatValidationError as exc:
        if (
            output_format
            and output_format.lower() == "png"
            and output_compression is not None
        ):
            code = "compression_format_mismatch"
        else:
            code = "format_invalid"
        _add_blocker(blockers, blocker_codes, code=code, message=str(exc))

    # Quality is only advisory at preflight (no hard list locally).
    if quality and quality.lower() not in {"low", "medium", "high", "auto"}:
        warnings.append(
            f"quality={quality!r} is not one of low/medium/high/auto — the API "
            "may reject it"
        )


def _moderation_check(
    *,
    prompt: str,
    client: Any | None,
    skip_moderation_api: bool,
) -> tuple[bool, list[str], bool]:
    """Run /v1/moderations.

    Returns ``(flagged, categories, skipped)``. Never raises: any error means
    we bail out with ``skipped=True`` so the local validation result still
    reaches the caller.
    """
    if skip_moderation_api:
        return False, [], True

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key and client is None:
        return False, [], True

    try:
        cli = client if client is not None else _new_client()
    except Exception:  # noqa: BLE001 — preflight must never raise
        return False, [], True

    try:
        resp = cli.moderations.create(input=prompt)
    except Exception:  # noqa: BLE001 — network/auth errors are skips, not crashes
        return False, [], True

    # The OpenAI SDK returns a Moderation response with .results[0].flagged
    # and .results[0].categories (a CategoryScores-like object).
    try:
        result = resp.results[0]
    except (AttributeError, IndexError, TypeError):
        return False, [], True

    flagged = bool(getattr(result, "flagged", False))
    categories: list[str] = []
    cats = getattr(result, "categories", None)
    if cats is not None:
        # categories may be a pydantic model OR a dict. Avoid dir() since
        # MagicMock instances expose unbounded attrs.
        items: dict[str, Any] = {}
        if isinstance(cats, dict):
            items = cats
        elif hasattr(cats, "model_dump"):
            try:
                items = cats.model_dump()
            except Exception:  # noqa: BLE001
                items = {}
        else:
            for name in _KNOWN_MODERATION_CATEGORIES:
                try:
                    val = getattr(cats, name, None)
                except Exception:  # noqa: BLE001
                    continue
                if val is not None:
                    items[name] = val
        for name, val in items.items():
            if val is True:
                categories.append(name)
    return flagged, categories, False


_KNOWN_MODERATION_CATEGORIES: tuple[str, ...] = (
    "harassment",
    "harassment_threatening",
    "hate",
    "hate_threatening",
    "illicit",
    "illicit_violent",
    "self_harm",
    "self_harm_intent",
    "self_harm_instructions",
    "sexual",
    "sexual_minors",
    "violence",
    "violence_graphic",
)


def preflight(
    prompt: str,
    *,
    size: str = "1024x1024",
    quality: str = "medium",
    background: str = "auto",
    output_format: str = "png",
    output_compression: int | None = None,
    moderation: str = "auto",  # noqa: ARG001 — reserved for parity with render
    extra_params: dict[str, Any] | None = None,
    skip_moderation_api: bool = False,
    client: OpenAI | None = None,
) -> PreflightResult:
    """Run all checks before an expensive image-generation call.

    Returns a :class:`PreflightResult` describing whether the request would be
    locally accepted, whether the prompt is likely to be blocked by moderation,
    and any non-fatal warnings. The function never raises.
    """
    blockers: list[str] = []
    blocker_codes: list[str] = []
    warnings: list[str] = []

    _local_checks(
        size=size,
        quality=quality,
        background=background,
        output_format=output_format,
        output_compression=output_compression,
        extra_params=extra_params,
        blockers=blockers,
        blocker_codes=blocker_codes,
        warnings=warnings,
    )

    flagged, categories, skipped = _moderation_check(
        prompt=prompt,
        client=client,
        skip_moderation_api=skip_moderation_api,
    )

    passed = not blockers and not flagged
    return PreflightResult(
        passed=passed,
        blockers=blockers,
        blocker_codes=blocker_codes,
        warnings=warnings,
        moderation_flagged=flagged,
        moderation_categories=categories,
        estimated_tokens=None,
        skipped_moderation=skipped,
    )


def _new_client() -> Any:
    from openai import OpenAI  # noqa: WPS433

    return OpenAI()
