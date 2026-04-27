# SPDX-License-Identifier: Apache-2.0
"""`i2w ledger` — query, summarize, and export the local observability ledger."""
from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from ..ledger import (
    aggregate,
    drift,
    ledger_path,
    read_entries,
    top_failures,
)

ledger_app = typer.Typer(
    no_args_is_help=True,
    help="Query and summarize the local production observability ledger.",
)


def _parse_since(value: str | None) -> datetime | None:
    if not value:
        return None
    # Accept date-only YYYY-MM-DD and full ISO timestamps.
    try:
        if len(value) == 10:
            return datetime.fromisoformat(f"{value}T00:00:00+00:00")
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise typer.BadParameter(f"invalid --since: {value!r} ({exc})") from exc


def _aggregate_table(rows, *, title: str) -> Table:
    table = Table(title=title)
    table.add_column("template_id")
    table.add_column("snapshot")
    table.add_column("total", justify="right")
    table.add_column("ok", justify="right")
    table.add_column("error", justify="right")
    table.add_column("success_rate", justify="right")
    table.add_column("p50_ms", justify="right")
    table.add_column("p95_ms", justify="right")
    table.add_column("cost_usd", justify="right")
    for r in rows:
        table.add_row(
            r.template_id or "-",
            r.snapshot or "-",
            str(r.total),
            str(r.ok),
            str(r.error),
            f"{r.success_rate:.3f}",
            "-" if r.p50_latency_ms is None else str(r.p50_latency_ms),
            "-" if r.p95_latency_ms is None else str(r.p95_latency_ms),
            f"{r.total_cost_usd:.4f}",
        )
    return table


@ledger_app.command("query")
def query(
    template: Annotated[
        str | None, typer.Option("--template", help="Filter by template id")
    ] = None,
    since: Annotated[
        str | None, typer.Option("--since", help="ISO date e.g. 2026-01-01")
    ] = None,
    group_by: Annotated[
        str,
        typer.Option(
            "--group-by", help="template | snapshot | template_snapshot"
        ),
    ] = "template",
) -> None:
    """Print an aggregate table from the ledger."""
    console = Console()
    entries = read_entries()
    if not entries:
        console.print(
            f"ledger {ledger_path()} is empty or missing", markup=False
        )
        return
    since_dt = _parse_since(since)
    rows = aggregate(
        entries, template_id=template, since=since_dt, group_by=group_by
    )
    if not rows:
        console.print("no rows match the filter", markup=False)
        return
    console.print(
        _aggregate_table(rows, title=f"ledger query (group_by={group_by})")
    )
    console.print(
        "columns: template_id snapshot total ok error success_rate p50_ms p95_ms cost_usd",
        markup=False,
    )


@ledger_app.command("top-failures")
def top_failures_cmd(
    limit: Annotated[int, typer.Option("--limit")] = 10,
) -> None:
    """Print the worst-performing template/snapshot pairs."""
    console = Console()
    entries = read_entries()
    if not entries:
        console.print(
            f"ledger {ledger_path()} is empty or missing", markup=False
        )
        return
    rows = top_failures(entries, limit=limit)
    console.print(_aggregate_table(rows, title=f"top-failures (limit={limit})"))


@ledger_app.command("drift")
def drift_cmd(
    baseline: Annotated[str, typer.Option("--baseline")],
    candidate: Annotated[str, typer.Option("--candidate")],
) -> None:
    """Compare success rate per template across two snapshots."""
    console = Console()
    entries = read_entries()
    if not entries:
        console.print(
            f"ledger {ledger_path()} is empty or missing", markup=False
        )
        return
    records = drift(
        entries, baseline_snapshot=baseline, candidate_snapshot=candidate
    )
    if not records:
        console.print(
            "no templates have entries in both baseline and candidate snapshots",
            markup=False,
        )
        return
    table = Table(title=f"drift {baseline} -> {candidate}")
    table.add_column("template_id")
    table.add_column("baseline_success_rate", justify="right")
    table.add_column("candidate_success_rate", justify="right")
    table.add_column("delta", justify="right")
    table.add_column("baseline_total", justify="right")
    table.add_column("candidate_total", justify="right")
    for rec in records:
        table.add_row(
            rec["template_id"] or "-",
            f"{rec['baseline_success_rate']:.3f}",
            f"{rec['candidate_success_rate']:.3f}",
            f"{rec['delta']:+.3f}",
            str(rec["baseline_total"]),
            str(rec["candidate_total"]),
        )
    console.print(table)


@ledger_app.command("export")
def export(
    out: Annotated[Path, typer.Option("--out")],
    format_: Annotated[
        str, typer.Option("--format", help="csv | jsonl")
    ] = "csv",
) -> None:
    """Export raw ledger entries to ``--out`` in CSV or JSONL form."""
    console = Console()
    entries = read_entries()
    out.parent.mkdir(parents=True, exist_ok=True)
    fmt = format_.lower()
    if fmt == "jsonl":
        with out.open("w", encoding="utf-8") as fh:
            for entry in entries:
                fh.write(
                    json.dumps(
                        entry.model_dump(mode="json"),
                        separators=(",", ":"),
                        ensure_ascii=False,
                    )
                    + "\n"
                )
    elif fmt == "csv":
        fields = [
            "timestamp",
            "kind",
            "template_id",
            "snapshot",
            "status",
            "latency_ms",
            "cost_usd",
            "size",
            "quality",
            "n",
            "error_code",
            "error_exit_code",
            "extra",
        ]
        with out.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fields)
            writer.writeheader()
            for entry in entries:
                row = entry.model_dump(mode="json")
                row["extra"] = json.dumps(row.get("extra") or {}, separators=(",", ":"))
                writer.writerow({k: row.get(k, "") for k in fields})
    else:
        raise typer.BadParameter(f"unknown --format {format_!r}; want csv or jsonl")
    console.print(
        f"wrote {len(entries)} entries to {out} ({fmt})", markup=False
    )
