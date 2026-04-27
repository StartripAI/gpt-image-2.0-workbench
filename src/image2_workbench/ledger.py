# SPDX-License-Identifier: Apache-2.0
"""Append-only JSONL ledger for production observability.

Every render/edit/preflight/batch call appends one record. Aggregation queries
operate on the local ledger to compute success rate, latency percentiles, cost,
and per-snapshot regression signals.

Path: ``$IMAGE2_LEDGER_PATH`` or ``~/.image2/ledger.jsonl``.
"""
from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

CallKind = Literal["generate", "edit", "preflight", "batch_submit", "batch_fetch"]
CallStatus = Literal["ok", "error"]


class LedgerEntry(BaseModel):
    """One row in the local production-observability ledger."""

    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    kind: CallKind
    template_id: str | None = None
    snapshot: str | None = None
    status: CallStatus
    latency_ms: int | None = None
    cost_usd: float | None = None
    size: str | None = None
    quality: str | None = None
    n: int | None = None
    error_code: str | None = None
    error_exit_code: int | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


DEFAULT_LEDGER_PATH = Path.home() / ".image2" / "ledger.jsonl"


def ledger_path() -> Path:
    """Resolve the active ledger path, honouring ``IMAGE2_LEDGER_PATH``."""
    override = os.environ.get("IMAGE2_LEDGER_PATH")
    return Path(override) if override else DEFAULT_LEDGER_PATH


def append_entry(entry: LedgerEntry, *, path: Path | None = None) -> Path:
    """Append-only write. Creates the parent directory if missing.

    The file is opened in line-buffered append mode so concurrent writers do
    not interleave bytes within a single record. Returns the resolved path.
    """
    target = path if path is not None else ledger_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = entry.model_dump(mode="json")
    line = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    with target.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")
    return target


def read_entries(path: Path | None = None) -> list[LedgerEntry]:
    """Read all entries; silently skip any line that fails to parse."""
    target = path if path is not None else ledger_path()
    if not target.exists():
        return []
    out: list[LedgerEntry] = []
    with target.open("r", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                out.append(LedgerEntry.model_validate(obj))
            except Exception:  # noqa: BLE001 — be tolerant of malformed history
                continue
    return out


# --------------------------------------------------------------------------- #
# Aggregation
# --------------------------------------------------------------------------- #


class AggregateRow(BaseModel):
    template_id: str | None = None
    snapshot: str | None = None
    total: int
    ok: int
    error: int
    success_rate: float
    p50_latency_ms: int | None = None
    p95_latency_ms: int | None = None
    total_cost_usd: float
    error_code_breakdown: dict[str, int] = Field(default_factory=dict)


def _percentile(values: list[int], pct: float) -> int | None:
    """Return the integer percentile of ``values``; nearest-rank method."""
    if not values:
        return None
    sorted_vals = sorted(values)
    if len(sorted_vals) == 1:
        return int(sorted_vals[0])
    # nearest-rank, stable across small N
    rank = max(1, int((pct / 100.0) * len(sorted_vals) + 0.5))
    rank = min(rank, len(sorted_vals))
    return int(sorted_vals[rank - 1])


def _group_key(
    entry: LedgerEntry, group_by: str
) -> tuple[str | None, str | None]:
    if group_by == "template":
        return entry.template_id, None
    if group_by == "snapshot":
        return None, entry.snapshot
    if group_by == "template_snapshot":
        return entry.template_id, entry.snapshot
    raise ValueError(f"unknown group_by={group_by!r}")


def aggregate(
    entries: list[LedgerEntry],
    *,
    template_id: str | None = None,
    since: datetime | None = None,
    group_by: Literal["template", "snapshot", "template_snapshot"] = "template",
) -> list[AggregateRow]:
    """Group ``entries`` and compute per-group metrics.

    Filters by ``template_id`` and ``since`` first, then groups by the
    requested key. Latency percentiles are computed only over entries that
    carry a non-null ``latency_ms``. ``total_cost_usd`` sums every non-null
    ``cost_usd`` in the group.
    """
    buckets: dict[
        tuple[str | None, str | None],
        list[LedgerEntry],
    ] = {}
    for entry in entries:
        if template_id is not None and entry.template_id != template_id:
            continue
        if since is not None and entry.timestamp < since:
            continue
        key = _group_key(entry, group_by)
        buckets.setdefault(key, []).append(entry)

    rows: list[AggregateRow] = []
    for (tid, snap), bucket in buckets.items():
        total = len(bucket)
        ok = sum(1 for e in bucket if e.status == "ok")
        err = total - ok
        latencies = [e.latency_ms for e in bucket if e.latency_ms is not None]
        cost_total = sum((e.cost_usd or 0.0) for e in bucket)
        breakdown: dict[str, int] = {}
        for e in bucket:
            if e.status == "error" and e.error_code:
                breakdown[e.error_code] = breakdown.get(e.error_code, 0) + 1
        success_rate = (ok / total) if total else 0.0
        rows.append(
            AggregateRow(
                template_id=tid,
                snapshot=snap,
                total=total,
                ok=ok,
                error=err,
                success_rate=success_rate,
                p50_latency_ms=_percentile(latencies, 50.0),
                p95_latency_ms=_percentile(latencies, 95.0),
                total_cost_usd=round(cost_total, 6),
                error_code_breakdown=breakdown,
            )
        )

    # Stable, deterministic ordering for tests and table rendering.
    rows.sort(
        key=lambda r: (
            r.template_id or "",
            r.snapshot or "",
        )
    )
    return rows


def top_failures(
    entries: list[LedgerEntry], *, limit: int = 10
) -> list[AggregateRow]:
    """Return the worst-performing template/snapshot pairs.

    Sorted by ``1 - success_rate`` descending, then by ``total`` descending so
    high-volume failures rank above one-off blips.
    """
    rows = aggregate(entries, group_by="template_snapshot")
    rows.sort(key=lambda r: (-(1.0 - r.success_rate), -r.total))
    return rows[:limit]


def drift(
    entries: list[LedgerEntry],
    *,
    baseline_snapshot: str,
    candidate_snapshot: str,
) -> list[dict[str, Any]]:
    """Compare two snapshots; return one record per template seen in both."""
    base_rows = {
        r.template_id: r
        for r in aggregate(
            [e for e in entries if e.snapshot == baseline_snapshot],
            group_by="template",
        )
    }
    cand_rows = {
        r.template_id: r
        for r in aggregate(
            [e for e in entries if e.snapshot == candidate_snapshot],
            group_by="template",
        )
    }
    out: list[dict[str, Any]] = []
    for tid in sorted(set(base_rows) & set(cand_rows), key=lambda x: x or ""):
        base = base_rows[tid]
        cand = cand_rows[tid]
        out.append(
            {
                "template_id": tid,
                "baseline_success_rate": base.success_rate,
                "candidate_success_rate": cand.success_rate,
                "delta": cand.success_rate - base.success_rate,
                "baseline_total": base.total,
                "candidate_total": cand.total,
            }
        )
    return out
