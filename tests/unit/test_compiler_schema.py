# SPDX-License-Identifier: Apache-2.0
"""Tests for the pydantic schema and YAML loader."""

from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml

from image2_workbench.compiler.loader import load_template
from image2_workbench.compiler.schema import TemplateSpec
from image2_workbench.compiler.validators import SizeValidationError, ValidationError

EXAMPLE_PATH = Path(__file__).resolve().parents[2] / "templates" / "_schema" / "example.yml"


def _example_dict() -> dict:
    with EXAMPLE_PATH.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def test_loads_example_yaml():
    t = load_template(EXAMPLE_PATH)
    assert isinstance(t, TemplateSpec)
    assert t.id == "smoke_demo"
    assert t.domain == "business"
    assert t.artifact.size == "1536x1024"
    assert (t.artifact.width, t.artifact.height) == (1536, 1024)
    assert t.artifact.aspect == "3:2"
    assert len(t.spec.text_blocks) == 2
    assert t.spec.preserve == ["Company logo in the top-left corner"]
    assert t.spec.negative == ["no neon colors", "no photorealistic faces"]
    assert t.api_mode == "images_generate"
    assert t.moderation == "auto"
    assert t.language_targets == ["zh-CN", "en"]
    assert t.grader_profile == "text_fidelity_dense"


def test_models_are_frozen():
    t = load_template(EXAMPLE_PATH)
    with pytest.raises(Exception):
        t.id = "renamed"  # type: ignore[misc]


def test_extra_keys_forbidden():
    data = _example_dict()
    data["surprise"] = "boom"
    with pytest.raises(Exception):
        TemplateSpec.model_validate(data)


def test_missing_required_field_rejected():
    data = _example_dict()
    del data["artifact"]
    with pytest.raises(Exception):
        TemplateSpec.model_validate(data)


def test_invalid_domain_rejected():
    data = _example_dict()
    data["domain"] = "espionage"
    with pytest.raises(Exception):
        TemplateSpec.model_validate(data)


@pytest.mark.parametrize(
    "bad_id",
    ["1leading_digit", "Has_Caps", "with-dash", "", "trailingsymbol!"],
)
def test_invalid_id_chars_rejected(bad_id: str):
    data = _example_dict()
    data["id"] = bad_id
    with pytest.raises((ValidationError, Exception)):
        TemplateSpec.model_validate(data)


def test_size_violation_rejected():
    data = _example_dict()
    data["artifact"] = copy.deepcopy(data["artifact"])
    data["artifact"]["size"] = "1023x1024"  # not multiple of 16
    data["artifact"]["aspect"] = "1023:1024"
    with pytest.raises((SizeValidationError, Exception)):
        TemplateSpec.model_validate(data)


def test_aspect_disagrees_with_size_rejected():
    data = _example_dict()
    data["artifact"] = copy.deepcopy(data["artifact"])
    data["artifact"]["aspect"] = "16:9"  # disagrees with 1536x1024 (= 3:2)
    with pytest.raises(Exception):
        TemplateSpec.model_validate(data)


def test_empty_language_targets_rejected():
    data = _example_dict()
    data["language_targets"] = []
    with pytest.raises(Exception):
        TemplateSpec.model_validate(data)


def test_invalid_quality_policy_rejected():
    data = _example_dict()
    data["quality_policy"] = {"default": "ultra", "exploration": "low"}
    with pytest.raises(Exception):
        TemplateSpec.model_validate(data)


def test_invalid_api_mode_rejected():
    data = _example_dict()
    data["api_mode"] = "carrier_pigeon"
    with pytest.raises(Exception):
        TemplateSpec.model_validate(data)


def test_text_block_too_long_rejected_at_schema():
    data = _example_dict()
    data["spec"] = copy.deepcopy(data["spec"])
    data["spec"]["text_blocks"] = [
        {"slot": "header", "text": "x" * 200},
    ]
    with pytest.raises(Exception):
        TemplateSpec.model_validate(data)
