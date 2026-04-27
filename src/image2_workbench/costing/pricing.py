# SPDX-License-Identifier: Apache-2.0
"""Official-style token-based cost estimator for gpt-image-2.

We model the public pricing structure (text input tokens + image output
tokens) by mapping common (size, quality) pairs to documented per-image
price points. Numbers below are reference values sourced from public docs
near 2026-04 — they are *estimates* and can drift; canonical pricing
must always come from the OpenAI calculator. When a (size, quality)
pair is not in the table we fall back to the pixel-based heuristic in
`heuristics.py`, marked clearly via `track="heuristic_pixel"`.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from .heuristics import heuristic_cost

Quality = Literal["low", "medium", "high", "auto"]
Track = Literal["official_table", "heuristic_pixel"]

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


class CostEstimate(BaseModel):
    size: str
    quality: Quality
    n: int
    per_image_usd: float
    total_usd: float
    track: Track
    note: str = ""


def _parse_size(size: str) -> tuple[int, int]:
    parts = size.lower().split("x")
    if len(parts) != 2:
        raise ValueError(f"size must look like '1024x1024', got {size!r}")
    try:
        width, height = int(parts[0]), int(parts[1])
    except ValueError as exc:
        raise ValueError(f"size must be two ints separated by 'x', got {size!r}") from exc
    return width, height


def estimate_cost(size: str, quality: Quality, n: int = 1) -> CostEstimate:
    if n <= 0:
        raise ValueError(f"n must be positive, got {n}")

    # quality="auto" is a server-side decision; for forecasting we treat it
    # as medium (the modal pick in our internal traces) but flag the note.
    effective_quality: Quality = quality if quality != "auto" else "medium"

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
