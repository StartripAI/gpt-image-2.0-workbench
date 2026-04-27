# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the preflight runtime."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from image2_workbench.runtimes.preflight import PreflightResult, preflight


@pytest.fixture(autouse=True)
def _no_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Tests must never accidentally hit the real OpenAI API."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)


def _moderation_response(*, flagged: bool, categories: dict[str, bool]) -> object:
    """Build a minimal stand-in matching the OpenAI Moderation response shape."""

    class _Cats:
        def __init__(self, mapping: dict[str, bool]) -> None:
            for name, val in mapping.items():
                setattr(self, name, val)

        def model_dump(self) -> dict[str, bool]:
            return {
                k: v
                for k, v in self.__dict__.items()
                if not k.startswith("_")
            }

    class _Item:
        def __init__(self, flagged: bool, cats: _Cats) -> None:
            self.flagged = flagged
            self.categories = cats

    class _Resp:
        def __init__(self, item: _Item) -> None:
            self.results = [item]

    return _Resp(_Item(flagged, _Cats(categories)))


def test_transparent_background_blocks() -> None:
    result = preflight("a cat", background="transparent")
    assert result.passed is False
    assert "transparent_bg_unsupported" in result.blocker_codes
    assert any("transparent" in m for m in result.blockers)


def test_input_fidelity_extra_param_blocks() -> None:
    result = preflight(
        "a cat",
        extra_params={"input_fidelity": "high"},
    )
    assert result.passed is False
    assert "input_fidelity_unsupported" in result.blocker_codes


def test_size_too_small_blocks() -> None:
    result = preflight("a cat", size="100x100")
    assert result.passed is False
    # 100x100 violates BOTH the multiple-of-16 rule (depending on rule order)
    # and the min-pixel rule. Either resulting code is acceptable.
    assert any(
        c in result.blocker_codes
        for c in ("size_too_small", "size_too_large", "size_invalid")
    )


def test_size_too_large_blocks() -> None:
    result = preflight("a cat", size="4096x4096")
    assert result.passed is False
    assert "size_too_large" in result.blocker_codes


def test_clean_request_no_api_key_skips_moderation() -> None:
    result = preflight("a friendly golden retriever in a park")
    assert isinstance(result, PreflightResult)
    assert result.passed is True
    assert result.skipped_moderation is True
    assert result.blockers == []


def test_moderation_flag_blocks() -> None:
    cli = MagicMock()
    cli.moderations.create.return_value = _moderation_response(
        flagged=True, categories={"violence": True, "hate": False}
    )
    result = preflight("disallowed prompt", client=cli)
    assert result.moderation_flagged is True
    assert result.passed is False
    assert "violence" in result.moderation_categories


def test_moderation_clean_returns_passed() -> None:
    cli = MagicMock()
    cli.moderations.create.return_value = _moderation_response(
        flagged=False, categories={"violence": False}
    )
    result = preflight("a cat sleeping", client=cli)
    assert result.moderation_flagged is False
    assert result.skipped_moderation is False
    assert result.passed is True


def test_moderation_runtime_error_skipped(monkeypatch: pytest.MonkeyPatch) -> None:
    cli = MagicMock()
    cli.moderations.create.side_effect = RuntimeError("boom")
    result = preflight("a cat", client=cli)
    assert result.skipped_moderation is True
    assert result.passed is True


def test_skip_moderation_api_flag() -> None:
    cli = MagicMock()
    # Even though a client is supplied, the flag should bypass the call.
    result = preflight("a cat", client=cli, skip_moderation_api=True)
    cli.moderations.create.assert_not_called()
    assert result.skipped_moderation is True


def test_compression_with_png_blocks() -> None:
    result = preflight(
        "a cat", output_format="png", output_compression=80
    )
    assert result.passed is False
    assert "compression_format_mismatch" in result.blocker_codes


def test_warnings_for_experimental_size() -> None:
    # 3072x1024 is allowed (multiple of 16, aspect 3:1, edges < 3840) but
    # exceeds the experimental long-edge cap of 2560 — should add a warning.
    result = preflight("a banner", size="3072x1024")
    assert result.passed is True
    assert any("experimental" in w for w in result.warnings)


def test_blocker_does_not_raise_on_bad_inputs() -> None:
    # Multiple stacked failures: no exception escapes.
    result = preflight(
        "a cat",
        size="not-a-size",
        background="transparent",
        output_format="png",
        output_compression=50,
        extra_params={"input_fidelity": "high"},
    )
    assert result.passed is False
    assert len(result.blockers) >= 3
