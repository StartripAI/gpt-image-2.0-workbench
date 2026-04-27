# SPDX-License-Identifier: Apache-2.0
"""Tests for cross-runtime Skill compatibility.

Verifies that:
  - skills/gpt-image/SKILL.md frontmatter parses cleanly via yaml.safe_load
    (and via python-frontmatter when that optional package is installed)
  - the `compatibility:` block lists at least 7 runtime entries with
    `runtime`, `status`, and `manifest` keys
  - every manifest path resolves to an existing file
  - JSON manifests parse via json.loads, YAML manifests via yaml.safe_load
  - Python manifests parse via ast.parse without SyntaxError
"""
from __future__ import annotations

import ast
import json
import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_DIR = REPO_ROOT / "skills" / "gpt-image"
SKILL_MD = SKILL_DIR / "SKILL.md"
MANIFEST_DIR = SKILL_DIR / "manifests"


def _extract_frontmatter(text: str) -> dict:
    """Pull the YAML block between the first --- pair without external deps."""
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    assert match, "SKILL.md must start with a YAML frontmatter block"
    return yaml.safe_load(match.group(1))


@pytest.fixture(scope="module")
def frontmatter() -> dict:
    return _extract_frontmatter(SKILL_MD.read_text(encoding="utf-8"))


def test_skill_md_exists():
    assert SKILL_MD.is_file(), f"missing {SKILL_MD}"


def test_frontmatter_parses_with_yaml(frontmatter):
    # Top-level required Anthropic / Codex / agentskills.io fields.
    assert frontmatter["name"] == "gpt-image"
    assert isinstance(frontmatter["description"], str)
    assert frontmatter["description"].strip(), "description must be non-empty"


def test_frontmatter_parses_with_python_frontmatter():
    """If python-frontmatter is installed, it must agree with yaml.safe_load.

    The package is NOT a hard dependency; skip cleanly when missing.
    """
    frontmatter_pkg = pytest.importorskip("frontmatter")
    parsed = frontmatter_pkg.loads(SKILL_MD.read_text(encoding="utf-8"))
    assert parsed["name"] == "gpt-image"
    assert "compatibility" in parsed.metadata


def test_compatibility_has_at_least_seven_entries(frontmatter):
    compat = frontmatter.get("compatibility")
    assert isinstance(compat, list)
    assert len(compat) >= 7, f"expected >= 7 runtime entries, got {len(compat)}"


def test_each_compatibility_entry_has_required_fields(frontmatter):
    valid_statuses = {"tested", "shim_ready", "theoretical"}
    seen_runtimes: set[str] = set()
    for entry in frontmatter["compatibility"]:
        for field in ("runtime", "status", "manifest"):
            assert field in entry, f"entry missing {field}: {entry}"
        assert entry["status"] in valid_statuses, entry
        assert entry["runtime"] not in seen_runtimes, f"duplicate runtime {entry['runtime']}"
        seen_runtimes.add(entry["runtime"])


def test_each_manifest_path_resolves(frontmatter):
    for entry in frontmatter["compatibility"]:
        manifest = SKILL_DIR / entry["manifest"]
        assert manifest.is_file(), f"missing manifest file: {manifest}"


def test_json_manifests_parse():
    json_files = sorted(MANIFEST_DIR.glob("*.json"))
    assert json_files, "expected at least one JSON manifest"
    for path in json_files:
        json.loads(path.read_text(encoding="utf-8"))


def test_yaml_manifests_parse():
    yaml_files = sorted(MANIFEST_DIR.glob("*.yml")) + sorted(MANIFEST_DIR.glob("*.yaml"))
    assert yaml_files, "expected at least one YAML manifest"
    for path in yaml_files:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(loaded, dict), f"{path} must parse to a mapping"


def test_python_manifests_parse():
    py_files = sorted(MANIFEST_DIR.glob("*.py"))
    assert py_files, "expected at least one Python manifest"
    for path in py_files:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def test_manifest_files_under_thirty_lines():
    for path in MANIFEST_DIR.iterdir():
        if path.suffix in {".json", ".yml", ".yaml", ".py"}:
            # `wc -l` semantics: count terminating newlines.
            line_count = path.read_text(encoding="utf-8").count("\n")
            assert line_count <= 30, f"{path.name} has {line_count} lines (limit 30)"


def test_manifests_readme_present():
    assert (MANIFEST_DIR / "README.md").is_file()


def test_runtimes_summary_field(frontmatter):
    runtimes = frontmatter.get("runtimes")
    assert isinstance(runtimes, dict)
    for bucket in ("preferred", "shimmed", "theoretical"):
        assert bucket in runtimes
        assert isinstance(runtimes[bucket], list)
        assert runtimes[bucket], f"{bucket} bucket must not be empty"
