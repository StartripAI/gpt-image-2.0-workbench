# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the V1.5 token-level cost estimator.

The token estimator is a forecasting aid; numbers are approximate but
must stay monotonic in the obvious dimensions (size, quality, thinking,
image_inputs) and round up rather than down.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from image2_workbench.costing.pricing import (
    TokenEstimate,
    estimate_dollar_cost,
    estimate_tokens,
)


def test_basic_estimate_returns_token_estimate() -> None:
    est = estimate_tokens("short prompt", "1024x1024", "low")
    assert isinstance(est, TokenEstimate)
    assert est.text_tokens_in > 0
    assert est.image_tokens_in == 0
    assert est.image_tokens_out > 0
    assert est.thinking_overhead == 0
    assert est.total_tokens == (
        est.text_tokens_in + est.image_tokens_in + est.image_tokens_out
    )
    assert est.track == "token_table"


def test_text_tokens_round_up() -> None:
    # 7 chars / 4 chars-per-token = 1.75 → ceil to 2.
    est = estimate_tokens("a" * 7, "1024x1024", "low")
    assert est.text_tokens_in == 2


def test_bigger_size_more_image_output_tokens() -> None:
    small = estimate_tokens("p", "1024x1024", "medium")
    big = estimate_tokens("p", "2048x2048", "medium")
    assert big.image_tokens_out > small.image_tokens_out


def test_higher_quality_more_image_output_tokens() -> None:
    low = estimate_tokens("p", "1024x1024", "low")
    medium = estimate_tokens("p", "1024x1024", "medium")
    high = estimate_tokens("p", "1024x1024", "high")
    assert low.image_tokens_out < medium.image_tokens_out < high.image_tokens_out


def test_thinking_high_adds_overhead() -> None:
    no_think = estimate_tokens("p", "1024x1024", "medium")
    high = estimate_tokens("p", "1024x1024", "medium", thinking="high")
    assert high.thinking_overhead > no_think.thinking_overhead == 0
    # high == 250%, so overhead should dwarf the subtotal.
    assert high.thinking_overhead > 2 * (
        high.text_tokens_in + high.image_tokens_in + high.image_tokens_out
    )


def test_thinking_levels_monotonic() -> None:
    base = estimate_tokens("p", "1024x1024", "medium").total_tokens
    low_t = estimate_tokens("p", "1024x1024", "medium", thinking="low").total_tokens
    medium_t = estimate_tokens("p", "1024x1024", "medium", thinking="medium").total_tokens
    high_t = estimate_tokens("p", "1024x1024", "medium", thinking="high").total_tokens
    assert base < low_t < medium_t < high_t


def test_image_inputs_increase_image_tokens_in() -> None:
    none = estimate_tokens("p", "1024x1024", "low", image_inputs=0)
    two = estimate_tokens("p", "1024x1024", "low", image_inputs=2)
    assert two.image_tokens_in > none.image_tokens_in
    # And exactly 2x the per-input rate.
    assert two.image_tokens_in == 2 * 256


def test_n_scales_image_tokens_out() -> None:
    one = estimate_tokens("p", "1024x1024", "medium", n=1)
    three = estimate_tokens("p", "1024x1024", "medium", n=3)
    assert three.image_tokens_out == 3 * one.image_tokens_out


def test_token_estimate_is_pydantic_validated() -> None:
    # Negative counts must be rejected at construction.
    with pytest.raises(ValidationError):
        TokenEstimate(
            text_tokens_in=-1,
            image_tokens_in=0,
            image_tokens_out=0,
            thinking_overhead=0,
            total_tokens=0,
            track="heuristic",
        )


def test_uncommon_size_uses_heuristic_track() -> None:
    est = estimate_tokens("p", "1280x720", "low")
    assert est.track == "heuristic"


def test_estimate_tokens_rejects_bad_n() -> None:
    with pytest.raises(ValueError):
        estimate_tokens("p", "1024x1024", "low", n=0)


def test_estimate_tokens_rejects_negative_image_inputs() -> None:
    with pytest.raises(ValueError):
        estimate_tokens("p", "1024x1024", "low", image_inputs=-1)


def test_estimate_tokens_rejects_unknown_thinking() -> None:
    with pytest.raises(ValueError):
        estimate_tokens("p", "1024x1024", "low", thinking="ultra")


def test_auto_quality_resolves_to_medium_for_token_estimate() -> None:
    auto = estimate_tokens("p", "1024x1024", "auto")
    medium = estimate_tokens("p", "1024x1024", "medium")
    assert auto.image_tokens_out == medium.image_tokens_out


def test_estimate_dollar_cost_matches_table_when_no_thinking() -> None:
    token_est = estimate_tokens("hi", "1024x1024", "medium")
    dollars = estimate_dollar_cost(token_est, "1024x1024", "medium", 1)
    # Without thinking, surcharge is zero; equals the table value.
    assert dollars == pytest.approx(0.053, rel=1e-6)


def test_estimate_dollar_cost_includes_thinking_surcharge() -> None:
    no_think = estimate_dollar_cost(
        estimate_tokens("hi", "1024x1024", "medium"),
        "1024x1024",
        "medium",
        1,
    )
    with_think = estimate_dollar_cost(
        estimate_tokens("hi", "1024x1024", "medium", thinking="high"),
        "1024x1024",
        "medium",
        1,
    )
    assert with_think > no_think
