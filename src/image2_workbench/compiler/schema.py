# SPDX-License-Identifier: Apache-2.0
"""Pydantic v2 models for the seven-section template DSL.

The DSL has 7 logical sections plus meta:

  Section 1  subject       (主体)
  Section 2  action        (动作)
  Section 3  scene         (场景)
  Section 4  composition   (构图)
  Section 5  style         (风格 / 光影 / 媒介)
  Section 6  text_blocks   (文字渲染 — chunked)
  Section 7  preserve / negative  (保留 / 禁止)

Pydantic owns authoritative validation; the YAML reference under
``templates/_schema/template.schema.yml`` is informational only.
"""

from __future__ import annotations

import re
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)

from .validators import (
    SizeValidationError,
    ValidationError,
    validate_size,
    validate_text_block_chunking,
)

ID_PATTERN = re.compile(r"^[a-z][a-z0-9_]+$")

ALLOWED_DOMAINS = (
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
)
Domain = Literal[
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
]
ArtifactType = Literal[
    "infographic",
    "poster",
    "mockup",
    "character_sheet",
    "comic_page",
    "diagram",
    "dashboard",
    "photo",
]
QualityLevel = Literal["low", "medium", "high"]
ApiMode = Literal["images_generate", "images_edit", "responses"]
Moderation = Literal["auto", "low"]
GraderProfile = Literal[
    "text_fidelity_dense",
    "text_fidelity_sparse",
    "layout",
    "edit_locality",
    "continuity",
]


_FROZEN_FORBID = ConfigDict(frozen=True, extra="forbid", str_strip_whitespace=True)


# Aspect strings such as "3:2" or "16:9".
AspectStr = Annotated[str, StringConstraints(pattern=r"^\d+:\d+$")]


def _aspect_to_ratio(aspect: str) -> float:
    a, b = aspect.split(":")
    return int(a) / int(b)


class Artifact(BaseModel):
    """Top-level artifact descriptor (type, aspect, size, audience)."""

    model_config = _FROZEN_FORBID

    type: ArtifactType
    aspect: AspectStr
    size: str
    audience: str | None = None
    width: int = Field(..., description="Parsed width in px; populated from size.")
    height: int = Field(..., description="Parsed height in px; populated from size.")

    @model_validator(mode="before")
    @classmethod
    def _populate_dimensions(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data
        size = data.get("size")
        if size is None:
            return data
        width, height = validate_size(str(size))
        data = dict(data)
        data["width"] = width
        data["height"] = height
        return data

    @model_validator(mode="after")
    def _check_aspect_consistency(self) -> Artifact:
        declared = _aspect_to_ratio(self.aspect)
        actual = self.width / self.height
        # 5% tolerance — common rounding (e.g. 1536/1024 = 1.5 vs "3:2" = 1.5).
        if abs(declared - actual) / declared > 0.05:
            raise SizeValidationError(
                f"aspect {self.aspect!r} disagrees with size {self.size!r} "
                f"(declared {declared:.3f}, actual {actual:.3f})"
            )
        return self


class TextBlock(BaseModel):
    """A named text slot rendered inside the image."""

    model_config = _FROZEN_FORBID

    slot: Annotated[str, StringConstraints(min_length=1, max_length=40)]
    text: Annotated[str, StringConstraints(min_length=1)]


class Spec(BaseModel):
    """The seven-section content payload (sections 1-7)."""

    model_config = _FROZEN_FORBID

    subject: Annotated[str, StringConstraints(min_length=1)]
    action: Annotated[str, StringConstraints(min_length=1)]
    scene: Annotated[str, StringConstraints(min_length=1)]
    composition: Annotated[str, StringConstraints(min_length=1)]
    style: Annotated[str, StringConstraints(min_length=1)]
    text_blocks: list[TextBlock] = Field(default_factory=list)
    preserve: list[str] = Field(default_factory=list)
    negative: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _check_chunking(self) -> Spec:
        validate_text_block_chunking(self.text_blocks)
        return self


class QualityPolicy(BaseModel):
    """Default quality levels for ship vs. exploration runs."""

    model_config = _FROZEN_FORBID

    default: QualityLevel
    exploration: QualityLevel


class TemplateSpec(BaseModel):
    """Root model — one yaml file deserializes to one TemplateSpec."""

    model_config = _FROZEN_FORBID

    id: str
    domain: Domain
    description: str | None = None
    artifact: Artifact
    spec: Spec
    quality_policy: QualityPolicy
    api_mode: ApiMode
    moderation: Moderation = "auto"
    language_targets: list[Literal["zh-CN", "en"]] = Field(default_factory=lambda: ["zh-CN", "en"])
    grader_profile: GraderProfile
    license: str = "CC-BY-4.0"

    @field_validator("id")
    @classmethod
    def _check_id(cls, v: str) -> str:
        if not ID_PATTERN.match(v):
            raise ValidationError(
                f"id {v!r} must match {ID_PATTERN.pattern} "
                f"(snake_case, starts with a letter)"
            )
        return v

    @field_validator("language_targets")
    @classmethod
    def _check_language_targets(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValidationError("language_targets must be non-empty")
        # de-dupe while preserving order.
        seen = []
        for lang in v:
            if lang not in seen:
                seen.append(lang)
        return seen


__all__ = [
    "ALLOWED_DOMAINS",
    "ApiMode",
    "Artifact",
    "ArtifactType",
    "Domain",
    "GraderProfile",
    "Moderation",
    "QualityLevel",
    "QualityPolicy",
    "Spec",
    "TemplateSpec",
    "TextBlock",
]
