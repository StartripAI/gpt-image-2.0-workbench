# SPDX-License-Identifier: Apache-2.0
"""Local template index used by `i2w catalog list/search`.

V1 only walks `templates/<domain>/*.yml` on the filesystem; V2 will fold in
normalized corpus entries from `corpus/normalized/`.
"""
from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel

REPO_ROOT = Path(__file__).resolve().parents[3]
TEMPLATES_DIR = REPO_ROOT / "templates"

_SKIP_DIRS = {"_schema", "_vars_examples"}


class CatalogEntry(BaseModel):
    id: str
    domain: str
    path: Path
    description: str = ""
    artifact_type: str = ""
    grader_profile: str | None = None
    language_targets: list[str] = []
    license: str = ""


def _load_entry(path: Path, domain: str) -> CatalogEntry | None:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return None
    artifact = raw.get("artifact") or {}
    artifact_type = artifact.get("type", "") if isinstance(artifact, dict) else ""
    return CatalogEntry(
        id=str(raw.get("id") or path.stem),
        domain=str(raw.get("domain") or domain),
        path=path,
        description=str(raw.get("description") or ""),
        artifact_type=str(artifact_type or ""),
        grader_profile=raw.get("grader_profile"),
        language_targets=list(raw.get("language_targets") or []),
        license=str(raw.get("license") or ""),
    )


def scan_templates(root: Path | None = None) -> list[CatalogEntry]:
    base = Path(root) if root is not None else _resolve_templates_dir()
    entries: list[CatalogEntry] = []
    if not base.exists():
        return entries
    for domain_dir in sorted(p for p in base.iterdir() if p.is_dir()):
        if domain_dir.name in _SKIP_DIRS or domain_dir.name.startswith("."):
            continue
        for yml in sorted(domain_dir.glob("*.yml")):
            entry = _load_entry(yml, domain_dir.name)
            if entry is not None:
                entries.append(entry)
    return entries


def _resolve_templates_dir() -> Path:
    import sys

    mod = sys.modules.get(__name__)
    return Path(getattr(mod, "TEMPLATES_DIR", TEMPLATES_DIR))


def list_templates(domain: str | None = None) -> list[CatalogEntry]:
    entries = scan_templates(root=_resolve_templates_dir())
    if domain is None:
        return entries
    return [e for e in entries if e.domain == domain]


def search_templates(query: str, domain: str | None = None) -> list[CatalogEntry]:
    entries = list_templates(domain=domain)
    q = query.strip().lower()
    if not q:
        return entries
    tokens = [t for t in q.split() if t]
    results: list[CatalogEntry] = []
    for entry in entries:
        haystacks = [
            entry.id.lower(),
            entry.description.lower(),
            entry.artifact_type.lower(),
            (entry.grader_profile or "").lower(),
            " ".join(t.lower() for t in entry.language_targets),
        ]
        blob = " | ".join(haystacks)
        if q in blob or all(tok in blob for tok in tokens):
            results.append(entry)
    return results
