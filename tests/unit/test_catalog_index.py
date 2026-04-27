# SPDX-License-Identifier: Apache-2.0
from pathlib import Path

import pytest
import yaml

from image2_workbench.catalog.index import (
    CatalogEntry,
    scan_templates,
    search_templates,
)


def _write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


@pytest.fixture
def tmp_templates(tmp_path: Path) -> Path:
    root = tmp_path / "tmp_templates"
    _write_yaml(
        root / "business" / "pitch_slide.yml",
        {
            "id": "business_pitch_slide",
            "domain": "business",
            "description": "Single-slide pitch deck cover.",
            "artifact": {"type": "poster", "aspect": "16:9", "size": "1920x1088"},
            "grader_profile": "text_fidelity_dense",
            "language_targets": ["zh-CN", "en"],
            "license": "CC-BY-4.0",
        },
    )
    _write_yaml(
        root / "anime" / "manga_panel.yml",
        {
            "id": "anime_manga_panel",
            "domain": "anime",
            "description": "Black-and-white manga panel.",
            "artifact": {"type": "panel", "aspect": "3:4", "size": "1024x1360"},
            "grader_profile": "style_consistency",
            "language_targets": ["ja", "en"],
            "license": "CC-BY-4.0",
        },
    )
    _write_yaml(
        root / "_schema" / "template.schema.yml",
        {"$schema": "https://json-schema.org/draft/2020-12/schema"},
    )
    _write_yaml(
        root / "_vars_examples" / "business_pitch_slide.yml",
        {"company": "Acme Corp"},
    )
    return root


def test_scan_returns_two_entries(tmp_templates: Path):
    entries = scan_templates(root=tmp_templates)
    assert len(entries) == 2
    assert all(isinstance(e, CatalogEntry) for e in entries)


def test_scan_skips_schema_and_vars_examples(tmp_templates: Path):
    entries = scan_templates(root=tmp_templates)
    domains = {e.domain for e in entries}
    assert "_schema" not in domains
    assert "_vars_examples" not in domains
    assert domains == {"business", "anime"}


def test_filter_by_domain(tmp_templates: Path, monkeypatch):
    monkeypatch.setattr(
        "image2_workbench.catalog.index.TEMPLATES_DIR", tmp_templates
    )
    from image2_workbench.catalog.index import list_templates

    business = list_templates(domain="business")
    assert len(business) == 1
    assert business[0].id == "business_pitch_slide"

    anime = list_templates(domain="anime")
    assert len(anime) == 1
    assert anime[0].id == "anime_manga_panel"


def test_search_by_id_substring(tmp_templates: Path, monkeypatch):
    monkeypatch.setattr(
        "image2_workbench.catalog.index.TEMPLATES_DIR", tmp_templates
    )
    results = search_templates("manga")
    assert len(results) == 1
    assert results[0].id == "anime_manga_panel"


def test_search_by_language_targets(tmp_templates: Path, monkeypatch):
    monkeypatch.setattr(
        "image2_workbench.catalog.index.TEMPLATES_DIR", tmp_templates
    )
    ja_hits = search_templates("ja")
    ja_ids = {e.id for e in ja_hits}
    assert "anime_manga_panel" in ja_ids
    assert "business_pitch_slide" not in ja_ids


def test_search_combined_with_domain_filter(tmp_templates: Path, monkeypatch):
    monkeypatch.setattr(
        "image2_workbench.catalog.index.TEMPLATES_DIR", tmp_templates
    )
    results = search_templates("pitch", domain="business")
    assert len(results) == 1
    assert results[0].id == "business_pitch_slide"

    none = search_templates("pitch", domain="anime")
    assert none == []


def test_artifact_type_extracted(tmp_templates: Path):
    entries = scan_templates(root=tmp_templates)
    by_id = {e.id: e for e in entries}
    assert by_id["business_pitch_slide"].artifact_type == "poster"
    assert by_id["anime_manga_panel"].artifact_type == "panel"
