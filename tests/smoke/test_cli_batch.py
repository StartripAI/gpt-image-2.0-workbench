# SPDX-License-Identifier: Apache-2.0
"""Smoke tests for the V1.5 ``i2w batch`` CLI surface.

We invoke the ``batch_app`` Typer sub-app directly. Real network calls
are avoided: tests use ``--dry-run`` for sweep, and ``status`` against
unknown ids relies on the SDK refusing a request that we never let
escape (no OPENAI_API_KEY in test env → :class:`BatchApiError`).
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from typer.testing import CliRunner

from image2_workbench.commands.batch import batch_app

runner = CliRunner()

REPO_ROOT = Path(__file__).resolve().parents[2]
SWOT_VARS = REPO_ROOT / "templates" / "business" / "_vars_examples" / "swot_acme.yml"


@pytest.fixture(autouse=True)
def _tmp_ledger(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IMAGE2_LEDGER_PATH", str(tmp_path / "ledger.jsonl"))


def test_sweep_dry_run_with_real_template_and_vars() -> None:
    assert SWOT_VARS.exists(), f"expected demo vars at {SWOT_VARS}"
    result = runner.invoke(
        batch_app,
        [
            "sweep",
            "--template",
            "business_swot_card",
            "--vars",
            str(SWOT_VARS),
            "--route",
            "batch-api",
            "--dry-run",
        ],
    )
    assert result.exit_code == 0, (result.stdout, result.stderr)
    assert "dry-run" in result.stdout.lower()
    assert "total_estimated=$" in result.stdout
    assert "batch_jsonl:" in result.stdout
    assert "\"url\": \"/v1/images/generations\"" in result.stdout


def test_sweep_dry_run_immediate_route() -> None:
    assert SWOT_VARS.exists()
    result = runner.invoke(
        batch_app,
        [
            "sweep",
            "--template",
            "business_swot_card",
            "--vars",
            str(SWOT_VARS),
            "--route",
            "immediate",
            "--dry-run",
        ],
    )
    assert result.exit_code == 0, (result.stdout, result.stderr)
    assert "dry-run" in result.stdout.lower()


def test_sweep_invalid_route_rejected() -> None:
    assert SWOT_VARS.exists()
    result = runner.invoke(
        batch_app,
        [
            "sweep",
            "--template",
            "business_swot_card",
            "--vars",
            str(SWOT_VARS),
            "--route",
            "carrier-pigeon",
            "--dry-run",
        ],
    )
    assert result.exit_code != 0


def test_sweep_invalid_size_rejected_before_submission() -> None:
    assert SWOT_VARS.exists()
    result = runner.invoke(
        batch_app,
        [
            "sweep",
            "--template",
            "business_swot_card",
            "--vars",
            str(SWOT_VARS),
            "--sizes",
            "4096x4096",
            "--route",
            "batch-api",
            "--dry-run",
        ],
    )
    assert result.exit_code == 4, (result.stdout, result.stderr)
    assert "invalid batch request" in result.stderr


def test_sweep_unknown_template_rejected(tmp_path: Path) -> None:
    vars_file = tmp_path / "v.yml"
    vars_file.write_text("company_name: x\n", encoding="utf-8")
    result = runner.invoke(
        batch_app,
        [
            "sweep",
            "--template",
            "no_such_template_xyz",
            "--vars",
            str(vars_file),
            "--dry-run",
        ],
    )
    assert result.exit_code != 0


def test_status_with_no_credentials_returns_nonzero() -> None:
    # Force the API call to fail without our control by removing any
    # ambient API key, then asking for an obviously-fake batch id.
    saved = os.environ.pop("OPENAI_API_KEY", None)
    try:
        result = runner.invoke(batch_app, ["status", "nonexistent_id"])
    finally:
        if saved is not None:
            os.environ["OPENAI_API_KEY"] = saved
    assert result.exit_code != 0


def test_status_empty_id_rejected() -> None:
    result = runner.invoke(batch_app, ["status", ""])
    assert result.exit_code != 0


def test_fetch_with_no_credentials_returns_nonzero(tmp_path: Path) -> None:
    saved = os.environ.pop("OPENAI_API_KEY", None)
    try:
        result = runner.invoke(
            batch_app,
            ["fetch", "nonexistent_id", "--out-dir", str(tmp_path / "out")],
        )
    finally:
        if saved is not None:
            os.environ["OPENAI_API_KEY"] = saved
    assert result.exit_code != 0
