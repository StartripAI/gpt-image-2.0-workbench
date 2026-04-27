# SPDX-License-Identifier: Apache-2.0
"""Smoke test: `i2w doctor capabilities` must not crash without an API key."""

import pytest
from typer.testing import CliRunner

from image2_workbench.cli import app

runner = CliRunner()


def test_doctor_capabilities_no_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    result = runner.invoke(app, ["doctor", "capabilities"])
    assert result.exit_code == 0, result.stdout
    assert "capabilit" in result.stdout.lower()
