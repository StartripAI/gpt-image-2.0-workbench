# SPDX-License-Identifier: Apache-2.0
"""Smoke tests for granular exit codes and the doctor's Will-Fail Patterns.

These tests run the real CLI through Typer's ``CliRunner`` so they exercise
the same code path as a user typing ``i2w doctor capabilities``.
"""

from __future__ import annotations

import pytest
from typer.testing import CliRunner

from image2_workbench.cli import app

runner = CliRunner()


def test_doctor_capabilities_exits_zero(monkeypatch: pytest.MonkeyPatch) -> None:
    """Probe is informational — exit code is always 0, even without an API key."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    result = runner.invoke(app, ["doctor", "capabilities"])
    assert result.exit_code == 0, result.stdout


def test_doctor_capabilities_lists_will_fail_patterns(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The Will-Fail Patterns block must surface input_fidelity and transparent."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    result = runner.invoke(app, ["doctor", "capabilities"])
    assert result.exit_code == 0, result.stdout
    out = result.stdout
    assert "Will-Fail Patterns" in out
    assert "input_fidelity" in out
    assert "transparent" in out
