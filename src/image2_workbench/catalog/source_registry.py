# SPDX-License-Identifier: Apache-2.0
"""Upstream-source registry for corpora the project ingests metadata from.

The registry is metadata-only by policy: we record where prompt-engineering
ideas came from so we can audit license posture, but we never redistribute
upstream prompt text from sources marked `redistributable: none`.
"""
from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field

LicenseStatus = Literal["clear", "ambiguous", "metadata_only"]
Redistributable = Literal["none", "with_attribution", "unrestricted"]
SourceKind = Literal["official", "github_repo", "community_post", "docs_mirror"]


class SourceEntry(BaseModel):
    id: str
    kind: SourceKind
    url: str
    license_declared: str
    license_observed: str
    license_status: LicenseStatus
    redistributable: Redistributable
    use: str
    notes: str = ""


class SourceRegistry(BaseModel):
    sources: list[SourceEntry] = Field(default_factory=list)

    def find(self, source_id: str) -> SourceEntry | None:
        for entry in self.sources:
            if entry.id == source_id:
                return entry
        return None

    def filter_redistributable(self) -> list[SourceEntry]:
        return [e for e in self.sources if e.redistributable != "none"]

    def audit(self) -> list[str]:
        """Return human-readable audit findings.

        We surface license posture problems that a human reviewer should look at
        before this project ships any derived corpus: ambiguous license status,
        declared/observed mismatches, and impossible combinations like
        `metadata_only` license status paired with broader redistribution rights
        (which would imply we're claiming permission we cannot demonstrate).
        """
        findings: list[str] = []
        seen_ids: set[str] = set()
        for entry in self.sources:
            if entry.id in seen_ids:
                findings.append(f"{entry.id}: duplicate id in registry")
            seen_ids.add(entry.id)
            if entry.license_status == "ambiguous":
                findings.append(f"{entry.id}: license_status is ambiguous")
            if entry.license_declared != entry.license_observed:
                findings.append(
                    f"{entry.id}: license_declared != license_observed "
                    f"({entry.license_declared!r} vs {entry.license_observed!r})"
                )
            if entry.license_status == "metadata_only" and entry.redistributable != "none":
                findings.append(
                    f"{entry.id}: metadata_only status implies redistributable=none, "
                    f"got {entry.redistributable!r}"
                )
        return findings


DEFAULT_REGISTRY = Path("corpus/manifests/source_registry.yml")


def load_registry(path: Path = DEFAULT_REGISTRY) -> SourceRegistry:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ValueError(f"registry root must be a mapping, got {type(raw).__name__}")
    return SourceRegistry.model_validate(raw)
