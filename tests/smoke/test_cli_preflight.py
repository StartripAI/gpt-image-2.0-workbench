# SPDX-License-Identifier: Apache-2.0
"""Smoke tests for the `i2w preflight` Typer app.

These call ``preflight_app`` directly via Typer's CliRunner so they pass even
before ``cli.py`` registers the new sub-app (X4 wires the registration).
"""
from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from image2_workbench.commands.preflight import preflight_app

runner = CliRunner()


@pytest.fixture(autouse=True)
def _no_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)


def test_preflight_clean_prompt_passes(tmp_path: Path) -> None:
    prompt_file = tmp_path / "prompt.md"
    prompt_file.write_text("a friendly golden retriever in a park", encoding="utf-8")
    result = runner.invoke(preflight_app, ["run", str(prompt_file)])
    assert result.exit_code == 0, result.stdout
    assert "passed: True" in result.stdout
    assert "skipped_moderation: True" in result.stdout


def test_preflight_transparent_background_exits_4(tmp_path: Path) -> None:
    prompt_file = tmp_path / "prompt.md"
    prompt_file.write_text("a clean cutout product photo", encoding="utf-8")
    result = runner.invoke(
        preflight_app, ["run", str(prompt_file), "--background", "transparent"]
    )
    assert result.exit_code == 4, result.stdout
    assert "transparent" in result.stdout.lower()


def test_preflight_input_fidelity_exits_4_via_size_too_large(
    tmp_path: Path,
) -> None:
    """A 4096x4096 size is clearly oversized; preflight must exit 4."""
    prompt_file = tmp_path / "prompt.md"
    prompt_file.write_text("a logo", encoding="utf-8")
    result = runner.invoke(
        preflight_app, ["run", str(prompt_file), "--size", "4096x4096"]
    )
    assert result.exit_code == 4, result.stdout
    assert "size_too_large" in result.stdout


def test_preflight_missing_prompt_file_exits_4(tmp_path: Path) -> None:
    result = runner.invoke(preflight_app, ["run", str(tmp_path / "missing.md")])
    assert result.exit_code == 4, result.stdout


def test_preflight_no_moderation_api_flag(tmp_path: Path) -> None:
    prompt_file = tmp_path / "prompt.md"
    prompt_file.write_text("a cat", encoding="utf-8")
    result = runner.invoke(
        preflight_app, ["run", str(prompt_file), "--no-moderation-api"]
    )
    assert result.exit_code == 0, result.stdout
    assert "skipped_moderation: True" in result.stdout
