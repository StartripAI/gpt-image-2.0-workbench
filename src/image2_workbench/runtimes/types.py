"""Shared runtime types, request/response models, and exceptions.

These models are the contract between the CLI / SDK callers and the
concrete runtime adapters (``images_api``, ``responses_api``). They are
intentionally minimal — fields map almost 1:1 to the OpenAI API,
except for ``fmt`` which is renamed in the adapter to avoid shadowing
Python's built-in ``format``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, model_validator

Quality = Literal["low", "medium", "high", "auto"]
Format = Literal["png", "jpeg", "webp"]
Background = Literal["auto", "opaque"]
Moderation = Literal["auto", "low"]
ApiMode = Literal["images_generate", "images_edit", "responses"]
Thinking = Literal["auto", "low", "medium", "high"]


class GenerateRequest(BaseModel):
    """Request envelope for ``images.generate`` and the Responses tool path."""

    prompt: str
    model: str = "gpt-image-2"
    size: str = "1024x1024"
    quality: Quality = "medium"
    n: int = Field(1, ge=1, le=10)
    fmt: Format = "png"
    output_compression: int | None = Field(None, ge=0, le=100)
    background: Background = "auto"
    moderation: Moderation = "auto"
    partial_images: int | None = Field(None, ge=0, le=3)
    thinking: Thinking | None = None

    @model_validator(mode="after")
    def _check_compression_format(self) -> GenerateRequest:
        # output_compression is only meaningful for lossy formats per docs.
        if self.output_compression is not None and self.fmt not in ("jpeg", "webp"):
            raise ValueError(
                "output_compression is only valid when fmt is 'jpeg' or 'webp'; "
                f"got fmt={self.fmt!r}"
            )
        return self


class EditRequest(BaseModel):
    """Request envelope for ``images.edit`` (1+ source images, optional mask)."""

    prompt: str
    model: str = "gpt-image-2"
    images: list[Path] = Field(..., min_length=1)
    mask: Path | None = None
    size: str = "1024x1024"
    quality: Quality = "medium"
    moderation: Moderation = "auto"
    background: Background = "auto"
    fmt: Format = "png"


class GenerateResponse(BaseModel):
    """Normalized response — base64 image payloads plus a few audit fields."""

    images_b64: list[str]
    revised_prompt: str | None = None
    snapshot: str
    model: str


class CapabilityProbe(BaseModel):
    """Result of a best-effort environment / account probe.

    All fields are advisory. The probe is designed to never raise.
    """

    has_api_key: bool
    org_verified: bool | None = None
    supports_thinking: bool | None = None
    # Per OpenAI gpt-image-2 docs the API only exposes auto/opaque.
    supports_transparent_background: bool = False
    max_resolution_seen: str | None = None
    streaming_partial_images: bool | None = None
    notes: list[str] = Field(default_factory=list)


class RuntimeError_(Exception):  # noqa: N801 — intentional trailing underscore
    """Base runtime error for image2_workbench (avoids shadowing builtin)."""


class UnsupportedParameterError(RuntimeError_):
    """A request parameter isn't supported by the target snapshot."""


class ApiCallError(RuntimeError_):
    """Wraps an underlying OpenAI SDK exception with our own context."""
