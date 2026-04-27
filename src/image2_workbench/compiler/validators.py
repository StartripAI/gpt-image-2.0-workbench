# SPDX-License-Identifier: Apache-2.0
"""Validators that enforce gpt-image-2 hard constraints.

These functions are reused by `schema.py` (during model validation) and by
runtime entry points; keeping them here avoids circular imports between the
template DSL and the request shapers.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .schema import TextBlock


class ValidationError(ValueError):
    """Base for image2-workbench validation failures."""


class SizeValidationError(ValidationError):
    """Raised when an image size violates gpt-image-2 constraints."""


class FormatValidationError(ValidationError):
    """Raised for format/compression mismatches."""


class BackgroundValidationError(ValidationError):
    """Raised when a forbidden background mode is requested."""


class UnsupportedParameterError(ValidationError):
    """Raised when an unsupported gpt-image-2 parameter is supplied."""


class TextBlockValidationError(ValidationError):
    """Raised when a text block exceeds chunking limits."""


_SIZE_PATTERN = re.compile(r"^(\d+)x(\d+)$")

# Hard bounds taken from the gpt-image-2 spec.
MIN_PIXELS = 655_360
MAX_PIXELS = 8_294_400
MAX_EDGE = 3840
SIZE_MULTIPLE = 16
MAX_ASPECT_RATIO = 3.0
EXPERIMENTAL_MAX_LONG_EDGE = 2560
EXPERIMENTAL_MAX_SHORT_EDGE = 1440

TEXT_BLOCK_CHAR_LIMIT = 80


def validate_size(s: str) -> tuple[int, int]:
    """Parse "WxH" and assert all gpt-image-2 size constraints.

    Returns the (width, height) tuple on success.
    """
    if not isinstance(s, str):
        raise SizeValidationError(f"size must be a string like '1024x1024', got {type(s).__name__}")
    match = _SIZE_PATTERN.match(s.strip())
    if not match:
        raise SizeValidationError(f"size must match WxH (e.g. '1024x1024'), got {s!r}")
    width = int(match.group(1))
    height = int(match.group(2))
    if width <= 0 or height <= 0:
        raise SizeValidationError(f"size {s!r} has non-positive dimension")
    if width % SIZE_MULTIPLE != 0 or height % SIZE_MULTIPLE != 0:
        raise SizeValidationError(
            f"size {s!r} must have both dimensions multiples of {SIZE_MULTIPLE}"
        )
    if max(width, height) > MAX_EDGE:
        raise SizeValidationError(
            f"size {s!r} exceeds max edge {MAX_EDGE} (got {max(width, height)})"
        )
    long_edge = max(width, height)
    short_edge = min(width, height)
    aspect = long_edge / short_edge
    if aspect > MAX_ASPECT_RATIO:
        raise SizeValidationError(
            f"size {s!r} has aspect ratio {aspect:.2f}:1, max is {MAX_ASPECT_RATIO}:1"
        )
    pixels = width * height
    if pixels < MIN_PIXELS:
        raise SizeValidationError(
            f"size {s!r} total pixels {pixels} below floor {MIN_PIXELS}"
        )
    if pixels > MAX_PIXELS:
        raise SizeValidationError(
            f"size {s!r} total pixels {pixels} above ceiling {MAX_PIXELS}"
        )
    return width, height


def is_experimental_size(w: int, h: int) -> bool:
    """True when the size is supported but flagged experimental."""
    return max(w, h) > EXPERIMENTAL_MAX_LONG_EDGE or min(w, h) > EXPERIMENTAL_MAX_SHORT_EDGE


def validate_format_compression(fmt: str, compression: int | None) -> None:
    """Compression is only meaningful for jpeg/webp."""
    if fmt is None:
        return
    fmt_lc = fmt.lower()
    if fmt_lc not in {"png", "jpeg", "jpg", "webp"}:
        raise FormatValidationError(
            f"unsupported output_format {fmt!r}; expected png/jpeg/webp"
        )
    if compression is None:
        return
    if not isinstance(compression, int) or not 0 <= compression <= 100:
        raise FormatValidationError(
            f"output_compression must be 0-100, got {compression!r}"
        )
    if fmt_lc == "png":
        raise FormatValidationError(
            "output_compression is only valid with jpeg or webp; png does not accept it"
        )


def validate_background(bg: str) -> None:
    """gpt-image-2 only supports 'auto' and 'opaque'; transparent is rejected."""
    if bg is None:
        return
    if not isinstance(bg, str):
        raise BackgroundValidationError(
            f"background must be a string, got {type(bg).__name__}"
        )
    bg_lc = bg.lower()
    if bg_lc == "transparent":
        raise BackgroundValidationError(
            "background='transparent' is not supported by gpt-image-2; "
            "use 'auto' or 'opaque'"
        )
    if bg_lc not in {"auto", "opaque"}:
        raise BackgroundValidationError(
            f"background must be 'auto' or 'opaque', got {bg!r}"
        )


def validate_no_input_fidelity(extra: dict[str, Any]) -> None:
    """gpt-image-2 does not support input_fidelity; reject before the API call."""
    if not isinstance(extra, dict):
        return
    for key in extra:
        if str(key).lower() == "input_fidelity":
            raise UnsupportedParameterError(
                "input_fidelity is not a supported gpt-image-2 parameter; "
                "remove it from the request"
            )


def validate_text_block_chunking(blocks: list[TextBlock]) -> None:
    """Each text block must stay under TEXT_BLOCK_CHAR_LIMIT chars."""
    for idx, block in enumerate(blocks):
        text = getattr(block, "text", None)
        slot = getattr(block, "slot", f"#{idx}")
        if text is None:
            raise TextBlockValidationError(
                f"text_block[{slot}] is missing 'text'"
            )
        if len(text) > TEXT_BLOCK_CHAR_LIMIT:
            raise TextBlockValidationError(
                f"text_block[{slot}] is {len(text)} chars; "
                f"chunk into pieces of <= {TEXT_BLOCK_CHAR_LIMIT}"
            )
