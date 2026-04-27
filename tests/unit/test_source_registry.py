# SPDX-License-Identifier: Apache-2.0
from pathlib import Path

from image2_workbench.catalog.source_registry import (
    SourceRegistry,
    load_registry,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / "corpus" / "manifests" / "source_registry.yml"


def test_registry_parses():
    registry = load_registry(REGISTRY_PATH)
    assert isinstance(registry, SourceRegistry)
    assert len(registry.sources) >= 4


def test_wuyoscar_entry_present_with_attribution():
    registry = load_registry(REGISTRY_PATH)
    entry = registry.find("wuyoscar-gpt-image-2-skill")
    assert entry is not None
    assert entry.redistributable == "with_attribution"
    assert entry.kind == "github_repo"
    assert entry.license_status == "clear"


def test_openai_entries_not_redistributable():
    registry = load_registry(REGISTRY_PATH)
    openai_ids = [
        "openai-cookbook-image-prompting",
        "openai-image-generation-guide",
        "openai-gpt-image-2-model-page",
    ]
    for sid in openai_ids:
        entry = registry.find(sid)
        assert entry is not None, f"missing {sid}"
        assert entry.redistributable == "none"
        assert entry.kind == "official"
        assert entry.license_status == "metadata_only"


def test_audit_clean_on_initial_registry():
    registry = load_registry(REGISTRY_PATH)
    assert registry.audit() == []


def test_filter_redistributable_excludes_official_docs():
    registry = load_registry(REGISTRY_PATH)
    redistributable = registry.filter_redistributable()
    ids = {e.id for e in redistributable}
    assert "wuyoscar-gpt-image-2-skill" in ids
    assert "openai-cookbook-image-prompting" not in ids


def test_find_unknown_returns_none():
    registry = load_registry(REGISTRY_PATH)
    assert registry.find("does-not-exist") is None
