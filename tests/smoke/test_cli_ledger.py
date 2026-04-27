# SPDX-License-Identifier: Apache-2.0
"""Smoke tests for the `i2w ledger` Typer app.

Invoked directly against ``ledger_app`` so they're independent of cli.py
registration (X4 wires the root CLI later).
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from image2_workbench.commands.ledger import ledger_app
from image2_workbench.ledger import LedgerEntry, append_entry

runner = CliRunner()


def _seed(path: Path) -> None:
    """Seed a tmp ledger with three representative entries."""
    entries = [
        LedgerEntry(
            kind="generate",
            template_id="tpl-a",
            snapshot="gpt-image-2-2026-04-21",
            status="ok",
            latency_ms=1200,
            cost_usd=0.05,
            size="1024x1024",
            quality="medium",
            n=1,
        ),
        LedgerEntry(
            kind="generate",
            template_id="tpl-a",
            snapshot="gpt-image-2-2026-04-21",
            status="error",
            latency_ms=300,
            cost_usd=0.0,
            size="1024x1024",
            quality="medium",
            n=1,
            error_code="rate_limited",
            error_exit_code=2,
        ),
        LedgerEntry(
            kind="edit",
            template_id="tpl-b",
            snapshot="gpt-image-2-2026-04-21",
            status="ok",
            latency_ms=2200,
            cost_usd=0.21,
            size="1024x1024",
            quality="high",
            n=1,
        ),
    ]
    for e in entries:
        append_entry(e, path=path)


@pytest.fixture()
def tmp_ledger(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Path:
    target = tmp_path / "ledger.jsonl"
    monkeypatch.setenv("IMAGE2_LEDGER_PATH", str(target))
    _seed(target)
    return target


def test_ledger_query_outputs_table(tmp_ledger: Path) -> None:
    result = runner.invoke(ledger_app, ["query"])
    assert result.exit_code == 0, result.stdout
    assert "success_rate" in result.stdout
    assert "cost_per_output" in result.stdout
    assert "rate_limited:1" in result.stdout


def test_ledger_query_filter_by_template(tmp_ledger: Path) -> None:
    result = runner.invoke(ledger_app, ["query", "--template", "tpl-a"])
    assert result.exit_code == 0, result.stdout
    assert "tpl-a" in result.stdout


def test_ledger_top_failures(tmp_ledger: Path) -> None:
    result = runner.invoke(ledger_app, ["top-failures", "--limit", "2"])
    assert result.exit_code == 0, result.stdout
    # tpl-a has the only error in the seed -> appears in top-failures.
    assert "tpl-a" in result.stdout


def test_ledger_drift(tmp_ledger: Path) -> None:
    # Add a candidate snapshot for the same templates so drift has overlap.
    cand = LedgerEntry(
        kind="generate",
        template_id="tpl-a",
        snapshot="gpt-image-2-2026-05-01",
        status="ok",
        latency_ms=900,
        cost_usd=0.05,
    )
    append_entry(cand, path=tmp_ledger)
    result = runner.invoke(
        ledger_app,
        [
            "drift",
            "--baseline",
            "gpt-image-2-2026-04-21",
            "--candidate",
            "gpt-image-2-2026-05-01",
        ],
    )
    assert result.exit_code == 0, result.stdout
    # Either there is a comparable template or the table is rendered.
    assert "tpl-a" in result.stdout or "drift" in result.stdout


def test_ledger_export_csv(tmp_ledger: Path, tmp_path: Path) -> None:
    out = tmp_path / "x.csv"
    result = runner.invoke(
        ledger_app, ["export", "--out", str(out), "--format", "csv"]
    )
    assert result.exit_code == 0, result.stdout
    assert out.exists()
    with out.open("r", encoding="utf-8", newline="") as fh:
        rows = list(csv.reader(fh))
    # Header + 3 data rows seeded above.
    assert rows[0][0] == "timestamp"
    assert len(rows) == 4
    # status column should contain ok/error values.
    status_idx = rows[0].index("status")
    statuses = {row[status_idx] for row in rows[1:]}
    assert statuses <= {"ok", "error"}


def test_ledger_export_jsonl(tmp_ledger: Path, tmp_path: Path) -> None:
    out = tmp_path / "x.jsonl"
    result = runner.invoke(
        ledger_app, ["export", "--out", str(out), "--format", "jsonl"]
    )
    assert result.exit_code == 0, result.stdout
    lines = out.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 3
    parsed = [json.loads(line) for line in lines]
    assert all("kind" in row for row in parsed)


def test_ledger_query_empty_ledger(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "empty.jsonl"
    monkeypatch.setenv("IMAGE2_LEDGER_PATH", str(target))
    result = runner.invoke(ledger_app, ["query"])
    assert result.exit_code == 0, result.stdout
    assert "empty" in result.stdout.lower() or "missing" in result.stdout.lower()
