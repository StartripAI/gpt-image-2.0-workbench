# SPDX-License-Identifier: Apache-2.0
"""Pixel-based heuristic cost track and quality recommendations.

Why this module exists: OpenAI image pricing changes faster than we can
ship a release. The official cost path lives in `pricing.py` and looks up
documented price points; when a (size, quality) pair is not in that table
(custom sizes, future tiers, experimental >2K resolutions) we fall through
to a quadratic-in-pixels heuristic so the workbench still emits a number,
and we mark `track="heuristic_pixel"` on the result so callers know to
double-check against the OpenAI calculator.
"""

from __future__ import annotations

from typing import Literal

# Quality multipliers calibrated against the table values in pricing.py:
#  1024x1024 (≈1.05 MP) low ≈ $0.006, medium ≈ $0.053 (≈ 8.8x), high ≈ $0.211 (≈ 35x).
QUALITY_MULT: dict[str, float] = {
    "low": 1.0,
    "medium": 8.5,
    "high": 35.0,
    "auto": 8.5,
}

# Tuned so that 1024x1024 (≈1.0486 MP) at quality=low gives ~$0.006.
BASE_USD_PER_MEGAPIXEL_LOW: float = 0.0057


def heuristic_cost(width: int, height: int, quality: str) -> float:
    if width <= 0 or height <= 0:
        raise ValueError(f"width/height must be positive, got {width}x{height}")
    if quality not in QUALITY_MULT:
        raise ValueError(f"unknown quality {quality!r}; known: {sorted(QUALITY_MULT)}")
    megapixels = (width * height) / 1_000_000
    return megapixels * BASE_USD_PER_MEGAPIXEL_LOW * QUALITY_MULT[quality]


Intent = Literal["explore", "review", "ship"]


def recommend_quality(intent: Intent, domain_hint: str | None = None) -> str:
    """Heuristic policy mapping intent to quality.

    - explore: cheapest tier, used for ideation passes.
    - review:  medium, suitable for stakeholder review of likely-final layouts.
    - ship:    high by default; downgraded to medium when the domain hint
               suggests text is sparse (anime, hero photography), where the
               extra cost rarely buys visible improvement.
    """
    if intent == "explore":
        return "low"
    if intent == "review":
        return "medium"
    if intent == "ship":
        text_light = {"anime", "hero", "photography", "photo"}
        if domain_hint and domain_hint.lower() in text_light:
            return "medium"
        return "high"
    raise ValueError(f"unknown intent {intent!r}")
