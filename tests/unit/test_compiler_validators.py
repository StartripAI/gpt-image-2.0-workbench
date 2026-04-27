# SPDX-License-Identifier: Apache-2.0
"""Tests for low-level validators (size, format, background, params, chunking)."""

from __future__ import annotations

import pytest

from image2_workbench.compiler.schema import TextBlock
from image2_workbench.compiler.validators import (
    BackgroundValidationError,
    FormatValidationError,
    SizeValidationError,
    TextBlockValidationError,
    UnsupportedParameterError,
    is_experimental_size,
    validate_background,
    validate_format_compression,
    validate_no_input_fidelity,
    validate_size,
    validate_text_block_chunking,
)

# ---------- size ----------


@pytest.mark.parametrize(
    "size,expected",
    [
        ("1024x1024", (1024, 1024)),
        ("1536x1024", (1536, 1024)),
        ("1024x1536", (1024, 1536)),
        ("3840x2160", (3840, 2160)),
        ("2048x1024", (2048, 1024)),  # 2:1
    ],
)
def test_validate_size_ok(size, expected):
    assert validate_size(size) == expected


@pytest.mark.parametrize(
    "size",
    [
        "1023x1024",   # not a multiple of 16
        "1024x1023",   # not a multiple of 16
        "4096x4096",   # exceeds max edge
        "3856x1024",   # > max edge
        "640x640",     # below pixel floor (409,600)
        "3840x1024",   # aspect 3.75:1, exceeds 3:1
        "16x16",       # below pixel floor
        "garbage",
        "1024",
        "1024x",
        "1024x-128",
    ],
)
def test_validate_size_rejected(size):
    with pytest.raises(SizeValidationError):
        validate_size(size)


def test_validate_size_non_string():
    with pytest.raises(SizeValidationError):
        validate_size(1024)  # type: ignore[arg-type]


def test_is_experimental_size():
    # Standard sizes are not experimental.
    assert is_experimental_size(1024, 1024) is False
    assert is_experimental_size(1536, 1024) is False
    assert is_experimental_size(2560, 1440) is False
    # Beyond either threshold flips it on.
    assert is_experimental_size(3840, 2160) is True
    assert is_experimental_size(2576, 1440) is True
    assert is_experimental_size(2560, 1456) is True


# ---------- format / compression ----------


def test_format_png_no_compression_ok():
    validate_format_compression("png", None)


def test_format_jpeg_with_compression_ok():
    validate_format_compression("jpeg", 50)


def test_format_jpeg_uppercase_ok():
    validate_format_compression("JPEG", 80)


def test_format_webp_with_compression_ok():
    validate_format_compression("webp", 90)


def test_format_png_with_compression_rejected():
    with pytest.raises(FormatValidationError):
        validate_format_compression("png", 50)


def test_format_unknown_rejected():
    with pytest.raises(FormatValidationError):
        validate_format_compression("tiff", None)


@pytest.mark.parametrize("bad", [-1, 101, "high"])
def test_format_compression_out_of_range(bad):
    with pytest.raises(FormatValidationError):
        validate_format_compression("jpeg", bad)  # type: ignore[arg-type]


# ---------- background ----------


def test_background_auto_ok():
    validate_background("auto")


def test_background_opaque_ok():
    validate_background("opaque")


def test_background_transparent_rejected_with_clear_message():
    with pytest.raises(BackgroundValidationError) as exc:
        validate_background("transparent")
    assert "transparent" in str(exc.value)
    assert "auto" in str(exc.value) or "opaque" in str(exc.value)


def test_background_transparent_case_insensitive():
    with pytest.raises(BackgroundValidationError):
        validate_background("Transparent")


def test_background_unknown_rejected():
    with pytest.raises(BackgroundValidationError):
        validate_background("rainbow")


# ---------- input_fidelity ----------


def test_input_fidelity_rejected_in_extras():
    with pytest.raises(UnsupportedParameterError):
        validate_no_input_fidelity({"input_fidelity": 1.0})


def test_input_fidelity_rejected_case_insensitive():
    with pytest.raises(UnsupportedParameterError):
        validate_no_input_fidelity({"Input_Fidelity": 0.5})


def test_other_extras_ok():
    validate_no_input_fidelity({"seed": 42, "n": 1})


def test_non_dict_extras_ignored():
    validate_no_input_fidelity(None)  # type: ignore[arg-type]


# ---------- text-block chunking ----------


def test_text_block_within_limit_ok():
    blocks = [TextBlock(slot="header", text="x" * 80)]
    validate_text_block_chunking(blocks)


def test_text_block_exceeding_limit_rejected():
    blocks = [TextBlock(slot="header", text="x" * 81)]
    with pytest.raises(TextBlockValidationError):
        validate_text_block_chunking(blocks)


def test_text_block_chunking_reports_slot_name():
    blocks = [
        TextBlock(slot="header", text="ok"),
        TextBlock(slot="footer", text="x" * 200),
    ]
    with pytest.raises(TextBlockValidationError) as exc:
        validate_text_block_chunking(blocks)
    assert "footer" in str(exc.value)
