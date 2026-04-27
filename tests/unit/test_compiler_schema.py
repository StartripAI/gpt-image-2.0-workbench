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

SCHEMA_DIR = Path(__file__).resolve().parents[2] / "templates" / "_schema"
EXAMPLE_PATH = SCHEMA_DIR / "example.yml"
SCHEMA_REF_PATH = SCHEMA_DIR / "template.schema.yml"


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


# Canonical atlas domain set — 4 V1 + 12 V0.3 + 14 V0.3.5 = 30 domains.
ALL_V03_DOMAINS = [
    # V1 (4)
    "business",
    "academic",
    "uiux",
    "anime",
    # V0.3 atlas (12)
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
    # V0.3.5 atlas expansion (14)
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
EXPECTED_DOMAIN_COUNT = 30


def test_domain_literal_has_sixteen_values():
    """Name kept for git-blame continuity; asserts the current atlas size."""
    from typing import get_args

    from image2_workbench.compiler.schema import ALLOWED_DOMAINS, Domain

    assert len(get_args(Domain)) == EXPECTED_DOMAIN_COUNT
    assert set(get_args(Domain)) == set(ALL_V03_DOMAINS)
    assert set(ALLOWED_DOMAINS) == set(ALL_V03_DOMAINS)


@pytest.mark.parametrize("domain", ALL_V03_DOMAINS)
def test_each_v03_domain_validates(domain: str):
    data = _example_dict()
    data["domain"] = domain
    t = TemplateSpec.model_validate(data)
    assert t.domain == domain


def test_reference_schema_enumerates_all_sixteen_domains():
    """Name kept for git-blame continuity; asserts the current atlas size."""
    with SCHEMA_REF_PATH.open("r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)
    domain_enum = raw["properties"]["domain"]["enum"]
    assert set(domain_enum) == set(ALL_V03_DOMAINS)
    assert len(domain_enum) == EXPECTED_DOMAIN_COUNT


def test_reference_schema_includes_dashboard_and_photo_artifacts():
    with SCHEMA_REF_PATH.open("r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)
    artifact_types = raw["properties"]["artifact"]["properties"]["type"]["enum"]
    assert {"dashboard", "photo"} <= set(artifact_types)


@pytest.mark.parametrize("artifact_type", ["dashboard", "photo"])
def test_dashboard_and_photo_artifact_types_validate(artifact_type: str):
    data = _example_dict()
    data["artifact"] = copy.deepcopy(data["artifact"])
    data["artifact"]["type"] = artifact_type
    t = TemplateSpec.model_validate(data)
    assert t.artifact.type == artifact_type


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
