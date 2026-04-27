# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the image artifact writer."""

from __future__ import annotations

import base64
import os
from pathlib import Path

import pytest

from image2_workbench.artifacts import writer


def test_write_image_round_trip(tmp_path: Path):
    raw = os.urandom(1024)
    b64 = base64.b64encode(raw).decode("ascii")
    out = tmp_path / "out.png"
    written = writer.write_image(b64, out, "png")
    assert written == out
    assert written.read_bytes() == raw


def test_write_image_creates_parent_dirs(tmp_path: Path):
    raw = b"\x89PNG\r\n\x1a\n"  # 8-byte PNG sig
    b64 = base64.b64encode(raw).decode("ascii")
    out = tmp_path / "deep" / "nested" / "img.png"
    written = writer.write_image(b64, out, "png")
    assert written.exists()
    assert written.read_bytes() == raw


def test_write_image_rejects_empty_b64(tmp_path: Path):
    with pytest.raises(ValueError):
        writer.write_image("", tmp_path / "x.png", "png")


def test_write_image_rejects_empty_fmt(tmp_path: Path):
    with pytest.raises(ValueError):
        writer.write_image("ZmFrZQ==", tmp_path / "x.png", "")
