# SPDX-License-Identifier: Apache-2.0
"""Smoke tests for the `i2w preflight` CLI contract."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from image2_workbench.cli import app
from image2_workbench.commands.preflight import preflight_app

runner = CliRunner()


@pytest.fixture(autouse=True)
def _no_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)


@pytest.fixture(autouse=True)
def _tmp_ledger(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IMAGE2_LEDGER_PATH", str(tmp_path / "ledger.jsonl"))


def test_preflight_clean_prompt_passes(tmp_path: Path) -> None:
    prompt_file = tmp_path / "prompt.md"
    prompt_file.write_text("a friendly golden retriever in a park", encoding="utf-8")
    result = runner.invoke(preflight_app, ["run", str(prompt_file)])
    assert result.exit_code == 0, result.stdout
    assert "passed: True" in result.stdout
    assert "skipped_moderation: True" in result.stdout


def test_preflight_direct_prompt_file_passes(tmp_path: Path) -> None:
    prompt_file = tmp_path / "prompt.md"
    prompt_file.write_text("a friendly product hero image", encoding="utf-8")
    ledger = tmp_path / "ledger.jsonl"
    result = runner.invoke(
        app,
        [
            "preflight",
            str(prompt_file),
            "--no-moderation-api",
            "--template-id",
            "business_swot_card",
        ],
    )
    assert result.exit_code == 0, (result.stdout, result.stderr)
    assert "passed: True" in result.stdout
    rows = [
        json.loads(line)
        for line in ledger.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert rows[-1]["template_id"] == "business_swot_card"


def test_preflight_legacy_run_prompt_file_passes(tmp_path: Path) -> None:
    prompt_file = tmp_path / "prompt.md"
    prompt_file.write_text("a friendly product hero image", encoding="utf-8")
    result = runner.invoke(
        app, ["preflight", "run", str(prompt_file), "--no-moderation-api"]
    )
    assert result.exit_code == 0, (result.stdout, result.stderr)
    assert "passed: True" in result.stdout


def test_preflight_transparent_background_exits_4(tmp_path: Path) -> None:
    prompt_file = tmp_path / "prompt.md"
    prompt_file.write_text("a clean cutout product photo", encoding="utf-8")
    result = runner.invoke(
        preflight_app, ["run", str(prompt_file), "--background", "transparent"]
    )
    assert result.exit_code == 4, result.stdout
    assert "transparent_bg_unsupported" in result.stderr


def test_preflight_input_fidelity_exits_4(
    tmp_path: Path,
) -> None:
    prompt_file = tmp_path / "prompt.md"
    prompt_file.write_text("a logo", encoding="utf-8")
    result = runner.invoke(
        app,
        [
            "preflight",
            str(prompt_file),
            "--input-fidelity",
            "high",
            "--no-moderation-api",
        ],
    )
    assert result.exit_code == 4, (result.stdout, result.stderr)
    assert "input_fidelity_unsupported" in result.stderr


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
