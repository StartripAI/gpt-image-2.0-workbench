# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the production-observability ledger."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from image2_workbench.ledger import (
    AggregateRow,
    LedgerEntry,
    aggregate,
    append_entry,
    drift,
    ledger_path,
    read_entries,
    top_failures,
)


def _entry(
    *,
    template_id: str | None = "tpl-a",
    snapshot: str | None = "gpt-image-2-2026-04-21",
    status: str = "ok",
    latency_ms: int | None = 1000,
    cost_usd: float | None = 0.05,
    error_code: str | None = None,
    kind: str = "generate",
    when: datetime | None = None,
) -> LedgerEntry:
    return LedgerEntry(
        timestamp=when or datetime.now(UTC),
        kind=kind,  # type: ignore[arg-type]
        template_id=template_id,
        snapshot=snapshot,
        status=status,  # type: ignore[arg-type]
        latency_ms=latency_ms,
        cost_usd=cost_usd,
        error_code=error_code,
    )


def test_append_and_read_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "ledger.jsonl"
    e1 = _entry()
    e2 = _entry(status="error", error_code="rate_limited", latency_ms=200, cost_usd=0)
    append_entry(e1, path=path)
    append_entry(e2, path=path)
    out = read_entries(path)
    assert len(out) == 2
    assert out[0].status == "ok"
    assert out[1].error_code == "rate_limited"


def test_append_creates_parent_dir(tmp_path: Path) -> None:
    nested = tmp_path / "deep" / "ledger.jsonl"
    append_entry(_entry(), path=nested)
    assert nested.exists()


def test_read_missing_file_returns_empty(tmp_path: Path) -> None:
    assert read_entries(tmp_path / "nope.jsonl") == []


def test_read_tolerates_malformed_lines(tmp_path: Path) -> None:
    path = tmp_path / "ledger.jsonl"
    append_entry(_entry(), path=path)
    with path.open("a", encoding="utf-8") as fh:
        fh.write("this is not json\n")
        fh.write('{"kind":"generate","status":"ok"}\n')  # missing required fields? no, optional
        fh.write("\n")  # blank line
    entries = read_entries(path)
    # The malformed plain-text line is skipped; valid lines (1 + 1 partial) parse.
    assert len(entries) >= 1


def test_aggregate_success_rate_mixed(tmp_path: Path) -> None:
    entries = [
        _entry(template_id="tpl-a", status="ok"),
        _entry(template_id="tpl-a", status="ok"),
        _entry(template_id="tpl-a", status="error", error_code="rate_limited"),
        _entry(template_id="tpl-b", status="error", error_code="auth_error"),
    ]
    rows = aggregate(entries, group_by="template")
    by_id = {r.template_id: r for r in rows}
    assert by_id["tpl-a"].total == 3
    assert by_id["tpl-a"].ok == 2
    assert by_id["tpl-a"].error == 1
    assert by_id["tpl-a"].success_rate == pytest.approx(2 / 3)
    assert by_id["tpl-b"].success_rate == 0.0
    assert by_id["tpl-a"].error_code_breakdown == {"rate_limited": 1}


def test_aggregate_percentiles_from_sorted_list() -> None:
    # Eleven latencies 100..1100 in increasing 100-ms steps.
    entries = [
        _entry(template_id="tpl-a", status="ok", latency_ms=v)
        for v in range(100, 1200, 100)
    ]
    rows = aggregate(entries, group_by="template")
    assert len(rows) == 1
    row = rows[0]
    assert row.p50_latency_ms is not None
    assert row.p95_latency_ms is not None
    # p50 should be in the middle band; p95 should be at or near the top.
    assert 500 <= row.p50_latency_ms <= 700
    assert row.p95_latency_ms >= 1000


def test_aggregate_group_by_template_snapshot() -> None:
    entries = [
        _entry(template_id="tpl-a", snapshot="snap-1"),
        _entry(template_id="tpl-a", snapshot="snap-2"),
        _entry(template_id="tpl-a", snapshot="snap-1"),
    ]
    rows = aggregate(entries, group_by="template_snapshot")
    assert len(rows) == 2
    by_key = {(r.template_id, r.snapshot): r for r in rows}
    assert by_key[("tpl-a", "snap-1")].total == 2
    assert by_key[("tpl-a", "snap-2")].total == 1


def test_aggregate_total_cost(tmp_path: Path) -> None:
    entries = [
        _entry(template_id="tpl-a", cost_usd=0.05),
        _entry(template_id="tpl-a", cost_usd=0.20),
        _entry(template_id="tpl-a", cost_usd=None),  # null cost ignored
    ]
    rows = aggregate(entries, group_by="template")
    assert rows[0].total_cost_usd == pytest.approx(0.25)


def test_aggregate_filter_by_template() -> None:
    entries = [
        _entry(template_id="tpl-a"),
        _entry(template_id="tpl-b"),
    ]
    rows = aggregate(entries, template_id="tpl-a", group_by="template")
    assert len(rows) == 1
    assert rows[0].template_id == "tpl-a"


def test_aggregate_filter_since() -> None:
    now = datetime.now(UTC)
    old = _entry(template_id="tpl-a", when=now - timedelta(days=10))
    fresh = _entry(template_id="tpl-a", when=now)
    rows = aggregate(
        [old, fresh],
        since=now - timedelta(days=1),
        group_by="template",
    )
    assert rows[0].total == 1


def test_top_failures_orders_by_failure_rate_then_total() -> None:
    entries = [
        # tpl-a: 5/5 errors -> failure_rate 1.0
        *[_entry(template_id="tpl-a", status="error", error_code="x") for _ in range(5)],
        # tpl-b: 1/2 errors -> failure_rate 0.5
        _entry(template_id="tpl-b", status="ok"),
        _entry(template_id="tpl-b", status="error", error_code="x"),
        # tpl-c: 0/1 errors -> failure_rate 0.0
        _entry(template_id="tpl-c", status="ok"),
    ]
    rows = top_failures(entries, limit=10)
    # First row should be tpl-a (highest failure rate)
    assert rows[0].template_id == "tpl-a"
    # tpl-b should come before tpl-c (higher failure rate)
    ids = [r.template_id for r in rows]
    assert ids.index("tpl-b") < ids.index("tpl-c")


def test_top_failures_respects_limit() -> None:
    entries = [
        _entry(template_id=f"tpl-{i}", status="error", error_code="x")
        for i in range(5)
    ]
    rows = top_failures(entries, limit=2)
    assert len(rows) == 2


def test_drift_compares_snapshots() -> None:
    entries = [
        # baseline: tpl-a 100% ok
        _entry(template_id="tpl-a", snapshot="snap-base", status="ok"),
        _entry(template_id="tpl-a", snapshot="snap-base", status="ok"),
        # candidate: tpl-a 50% ok
        _entry(template_id="tpl-a", snapshot="snap-cand", status="ok"),
        _entry(template_id="tpl-a", snapshot="snap-cand", status="error", error_code="x"),
        # tpl-b only in baseline -> should not appear in drift
        _entry(template_id="tpl-b", snapshot="snap-base", status="ok"),
    ]
    records = drift(
        entries,
        baseline_snapshot="snap-base",
        candidate_snapshot="snap-cand",
    )
    assert len(records) == 1
    rec = records[0]
    assert rec["template_id"] == "tpl-a"
    assert rec["baseline_success_rate"] == 1.0
    assert rec["candidate_success_rate"] == 0.5
    assert rec["delta"] == pytest.approx(-0.5)


def test_ledger_path_env_override(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "custom.jsonl"
    monkeypatch.setenv("IMAGE2_LEDGER_PATH", str(target))
    assert ledger_path() == target


def test_ledger_path_default_when_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("IMAGE2_LEDGER_PATH", raising=False)
    assert ledger_path() == Path.home() / ".image2" / "ledger.jsonl"


def test_aggregate_row_pydantic_shape() -> None:
    # Ensures the public model exposes expected fields for downstream tooling.
    row = AggregateRow(total=0, ok=0, error=0, success_rate=0.0, total_cost_usd=0.0)
    dumped = row.model_dump()
    for key in (
        "template_id",
        "snapshot",
        "total",
        "ok",
        "error",
        "success_rate",
        "p50_latency_ms",
        "p95_latency_ms",
        "total_cost_usd",
        "error_code_breakdown",
    ):
        assert key in dumped
