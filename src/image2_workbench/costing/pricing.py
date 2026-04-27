# SPDX-License-Identifier: Apache-2.0
"""Official-style token-based cost estimator for gpt-image-2.

We model the public pricing structure (text input tokens + image output
tokens) by mapping common (size, quality) pairs to documented per-image
price points. Numbers below are reference values sourced from public docs
near 2026-04 — they are *estimates* and can drift; canonical pricing
must always come from the OpenAI calculator. When a (size, quality)
pair is not in the table we fall back to the pixel-based heuristic in
`heuristics.py`, marked clearly via `track="heuristic_pixel"`.

V1.5 additions:
    * :func:`estimate_tokens` — token-level estimator for prompt/in-image/
      out-image tokens, with an optional thinking surcharge.
    * :func:`estimate_dollar_cost` — combine the token track with the
      official_table for a triangulated dollar figure.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from .heuristics import QUALITY_MULT, heuristic_cost

Quality = Literal["low", "medium", "high", "auto"]
Track = Literal["official_table", "heuristic_pixel"]
TokenTrack = Literal["token_table", "heuristic"]

# Reference per-image USD costs at common (size, quality) pairs.
_SIZE_QUALITY_USD: dict[tuple[str, Quality], float] = {
    ("1024x1024", "low"): 0.006,
    ("1024x1024", "medium"): 0.053,
    ("1024x1024", "high"): 0.211,
    ("1024x1536", "low"): 0.008,
    ("1024x1536", "medium"): 0.063,
    ("1024x1536", "high"): 0.250,
    ("1536x1024", "low"): 0.008,
    ("1536x1024", "medium"): 0.063,
    ("1536x1024", "high"): 0.250,
    ("2048x2048", "low"): 0.020,
    ("2048x2048", "medium"): 0.150,
    ("2048x2048", "high"): 0.600,
}

# Token reference values (rough but documented). Real numbers must be
# triangulated against OpenAI's pricing calculator. These are tuned for
# the conservative-overestimate side: we'd rather a forecast read $0.30
# and bill $0.25 than the other way around.
#
# 1024x1024 @ medium ≈ 1024 image-output tokens; we scale by
# (pixels / 1024**2) for size and by `QUALITY_MULT` for quality.
_BASE_OUT_TOKENS_PER_IMAGE: int = 1024  # 1024x1024 medium baseline
_BASE_PIXELS: int = 1024 * 1024
# Tokens-per-input-image for edit jobs (caller passes how many references).
_EDIT_INPUT_TOKENS_PER_IMAGE: int = 256
# Approx chars-per-token for English-leaning prompts. Rough — caller is
# warned in the docstring that real numbers differ for CJK and code.
_CHARS_PER_TOKEN: float = 4.0

# Thinking surcharge: applied to the running token total to simulate the
# extra hidden reasoning tokens. Keys are the documented thinking levels
# (auto behaves like low for forecasting).
_THINKING_OVERHEAD_MULT: dict[str, float] = {
    "auto": 0.25,
    "low": 0.25,
    "medium": 1.00,
    "high": 2.50,
}


class CostEstimate(BaseModel):
    size: str
    quality: Quality
    n: int
    per_image_usd: float
    total_usd: float
    track: Track
    note: str = ""


class TokenEstimate(BaseModel):
    """Token-level forecast for a planned image job.

    All counts are conservative estimates. ``track="token_table"`` means
    the (size, quality) pair lives in the official table; ``"heuristic"``
    means we extrapolated from pixels. Real billing may differ — verify
    against OpenAI's pricing calculator before forecasting at scale.
    """

    text_tokens_in: int = Field(..., ge=0)
    image_tokens_in: int = Field(..., ge=0)
    image_tokens_out: int = Field(..., ge=0)
    thinking_overhead: int = Field(..., ge=0)
    total_tokens: int = Field(..., ge=0)
    track: TokenTrack


def _parse_size(size: str) -> tuple[int, int]:
    parts = size.lower().split("x")
    if len(parts) != 2:
        raise ValueError(f"size must look like '1024x1024', got {size!r}")
    try:
        width, height = int(parts[0]), int(parts[1])
    except ValueError as exc:
        raise ValueError(f"size must be two ints separated by 'x', got {size!r}") from exc
    return width, height


def _effective_quality(quality: Quality) -> Quality:
    return quality if quality != "auto" else "medium"


def estimate_cost(size: str, quality: Quality, n: int = 1) -> CostEstimate:
    if n <= 0:
        raise ValueError(f"n must be positive, got {n}")

    # quality="auto" is a server-side decision; for forecasting we treat it
    # as medium (the modal pick in our internal traces) but flag the note.
    effective_quality: Quality = _effective_quality(quality)

    table_key = (size, effective_quality)
    if table_key in _SIZE_QUALITY_USD:
        per_image = _SIZE_QUALITY_USD[table_key]
        note = "official_table"
        if quality == "auto":
            note = "auto resolved as medium for forecasting; actual quality picked server-side"
        return CostEstimate(
            size=size,
            quality=quality,
            n=n,
            per_image_usd=per_image,
            total_usd=per_image * n,
            track="official_table",
            note=note,
        )

    width, height = _parse_size(size)
    per_image = heuristic_cost(width, height, effective_quality)
    note = (
        f"size/quality ({size},{quality}) not in official table; "
        "falling back to pixel heuristic — verify against OpenAI calculator before billing"
    )
    return CostEstimate(
        size=size,
        quality=quality,
        n=n,
        per_image_usd=per_image,
        total_usd=per_image * n,
        track="heuristic_pixel",
        note=note,
    )


def estimate_tokens(
    prompt: str,
    size: str,
    quality: Quality,
    n: int = 1,
    *,
    image_inputs: int = 0,
    thinking: str | None = None,
) -> TokenEstimate:
    """Token-level estimator. Conservative — bias toward over-estimating.

    Heuristics:
      * ``text_tokens_in`` ≈ ``len(prompt) / 4`` (English-biased; CJK and
        code typically consume more tokens-per-char so we round up).
      * ``image_tokens_in`` = ``image_inputs * 256`` (per-edit-reference).
      * ``image_tokens_out`` per image at 1024x1024 medium ≈ 1024; scaled
        linearly by pixels and by :data:`QUALITY_MULT` for quality.
      * ``thinking_overhead`` adds 25% (low/auto) / 100% (medium) /
        250% (high) to the running total.

    Real numbers come from OpenAI's pricing calculator — this is a
    forecasting aid only.
    """
    if n <= 0:
        raise ValueError(f"n must be positive, got {n}")
    if image_inputs < 0:
        raise ValueError(f"image_inputs must be >= 0, got {image_inputs}")

    eff_quality: Quality = _effective_quality(quality)
    if eff_quality not in QUALITY_MULT:
        raise ValueError(f"unknown quality {quality!r}")

    # Round up so we never under-quote text input.
    text_tokens_in = int(-(-len(prompt) // int(_CHARS_PER_TOKEN)))  # ceil div
    image_tokens_in = image_inputs * _EDIT_INPUT_TOKENS_PER_IMAGE

    width, height = _parse_size(size)
    pixel_ratio = max(1.0, (width * height) / _BASE_PIXELS)
    quality_mult = QUALITY_MULT[eff_quality]
    per_image_out = int(round(_BASE_OUT_TOKENS_PER_IMAGE * pixel_ratio * quality_mult))
    image_tokens_out = per_image_out * n

    track: TokenTrack = (
        "token_table"
        if (size, eff_quality) in _SIZE_QUALITY_USD
        else "heuristic"
    )

    subtotal = text_tokens_in + image_tokens_in + image_tokens_out
    thinking_overhead = 0
    if thinking is not None:
        key = thinking.lower()
        if key not in _THINKING_OVERHEAD_MULT:
            raise ValueError(
                f"unknown thinking level {thinking!r}; "
                f"expected one of {sorted(_THINKING_OVERHEAD_MULT)}"
            )
        thinking_overhead = int(round(subtotal * _THINKING_OVERHEAD_MULT[key]))

    total_tokens = subtotal + thinking_overhead

    return TokenEstimate(
        text_tokens_in=text_tokens_in,
        image_tokens_in=image_tokens_in,
        image_tokens_out=image_tokens_out,
        thinking_overhead=thinking_overhead,
        total_tokens=total_tokens,
        track=track,
    )


def estimate_dollar_cost(
    token_est: TokenEstimate,
    size: str,
    quality: Quality,
    n: int,
) -> float:
    """Triangulate dollars for a token forecast.

    We anchor on the official table (more reliable for plausible sizes),
    then fold in the thinking overhead as a proportional surcharge on top
    of the table price. Overhead is taken as ``thinking_overhead /
    (total - thinking_overhead)`` so it's invariant to prompt length
    relative to image-output tokens.
    """
    base = estimate_cost(size, quality, n).total_usd
    pre_thinking = max(1, token_est.total_tokens - token_est.thinking_overhead)
    surcharge_ratio = token_est.thinking_overhead / pre_thinking
    return base * (1.0 + surcharge_ratio)


__all__ = [
    "CostEstimate",
    "Quality",
    "QUALITY_MULT",
    "TokenEstimate",
    "Track",
    "TokenTrack",
    "estimate_cost",
    "estimate_dollar_cost",
    "estimate_tokens",
]
