# SPDX-License-Identifier: Apache-2.0
"""Integration check: every V1 template must load, validate, and render bilingually.

V1 demo-var filenames are inconsistent (e.g. ``swot_acme.yml`` instead of
``swot_card.yml``), so we keep ``DEMO_VARS_MAP_LEGACY`` as an explicit override
for the convention-over-config resolver. New V0.3+ templates should follow the
``<template_stem>.yml`` convention inside ``_vars_examples/`` and need NO entry
in this map.
"""
from pathlib import Path

import pytest
import yaml
from jinja2 import Environment, StrictUndefined

from image2_workbench.compiler.loader import (
    load_template,
    load_vars,
    resolve_demo_vars,
)
from image2_workbench.compiler.renderer import render_both
from image2_workbench.compiler.validators import TEXT_BLOCK_CHAR_LIMIT

REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATES_DIR = REPO_ROOT / "templates"

V1_DOMAINS = ["business", "academic", "uiux", "anime"]
EXPECTED_PER_DOMAIN = 4

# Legacy override map for V1 templates whose demo-vars filenames don't follow
# the ``<template_stem>.yml`` convention. Passed to ``resolve_demo_vars`` as
# the ``override`` arg. New templates should NOT add to this dict — they
# should adopt the convention instead.
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

# Backwards-compat alias for any external code that still imports the old
# name. The resolver, not this dict, is the canonical lookup.
DEMO_VARS_MAP = DEMO_VARS_MAP_LEGACY


def _list_templates() -> list[Path]:
    paths: list[Path] = []
    for domain in V1_DOMAINS:
        paths.extend(sorted((TEMPLATES_DIR / domain).glob("*.yml")))
    return paths


def _resolve_for(template_path: Path) -> Path | None:
    return resolve_demo_vars(template_path, override=DEMO_VARS_MAP_LEGACY)


def test_v1_template_count():
    templates = _list_templates()
    assert len(templates) == EXPECTED_PER_DOMAIN * len(V1_DOMAINS), (
        f"expected 16 V1 templates, found {len(templates)}: {[p.name for p in templates]}"
    )


def test_resolver_finds_demo_vars_for_every_v1_template():
    """Every V1 template must resolve via legacy-override-then-convention."""
    templates = _list_templates()
    missing: list[str] = []
    for tp in templates:
        resolved = _resolve_for(tp)
        if resolved is None or not resolved.is_file():
            missing.append(f"{tp.parent.name}/{tp.stem}")
    assert not missing, f"resolver could not locate demo vars for: {missing}"


def test_demo_vars_map_legacy_keys_match_real_templates():
    """Each override key still corresponds to an existing V1 template."""
    templates = _list_templates()
    template_keys = {f"{p.parent.name}/{p.stem}" for p in templates}
    stale = DEMO_VARS_MAP_LEGACY.keys() - template_keys
    assert not stale, (
        f"DEMO_VARS_MAP_LEGACY has stale entries (no template found): {stale}"
    )


@pytest.mark.parametrize(
    "template_path",
    _list_templates(),
    ids=lambda p: f"{p.parent.name}/{p.stem}",
)
def test_template_loads_and_renders(template_path: Path):
    spec = load_template(template_path)
    assert spec.id
    assert spec.domain in V1_DOMAINS

    vars_path = _resolve_for(template_path)
    assert vars_path is not None and vars_path.exists(), (
        f"missing demo vars file for {template_path.parent.name}/{template_path.stem}"
    )

    vars_ = load_vars(vars_path)
    rendered = render_both(spec, vars_)
    assert "zh-CN" in rendered and "en" in rendered
    assert len(rendered["zh-CN"]) > 50
    assert len(rendered["en"]) > 50


@pytest.mark.parametrize(
    "template_path",
    _list_templates(),
    ids=lambda p: f"{p.parent.name}/{p.stem}",
)
def test_demo_text_blocks_render_under_80_chars(template_path: Path):
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
                f"{spec.id}.{block.slot}={len(rendered_text)} chars: {rendered_text}"
            )
    assert not too_long, "\n".join(too_long)


def test_no_template_uses_transparent_or_low_moderation():
    for path in _list_templates():
        raw = yaml.safe_load(path.read_text())
        assert raw.get("moderation", "auto") != "low", f"{path}: moderation must not be low"
        artifact = raw.get("artifact", {})
        bg = artifact.get("background", "auto")
        assert bg != "transparent", f"{path}: transparent background not supported"


def test_resolver_finds_convention_filename_without_override(tmp_path: Path):
    """A future V0.3 template that follows ``<stem>.yml`` needs no override."""
    domain_dir = tmp_path / "newdomain"
    vars_dir = domain_dir / "_vars_examples"
    vars_dir.mkdir(parents=True)
    template_path = domain_dir / "future_template.yml"
    template_path.write_text("id: newdomain.future_template\n", encoding="utf-8")
    convention_vars = vars_dir / "future_template.yml"
    convention_vars.write_text("title: hello\n", encoding="utf-8")

    # No override needed — pure convention.
    resolved = resolve_demo_vars(template_path)
    assert resolved == convention_vars

    # And it still works when an (empty/unrelated) override is supplied.
    resolved_with_override = resolve_demo_vars(template_path, override={})
    assert resolved_with_override == convention_vars
