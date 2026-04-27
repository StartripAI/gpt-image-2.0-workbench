"""Integration check: every V1 template must load, validate, and render bilingually.

Demo var filenames don't follow a strict `<template_stem>_demo.yml` pattern across
domains, so we maintain an explicit template -> demo-vars map below. New templates
should add an entry to keep this regression test honest.
"""
from pathlib import Path

import pytest
import yaml
from jinja2 import Environment, StrictUndefined

from image2_workbench.compiler.loader import load_template, load_vars
from image2_workbench.compiler.renderer import render_both
from image2_workbench.compiler.validators import TEXT_BLOCK_CHAR_LIMIT

REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATES_DIR = REPO_ROOT / "templates"

V1_DOMAINS = ["business", "academic", "uiux", "anime"]
EXPECTED_PER_DOMAIN = 4

DEMO_VARS_MAP: dict[str, str] = {
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


def _list_templates() -> list[Path]:
    paths: list[Path] = []
    for domain in V1_DOMAINS:
        paths.extend(sorted((TEMPLATES_DIR / domain).glob("*.yml")))
    return paths


def test_v1_template_count():
    templates = _list_templates()
    assert len(templates) == EXPECTED_PER_DOMAIN * len(V1_DOMAINS), (
        f"expected 16 V1 templates, found {len(templates)}: {[p.name for p in templates]}"
    )


def test_demo_vars_map_complete():
    templates = _list_templates()
    rels = {f"{p.parent.name}/{p.stem}" for p in templates}
    missing = rels - DEMO_VARS_MAP.keys()
    assert not missing, f"DEMO_VARS_MAP missing entries for: {missing}"


@pytest.mark.parametrize(
    "template_path",
    _list_templates(),
    ids=lambda p: f"{p.parent.name}/{p.stem}",
)
def test_template_loads_and_renders(template_path: Path):
    spec = load_template(template_path)
    assert spec.id
    assert spec.domain in V1_DOMAINS

    rel = f"{template_path.parent.name}/{template_path.stem}"
    vars_rel = DEMO_VARS_MAP[rel]
    vars_path = TEMPLATES_DIR / vars_rel
    assert vars_path.exists(), f"missing demo vars file {vars_path} for {rel}"

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
    rel = f"{template_path.parent.name}/{template_path.stem}"
    vars_path = TEMPLATES_DIR / DEMO_VARS_MAP[rel]
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
