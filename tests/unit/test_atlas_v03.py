# SPDX-License-Identifier: Apache-2.0
"""V0.3 atlas regression tests.

Locks in the structural invariants of the 16-domain / 52-template atlas
that ships with `image2-workbench v0.3`:

    * directory layout (16 domains under ``templates/``, ``_schema/`` excluded)
    * 52 templates total, ≥3 per domain
    * ≥12 ``DOMAIN_CARD.md`` files (V0.3 batch — V1 domains may not have one yet)
    * every template loads via the compiler, renders bilingually, and respects
      the 80-char text-block ceiling AFTER Jinja substitution from demo vars
    * gpt-image-2 hard constraints — no ``low`` moderation, no
      ``transparent`` background, no top-level ``input_fidelity`` key
    * dimensional rules (``validate_size``) pass for every artifact
    * READMEs are gallery-drift-free in both languages
    * READMEs reference all 30 ``docs/assets/showcase-<domain>.webp`` paths
      as single-column showcase sections, not two-up HTML tables
    * READMEs reference at least 20 ``docs/assets/example-*.webp`` template
      proof images, with no orphaned example assets
    * READMEs keep the homepage ``hero-meme.webp`` banner above the fold
    * README local ``href`` / ``src`` / markdown image targets resolve
    * READMEs do not mention competitor names
    * the three SVG hero/workflow/production-controls assets are well-formed
    * the skill-compatibility doc names all 7 advertised runtimes

If a future change breaks one of these properties the failure surfaces here
before it lands in user-facing artifacts.
"""
from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import pytest
import yaml
from jinja2 import Environment, StrictUndefined
from typer.testing import CliRunner

from image2_workbench.cli import app
from image2_workbench.compiler.loader import (
    load_template,
    load_vars,
    resolve_demo_vars,
)
from image2_workbench.compiler.renderer import render_both
from image2_workbench.compiler.schema import ID_PATTERN
from image2_workbench.compiler.validators import (
    TEXT_BLOCK_CHAR_LIMIT,
    is_experimental_size,
    validate_size,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATES_DIR = REPO_ROOT / "templates"
DOCS_ASSETS = REPO_ROOT / "docs" / "assets"

# --------------------------------------------------------------------------- #
# Domain enumeration helpers.
# --------------------------------------------------------------------------- #

EXPECTED_DOMAIN_COUNT = 30        # 4 V1 + 12 V0.3 + 14 V0.3.5
EXPECTED_TEMPLATE_TOTAL = 80      # 16 V1+V0.3 (12 V0.3 × 3 + V1 4 × 4 = 52) + 14 V0.3.5 × 2 = 80
EXPECTED_DOMAIN_CARD_MIN = 26     # 12 V0.3 + 14 V0.3.5 each ship a DOMAIN_CARD; V1 4 don't

# Per-domain template floor varies between waves: V1 + V0.3 ship ≥ 3 templates
# each, V0.3.5 ships exactly 2 (post-image-drop expansion).
V03_5_DOMAINS = [
    "typography",
    "beauty",
    "events",
    "tattoo",
    "watercolor_illustration",
    "isometric_illustration",
    "comic_book",
    "music",
    "science_fiction_concept",
    "infographic_data",
    "kids_illustration",
    "automotive",
    "pet",
    "streetwear",
]
V03_DOMAINS = [
    "advertising",
    "architecture",
    "ecommerce",
    "fashion",
    "food",
    "gaming",
    "industrial",
    "interior",
    "photography",
    "product",
    "social_media",
    "travel",
]

# README showcase references all 30 domains as user-visible sections on
# GitHub.
SHOWCASE_DOMAINS = [
    "business",
    "academic",
    "uiux",
    "anime",
    "ecommerce",
    "industrial",
    "product",
    "advertising",
    "social_media",
    "gaming",
    "photography",
    "fashion",
    "food",
    "architecture",
    "interior",
    "travel",
    "typography",
    "beauty",
    "events",
    "tattoo",
    "watercolor_illustration",
    "isometric_illustration",
    "comic_book",
    "music",
    "science_fiction_concept",
    "infographic_data",
    "kids_illustration",
    "automotive",
    "pet",
    "streetwear",
]

# Same legacy override map as ``test_all_templates_load.py`` — required for
# the V1 templates whose demo-vars filenames predate the
# ``<template_stem>.yml`` convention. New templates do not need entries here.
DEMO_VARS_MAP_LEGACY: dict[str, str] = {
    "business/swot_card": "business/_vars_examples/swot_acme.yml",
    "business/pitch_slide": "business/_vars_examples/pitch_demo.yml",
    "business/linkedin_carousel": "business/_vars_examples/linkedin_demo.yml",
    "business/data_dashboard": "business/_vars_examples/dashboard_demo.yml",
    "academic/scientific_diagram": "academic/_vars_examples/diagram_demo.yml",
    "academic/chalkboard_proof": "academic/_vars_examples/proof_demo.yml",
    "academic/multilingual_eduposter": "academic/_vars_examples/eduposter_demo.yml",
    "academic/journal_poster": "academic/_vars_examples/journal_demo.yml",
    "uiux/ios_app_mockup": "uiux/_vars_examples/ios_app_demo.yml",
    "uiux/web_dashboard": "uiux/_vars_examples/web_dashboard_demo.yml",
    "uiux/design_system_card": "uiux/_vars_examples/design_system_demo.yml",
    "uiux/social_cover_xhs": "uiux/_vars_examples/xhs_cover_demo.yml",
    "anime/character_sheet": "anime/_vars_examples/character_demo.yml",
    "anime/comic_8panel": "anime/_vars_examples/comic_demo.yml",
    "anime/city_poster": "anime/_vars_examples/city_poster_demo.yml",
    "anime/ccd_candid": "anime/_vars_examples/ccd_demo.yml",
}


def _domain_dirs() -> list[Path]:
    """All 30 domain directories — ``_schema/`` and any dotfiles excluded."""
    return sorted(
        d
        for d in TEMPLATES_DIR.iterdir()
        if d.is_dir() and not d.name.startswith(".") and d.name != "_schema"
    )


def _all_atlas_templates() -> list[Path]:
    """Every ``.yml`` template across all 30 domains (80 total)."""
    paths: list[Path] = []
    for domain in _domain_dirs():
        paths.extend(sorted(domain.glob("*.yml")))
    return paths


def _resolve_for(template_path: Path) -> Path | None:
    return resolve_demo_vars(template_path, override=DEMO_VARS_MAP_LEGACY)


# --------------------------------------------------------------------------- #
# 1-2 — counts.
# --------------------------------------------------------------------------- #


def test_atlas_domain_count_is_16() -> None:
    domains = _domain_dirs()
    assert len(domains) == EXPECTED_DOMAIN_COUNT, (
        f"expected {EXPECTED_DOMAIN_COUNT} domain dirs, "
        f"found {len(domains)}: {[d.name for d in domains]}"
    )


def test_atlas_total_template_count_is_52() -> None:
    templates = _all_atlas_templates()
    assert len(templates) == EXPECTED_TEMPLATE_TOTAL, (
        f"expected {EXPECTED_TEMPLATE_TOTAL} templates, found {len(templates)}"
    )


# --------------------------------------------------------------------------- #
# 3 — per-domain template floor.
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "domain_dir",
    _domain_dirs(),
    ids=lambda p: p.name,
)
def test_each_domain_has_at_least_min_templates(domain_dir: Path) -> None:
    """V1 + V0.3 ship ≥ 3 templates per domain; V0.3.5 ships ≥ 2."""
    yamls = sorted(domain_dir.glob("*.yml"))
    floor = 2 if domain_dir.name in V03_5_DOMAINS else 3
    assert len(yamls) >= floor, (
        f"{domain_dir.name} has only {len(yamls)} templates "
        f"(min {floor}): {[p.name for p in yamls]}"
    )


# --------------------------------------------------------------------------- #
# 4 — DOMAIN_CARD coverage.
# --------------------------------------------------------------------------- #


def test_each_domain_has_a_DOMAIN_CARD() -> None:
    """At least 12 domains ship a DOMAIN_CARD.md (V0.3 batch).

    V1 domains (business/academic/uiux/anime) may not have a card yet —
    the assertion is intentionally a floor, not an exact match.
    """
    cards = sorted(TEMPLATES_DIR.rglob("DOMAIN_CARD.md"))
    assert len(cards) >= EXPECTED_DOMAIN_CARD_MIN, (
        f"expected at least {EXPECTED_DOMAIN_CARD_MIN} DOMAIN_CARD.md files, "
        f"found {len(cards)}: {[c.parent.name for c in cards]}"
    )
    # Every V0.3 domain must have one — that batch is non-negotiable.
    have = {c.parent.name for c in cards}
    missing_v03 = [d for d in V03_DOMAINS if d not in have]
    assert not missing_v03, f"V0.3 domains missing DOMAIN_CARD.md: {missing_v03}"


# --------------------------------------------------------------------------- #
# 5 — every template loads via the compiler.
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "template_path",
    _all_atlas_templates(),
    ids=lambda p: f"{p.parent.name}/{p.stem}",
)
def test_atlas_loads_all_via_compiler(template_path: Path) -> None:
    spec = load_template(template_path)
    assert spec.id, f"{template_path}: empty id"
    assert ID_PATTERN.match(spec.id), (
        f"{template_path}: id {spec.id!r} does not match {ID_PATTERN.pattern}"
    )
    # The id pattern requires at least 2 chars; double-check a sane floor.
    assert len(spec.id) >= 3, f"{template_path}: id {spec.id!r} too short"


# --------------------------------------------------------------------------- #
# 6 — bilingual render produces both language keys with non-trivial text.
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "template_path",
    _all_atlas_templates(),
    ids=lambda p: f"{p.parent.name}/{p.stem}",
)
def test_atlas_renders_bilingual(template_path: Path) -> None:
    spec = load_template(template_path)
    vars_path = _resolve_for(template_path)
    assert vars_path is not None and vars_path.exists(), (
        f"{template_path}: demo vars not resolvable"
    )
    vars_ = load_vars(vars_path)
    rendered = render_both(spec, vars_)
    assert set(rendered.keys()) >= {"zh-CN", "en"}, (
        f"{template_path}: expected zh-CN and en, got {list(rendered.keys())}"
    )
    assert rendered["zh-CN"].strip(), f"{template_path}: empty zh-CN render"
    assert rendered["en"].strip(), f"{template_path}: empty en render"
    # Non-trivial floor — a render that's only 5 chars is almost certainly broken.
    assert len(rendered["zh-CN"]) > 50
    assert len(rendered["en"]) > 50


# --------------------------------------------------------------------------- #
# 7 — text blocks must stay under 80 chars even AFTER Jinja substitution.
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "template_path",
    _all_atlas_templates(),
    ids=lambda p: f"{p.parent.name}/{p.stem}",
)
def test_atlas_text_blocks_below_80_chars_when_rendered(
    template_path: Path,
) -> None:
    spec = load_template(template_path)
    vars_path = _resolve_for(template_path)
    assert vars_path is not None
    vars_ = load_vars(vars_path)
    env = Environment(undefined=StrictUndefined, autoescape=False)

    too_long: list[str] = []
    for block in spec.spec.text_blocks:
        rendered_text = env.from_string(block.text).render(**vars_)
        if len(rendered_text) > TEXT_BLOCK_CHAR_LIMIT:
            too_long.append(
                f"{spec.id}.{block.slot}={len(rendered_text)} chars: "
                f"{rendered_text!r}"
            )
    assert not too_long, "\n".join(too_long)


# --------------------------------------------------------------------------- #
# 8 — gpt-image-2 forbids transparent background and 'low' moderation
# (extends the V1-only test to the full 52-template atlas).
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "template_path",
    _all_atlas_templates(),
    ids=lambda p: f"{p.parent.name}/{p.stem}",
)
def test_no_atlas_template_uses_transparent_or_low_moderation(
    template_path: Path,
) -> None:
    raw: dict[str, Any] = yaml.safe_load(
        template_path.read_text(encoding="utf-8")
    )
    assert raw.get("moderation", "auto") != "low", (
        f"{template_path}: moderation must not be 'low'"
    )
    artifact = raw.get("artifact", {}) or {}
    bg = artifact.get("background", "auto")
    assert bg != "transparent", (
        f"{template_path}: transparent background is not supported by gpt-image-2"
    )


# --------------------------------------------------------------------------- #
# 9 — input_fidelity is rejected by gpt-image-2; no template may carry it.
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "template_path",
    _all_atlas_templates(),
    ids=lambda p: f"{p.parent.name}/{p.stem}",
)
def test_no_atlas_template_uses_input_fidelity(template_path: Path) -> None:
    raw: dict[str, Any] = yaml.safe_load(
        template_path.read_text(encoding="utf-8")
    )
    # Top-level scan first.
    assert "input_fidelity" not in raw, (
        f"{template_path}: top-level 'input_fidelity' key is forbidden"
    )
    # Nested guard — also reject inside artifact and any extras dict if present.
    artifact = raw.get("artifact", {}) or {}
    assert "input_fidelity" not in artifact, (
        f"{template_path}: artifact.input_fidelity is forbidden"
    )
    extras = raw.get("extras") or raw.get("extra")
    if isinstance(extras, dict):
        assert "input_fidelity" not in extras, (
            f"{template_path}: extras.input_fidelity is forbidden"
        )


# --------------------------------------------------------------------------- #
# 10 — every artifact size passes dimensional rules; experimental sizes are
# allowed (warn-not-fail in production, but here we just observe the bit).
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "template_path",
    _all_atlas_templates(),
    ids=lambda p: f"{p.parent.name}/{p.stem}",
)
def test_atlas_sizes_pass_dimensional_rules(template_path: Path) -> None:
    raw: dict[str, Any] = yaml.safe_load(
        template_path.read_text(encoding="utf-8")
    )
    size = raw["artifact"]["size"]
    width, height = validate_size(size)
    # is_experimental_size is informational; we just call it to ensure it
    # does not raise. Templates above 2560×1440 are tolerated as experimental.
    _ = is_experimental_size(width, height)
    assert width > 0 and height > 0


# --------------------------------------------------------------------------- #
# 11-12 — gallery section drift checks via the actual CLI.
# --------------------------------------------------------------------------- #


def test_readme_gallery_section_is_drift_free() -> None:
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["gallery", "readme", "--lang", "en", "--check", str(REPO_ROOT / "README.md")],
    )
    assert result.exit_code == 0, (
        f"i2w gallery readme --check exited {result.exit_code}\n"
        f"output: {result.output}"
    )


def test_readme_zh_gallery_section_is_drift_free() -> None:
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "gallery",
            "readme",
            "--lang",
            "zh-CN",
            "--check",
            str(REPO_ROOT / "README.zh.md"),
        ],
    )
    assert result.exit_code == 0, (
        f"i2w gallery readme --lang zh-CN --check exited {result.exit_code}\n"
        f"output: {result.output}"
    )


# --------------------------------------------------------------------------- #
# 13 — neither README mentions competitor product names.
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "readme_path",
    [REPO_ROOT / "README.md", REPO_ROOT / "README.zh.md"],
    ids=lambda p: p.name,
)
@pytest.mark.parametrize(
    "needle",
    ["wuyoscar", "EvoLinkAI", "YouMind"],
)
def test_readme_no_competitor_mentions(readme_path: Path, needle: str) -> None:
    body = readme_path.read_text(encoding="utf-8")
    assert needle.lower() not in body.lower(), (
        f"{readme_path.name} unexpectedly mentions {needle!r}"
    )


# --------------------------------------------------------------------------- #
# 14 — gallery-forward READMEs reference all 30 showcase webp paths, and the
# assets exist locally.
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("domain", SHOWCASE_DOMAINS)
def test_showcase_image_assets_are_referenced_in_readmes(domain: str) -> None:
    expected = f"docs/assets/showcase-{domain}.webp"
    assert (REPO_ROOT / expected).is_file(), f"missing showcase asset {expected!r}"
    body_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    body_zh = (REPO_ROOT / "README.zh.md").read_text(encoding="utf-8")
    assert expected in body_en, f"README.md is missing {expected!r}"
    assert expected in body_zh, f"README.zh.md is missing {expected!r}"


@pytest.mark.parametrize(
    "readme_path",
    [REPO_ROOT / "README.md", REPO_ROOT / "README.zh.md"],
    ids=lambda p: p.name,
)
def test_showcase_is_single_column_large_images(readme_path: Path) -> None:
    body = readme_path.read_text(encoding="utf-8")
    assert '<td width="50%"' not in body
    assert '<table width="100%" cellpadding="12" cellspacing="0">' not in body


def test_template_proof_images_are_referenced_in_readmes() -> None:
    example_assets = sorted(DOCS_ASSETS.glob("example-*.webp"))
    assert len(example_assets) >= 20
    body_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    body_zh = (REPO_ROOT / "README.zh.md").read_text(encoding="utf-8")
    missing_en: list[str] = []
    missing_zh: list[str] = []
    oversized: list[str] = []
    for asset in example_assets:
        rel = f"docs/assets/{asset.name}"
        if rel not in body_en:
            missing_en.append(rel)
        if rel not in body_zh:
            missing_zh.append(rel)
        if asset.stat().st_size > 500_000:
            oversized.append(rel)

    assert not missing_en, f"README.md is missing example assets: {missing_en}"
    assert not missing_zh, f"README.zh.md is missing example assets: {missing_zh}"
    assert not oversized, f"example assets exceed 500KB: {oversized}"


@pytest.mark.parametrize(
    "readme_path",
    [REPO_ROOT / "README.md", REPO_ROOT / "README.zh.md"],
    ids=lambda p: p.name,
)
def test_readme_homepage_banner_is_present(readme_path: Path) -> None:
    body = readme_path.read_text(encoding="utf-8")
    assert 'src="docs/assets/hero-meme.webp"' in body


# --------------------------------------------------------------------------- #
# 14b — README local links and image targets resolve on GitHub.
# --------------------------------------------------------------------------- #


LOCAL_TARGET_RE = re.compile(
    r'(?:href|src)=["\']([^"\']+)["\']|!\[[^\]]*\]\(([^)\s]+)'
)
EXTERNAL_LINK_RE = re.compile(r"^[a-z][a-z0-9+.-]*:")


@pytest.mark.parametrize(
    "readme_path",
    [REPO_ROOT / "README.md", REPO_ROOT / "README.zh.md"],
    ids=lambda p: p.name,
)
def test_readme_local_href_src_targets_exist(readme_path: Path) -> None:
    body = readme_path.read_text(encoding="utf-8")
    missing: list[str] = []
    for match in LOCAL_TARGET_RE.finditer(body):
        raw_target = match.group(1) or match.group(2)
        target = raw_target.split("#", 1)[0]
        if not target or target.startswith("#") or EXTERNAL_LINK_RE.match(target):
            continue
        if not (readme_path.parent / target).exists():
            missing.append(raw_target)

    assert not missing, f"{readme_path.name} has broken local targets: {missing}"


# --------------------------------------------------------------------------- #
# 15 — SVG assets parse, have a viewBox, and carry a <title>.
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "svg_name",
    ["hero.svg", "workflow.svg", "production-controls.svg"],
)
def test_svgs_well_formed(svg_name: str) -> None:
    path = DOCS_ASSETS / svg_name
    assert path.is_file(), f"missing svg: {path}"
    tree = ET.parse(path)
    root = tree.getroot()
    # SVG root element with viewBox.
    assert root.tag.endswith("svg"), f"{svg_name}: unexpected root tag {root.tag!r}"
    assert root.get("viewBox"), f"{svg_name}: root <svg> missing viewBox attribute"
    # <title> child for accessibility — search regardless of namespace.
    title_elem = next(
        (el for el in root.iter() if el.tag.endswith("title")),
        None,
    )
    assert title_elem is not None, f"{svg_name}: missing <title> element"
    assert (title_elem.text or "").strip(), (
        f"{svg_name}: <title> element is empty"
    )


# --------------------------------------------------------------------------- #
# 16 — skill-compatibility doc names every advertised runtime.
# --------------------------------------------------------------------------- #


def test_skill_compatibility_doc_lists_seven_runtimes() -> None:
    doc = REPO_ROOT / "docs" / "skill-compatibility.md"
    assert doc.is_file(), f"missing {doc}"
    body = doc.read_text(encoding="utf-8").lower()
    runtimes = ["claude", "codex", "anthropic", "langchain", "smolagents", "openclaw", "hermes"]
    missing = [r for r in runtimes if r not in body]
    assert not missing, (
        f"{doc.name} is missing runtime mentions: {missing}"
    )


# --------------------------------------------------------------------------- #
# 17 — the legacy override map only references real templates (regression
# guard against drift between the V1 demo-var filenames and live templates).
# --------------------------------------------------------------------------- #


def test_legacy_demo_vars_map_keys_match_real_templates() -> None:
    real = {
        f"{p.parent.name}/{p.stem}" for p in _all_atlas_templates()
    }
    stale = set(DEMO_VARS_MAP_LEGACY) - real
    assert not stale, f"DEMO_VARS_MAP_LEGACY has stale keys: {stale}"


# --------------------------------------------------------------------------- #
# Sanity guard — the helpers we import are not silently empty (would mask
# every parametrization above and turn this file into a no-op).
# --------------------------------------------------------------------------- #


def test_helpers_enumerate_full_atlas() -> None:
    assert len(_domain_dirs()) == EXPECTED_DOMAIN_COUNT
    assert len(_all_atlas_templates()) == EXPECTED_TEMPLATE_TOTAL
    # And the python interpreter we're in is the one we expect (sanity).
    assert sys.version_info >= (3, 9)
