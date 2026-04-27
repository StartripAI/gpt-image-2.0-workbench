# SPDX-License-Identifier: Apache-2.0
"""Tests for the bilingual renderer."""

from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml
from jinja2 import UndefinedError

from image2_workbench.compiler.loader import load_template
from image2_workbench.compiler.renderer import render, render_both
from image2_workbench.compiler.schema import TemplateSpec
from image2_workbench.compiler.validators import TextBlockValidationError

EXAMPLE_PATH = Path(__file__).resolve().parents[2] / "templates" / "_schema" / "example.yml"
SAMPLE_VARS = {
    "subject_label": "Q3",
    "title": "Hello",
    "subhead": "World",
}


def _example_dict() -> dict:
    with EXAMPLE_PATH.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def test_render_contains_var_values():
    t = load_template(EXAMPLE_PATH)
    out = render(t, SAMPLE_VARS, "en")
    assert "Hello" in out
    assert "World" in out
    assert "Q3" in out


def test_render_both_languages():
    t = load_template(EXAMPLE_PATH)
    both = render_both(t, SAMPLE_VARS)
    assert set(both.keys()) == {"zh-CN", "en"}
    zh, en = both["zh-CN"], both["en"]
    # Same data, different labels.
    assert "Hello" in zh and "Hello" in en
    assert "World" in zh and "World" in en
    assert "主体" in zh and "Subject" in en
    assert "动作" in zh and "Action" in en
    assert "场景" in zh and "Scene" in en
    assert "构图" in zh and "Composition" in en
    assert "风格" in zh and "Style" in en
    # Cross-contamination check: en prompt should not carry the zh labels and
    # vice versa. Use the bracketed section markers so we don't trip on body
    # text that happens to contain a label word.
    assert "[1. 主体]" not in en
    assert "[1. Subject]" not in zh


def test_text_blocks_rendered_in_chunked_section():
    t = load_template(EXAMPLE_PATH)
    en = render(t, SAMPLE_VARS, "en")
    assert "Text to render exactly" in en
    # Templates own their own quoting convention; the renderer does not
    # double-wrap. The example.yml stores `'{{title}}'` (unquoted), so the
    # rendered slot line carries only the literal value.
    assert "- header: Hello" in en
    assert "- subhead: World" in en


def test_negative_appears_when_present():
    t = load_template(EXAMPLE_PATH)
    en = render(t, SAMPLE_VARS, "en")
    zh = render(t, SAMPLE_VARS, "zh-CN")
    assert en.rstrip().endswith("NO: no neon colors, no photorealistic faces")
    assert "禁止: no neon colors, no photorealistic faces" in zh


def test_negative_absent_when_empty():
    data = _example_dict()
    data["spec"] = copy.deepcopy(data["spec"])
    data["spec"]["negative"] = []
    t = TemplateSpec.model_validate(data)
    en = render(t, SAMPLE_VARS, "en")
    assert "NO:" not in en


def test_preserve_appears_when_present():
    t = load_template(EXAMPLE_PATH)
    en = render(t, SAMPLE_VARS, "en")
    assert "Preserve (edit mode only)" in en
    assert "Company logo in the top-left corner" in en


def test_strict_undefined_raises_on_missing_var():
    t = load_template(EXAMPLE_PATH)
    with pytest.raises(UndefinedError):
        render(t, {"subject_label": "Q3", "title": "Hello"}, "en")


def test_unknown_lang_rejected():
    t = load_template(EXAMPLE_PATH)
    with pytest.raises(ValueError):
        render(t, SAMPLE_VARS, "ja-JP")


def test_lang_not_in_targets_rejected():
    data = _example_dict()
    data["language_targets"] = ["en"]
    t = TemplateSpec.model_validate(data)
    with pytest.raises(ValueError):
        render(t, SAMPLE_VARS, "zh-CN")


def test_oversize_text_block_rejected_at_load():
    data = _example_dict()
    data["spec"] = copy.deepcopy(data["spec"])
    data["spec"]["text_blocks"] = [
        {"slot": "header", "text": "A" * 81},
    ]
    with pytest.raises(Exception):
        TemplateSpec.model_validate(data)


def test_oversize_rendered_text_block_rejected():
    t = load_template(EXAMPLE_PATH)
    vars_ = dict(SAMPLE_VARS)
    vars_["title"] = "A" * 81
    with pytest.raises(TextBlockValidationError):
        render(t, vars_, "en")


def test_no_code_fences_in_output():
    t = load_template(EXAMPLE_PATH)
    out = render(t, SAMPLE_VARS, "en")
    assert "```" not in out


def test_section_order_is_1_to_5():
    t = load_template(EXAMPLE_PATH)
    en = render(t, SAMPLE_VARS, "en")
    idx_subject = en.find("[1. Subject]")
    idx_action = en.find("[2. Action]")
    idx_scene = en.find("[3. Scene]")
    idx_composition = en.find("[4. Composition]")
    idx_style = en.find("[5. Style]")
    assert -1 < idx_subject < idx_action < idx_scene < idx_composition < idx_style
