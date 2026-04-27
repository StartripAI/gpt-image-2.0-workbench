# SPDX-License-Identifier: Apache-2.0
"""Per-record provenance metadata for normalized corpus entries.

A `ProvenanceRecord` represents one third-party prompt observation: where it
came from, who authored it, and what license posture it carries. By default
records are metadata-only — we store URLs and tags, not prompt text — and
`license_audit` flags any record that violates that invariant.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class ProvenanceRecord(BaseModel):
    record_id: str
    source_id: str
    source_url: str
    author: str | None = None
    captured_at: datetime
    language: str | None = None
    license_declared: str | None = None
    license_observed: str | None = None
    license_status: Literal["clear", "ambiguous", "metadata_only"]
    redistributable: Literal["none", "with_attribution", "unrestricted"]
    metadata_only: bool = True
    tags: list[str] = Field(default_factory=list)
    notes: str = ""


def write_jsonl(records: list[ProvenanceRecord], path: Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for record in records:
            fh.write(record.model_dump_json())
            fh.write("\n")


def read_jsonl(path: Path) -> list[ProvenanceRecord]:
    path = Path(path)
    out: list[ProvenanceRecord] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            out.append(ProvenanceRecord.model_validate(json.loads(line)))
    return out


def license_audit(records: list[ProvenanceRecord]) -> list[str]:
    findings: list[str] = []
    for record in records:
        if record.license_status == "ambiguous":
            findings.append(f"{record.record_id}: license_status is ambiguous")
        if (
            record.license_declared is not None
            and record.license_observed is not None
            and record.license_declared != record.license_observed
        ):
            findings.append(
                f"{record.record_id}: license_declared != license_observed "
                f"({record.license_declared!r} vs {record.license_observed!r})"
            )
        if not record.metadata_only and record.redistributable == "none":
            findings.append(
                f"{record.record_id}: full-text storage (metadata_only=False) "
                f"with redistributable=none"
            )
        if not record.metadata_only and record.license_status != "clear":
            findings.append(
                f"{record.record_id}: full-text storage requires clear license, "
                f"got {record.license_status!r}"
            )
    return findings
