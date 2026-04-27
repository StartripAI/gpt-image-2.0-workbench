# SPDX-License-Identifier: Apache-2.0
"""Smoke tests for `i2w gallery build`.

The gallery command renders every V1 template against its canonical demo
vars and writes one ``<domain>.md`` file. These tests verify that the
output is shaped correctly without touching the real ``docs/gallery/``
tree.
"""
from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from image2_workbench.cli import app

runner = CliRunner()


def test_gallery_build_writes_four_domain_files(tmp_path: Path) -> None:
    out_dir = tmp_path / "gallery"
    result = runner.invoke(app, ["gallery", "build", "--out-dir", str(out_dir)])
    assert result.exit_code == 0, (result.stdout, result.stderr)
    expected = {"business.md", "academic.md", "uiux.md", "anime.md"}
    actual = {p.name for p in out_dir.glob("*.md")}
    assert expected <= actual, f"missing domain files; got {actual}"
    for name in expected:
        path = out_dir / name
        size = path.stat().st_size
        assert size >= 1024, f"{name} too small ({size} bytes)"
        body = path.read_text(encoding="utf-8")
        assert "Path A" in body, f"{name} missing 'Path A' guidance"
        # Each domain has 4 templates -> at least 4 H2 sections.
        sections = [line for line in body.splitlines() if line.startswith("## ")]
        assert len(sections) >= 4, (
            f"{name} only has {len(sections)} template sections"
        )


def test_gallery_build_skips_index_md(tmp_path: Path) -> None:
    out_dir = tmp_path / "gallery"
    # Pre-seed an index.md to verify the build doesn't overwrite it.
    out_dir.mkdir(parents=True)
    sentinel = "# my hand-curated index\n"
    (out_dir / "index.md").write_text(sentinel, encoding="utf-8")

    result = runner.invoke(app, ["gallery", "build", "--out-dir", str(out_dir)])
    assert result.exit_code == 0, (result.stdout, result.stderr)
    assert (out_dir / "index.md").read_text(encoding="utf-8") == sentinel


def test_gallery_build_filters_by_domain(tmp_path: Path) -> None:
    out_dir = tmp_path / "gallery"
    result = runner.invoke(
        app, ["gallery", "build", "--out-dir", str(out_dir), "--domain", "business"]
    )
    assert result.exit_code == 0, (result.stdout, result.stderr)
    business = out_dir / "business.md"
    assert business.exists()
    # Other domain files must NOT appear when --domain is set.
    assert not (out_dir / "academic.md").exists()
    assert not (out_dir / "anime.md").exists()
    assert not (out_dir / "uiux.md").exists()


def test_gallery_build_bilingual_blocks_are_present(tmp_path: Path) -> None:
    out_dir = tmp_path / "gallery"
    result = runner.invoke(app, ["gallery", "build", "--out-dir", str(out_dir)])
    assert result.exit_code == 0, (result.stdout, result.stderr)
    body = (out_dir / "business.md").read_text(encoding="utf-8")
    assert "### English" in body
    assert "### 中文" in body
    # The renderer un-doubles inner quotes; the SWOT card should now
    # render `- header: "..."` (one set), not `""..."" `.
    assert '""' not in body
