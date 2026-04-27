# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the costing modules."""

from __future__ import annotations

import pytest

from image2_workbench.costing.heuristics import heuristic_cost, recommend_quality
from image2_workbench.costing.pricing import estimate_cost


def test_official_table_lookup_1024_medium() -> None:
    est = estimate_cost("1024x1024", "medium")
    assert est.track == "official_table"
    assert est.per_image_usd == pytest.approx(0.053)
    assert est.total_usd == pytest.approx(0.053)
    assert est.n == 1


def test_total_scales_with_n() -> None:
    est = estimate_cost("1024x1024", "medium", n=3)
    assert est.n == 3
    assert est.total_usd == pytest.approx(est.per_image_usd * 3)
    assert est.total_usd == pytest.approx(0.053 * 3)


def test_unmapped_size_falls_back_to_heuristic() -> None:
    est = estimate_cost("2048x1536", "high")
    assert est.track == "heuristic_pixel"
    assert est.per_image_usd > 0
    assert "heuristic" in est.note.lower()


def test_heuristic_cost_low_aligns_with_table() -> None:
    cost = heuristic_cost(1024, 1024, "low")
    # Heuristic was tuned against the 1024x1024-low table value of $0.006.
    assert cost == pytest.approx(0.006, rel=0.05)


def test_heuristic_rejects_invalid_quality() -> None:
    with pytest.raises(ValueError):
        heuristic_cost(1024, 1024, "ultra")


def test_heuristic_rejects_nonpositive_dims() -> None:
    with pytest.raises(ValueError):
        heuristic_cost(0, 1024, "low")


def test_recommend_quality_explore() -> None:
    assert recommend_quality("explore") == "low"


def test_recommend_quality_review() -> None:
    assert recommend_quality("review") == "medium"


def test_recommend_quality_ship_default_high() -> None:
    assert recommend_quality("ship") == "high"


def test_recommend_quality_ship_text_light_domain_downgrades() -> None:
    assert recommend_quality("ship", domain_hint="anime") == "medium"
    assert recommend_quality("ship", domain_hint="hero") == "medium"


def test_estimate_cost_rejects_bad_n() -> None:
    with pytest.raises(ValueError):
        estimate_cost("1024x1024", "medium", n=0)


def test_estimate_cost_auto_quality_resolves_to_medium_for_forecast() -> None:
    est = estimate_cost("1024x1024", "auto")
    assert est.quality == "auto"
    assert est.per_image_usd == pytest.approx(0.053)
    assert "auto" in est.note.lower()


def test_estimate_cost_rejects_malformed_size() -> None:
    with pytest.raises(ValueError):
        estimate_cost("not-a-size", "medium")
