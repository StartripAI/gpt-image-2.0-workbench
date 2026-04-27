"""Unit tests for sidecar JSON metadata."""

from __future__ import annotations

import json
from pathlib import Path

from image2_workbench.artifacts import sidecar


def _build_sidecar() -> sidecar.Sidecar:
    return sidecar.Sidecar(
        model="gpt-image-2",
        snapshot="gpt-image-2-2026-04-21",
        revised_prompt="A revised prompt",
        size="1024x1024",
        quality="medium",
        n=1,
        format="png",
        background="auto",
        moderation="auto",
        thinking="medium",
        prompt_hash=sidecar.hash_prompt("hello"),
        image_hash=sidecar.hash_image_bytes(b"\x89PNG"),
        cost_estimate_usd=0.042,
        events=["thinking_param_dropped"],
    )


def test_sidecar_round_trip(tmp_path: Path):
    sc = _build_sidecar()
    image_path = tmp_path / "out.png"
    image_path.write_bytes(b"\x89PNG")
    sidecar_path = sidecar.write(sc, image_path)
    assert sidecar_path == image_path.with_name("out.png.sidecar.json")
    assert sidecar_path.exists()

    raw = json.loads(sidecar_path.read_text(encoding="utf-8"))
    assert raw["model"] == "gpt-image-2"
    assert raw["snapshot"] == "gpt-image-2-2026-04-21"
    assert raw["revised_prompt"] == "A revised prompt"
    assert raw["size"] == "1024x1024"
    assert raw["quality"] == "medium"
    assert raw["n"] == 1
    assert raw["format"] == "png"
    assert raw["background"] == "auto"
    assert raw["moderation"] == "auto"
    assert raw["thinking"] == "medium"
    assert raw["prompt_hash"] == sidecar.hash_prompt("hello")
    assert isinstance(raw["image_hash"], str) and len(raw["image_hash"]) == 64
    assert raw["cost_estimate_usd"] == 0.042
    assert raw["events"] == ["thinking_param_dropped"]
    assert isinstance(raw["timestamp"], str) and "T" in raw["timestamp"]


def test_sidecar_minimal_optional_fields(tmp_path: Path):
    sc = sidecar.Sidecar(
        model="gpt-image-2",
        snapshot="gpt-image-2-2026-04-21",
        size="1024x1024",
        quality="auto",
        n=1,
        format="png",
        background="auto",
        moderation="auto",
        prompt_hash="x" * 64,
        image_hash="y" * 64,
    )
    image_path = tmp_path / "img.png"
    image_path.write_bytes(b"data")
    p = sidecar.write(sc, image_path)
    raw = json.loads(p.read_text(encoding="utf-8"))
    assert raw["thinking"] is None
    assert raw["revised_prompt"] is None
    assert raw["cost_estimate_usd"] is None
    assert raw["events"] == []


def test_hash_prompt_is_sha256_hex():
    h = sidecar.hash_prompt("test")
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_hash_image_file_matches_bytes(tmp_path: Path):
    p = tmp_path / "x.bin"
    payload = b"some image bytes"
    p.write_bytes(payload)
    assert sidecar.hash_image_file(p) == sidecar.hash_image_bytes(payload)
