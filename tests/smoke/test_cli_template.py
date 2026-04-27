# SPDX-License-Identifier: Apache-2.0
"""Smoke tests for `i2w template` CLI contract."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from image2_workbench.cli import app

runner = CliRunner()

REPO_ROOT = Path(__file__).resolve().parents[2]
SWOT_VARS = REPO_ROOT / "templates" / "business" / "_vars_examples" / "swot_acme.yml"


def test_template_render_requires_vars() -> None:
    result = runner.invoke(app, ["template", "render", "business_swot_card"])
    assert result.exit_code == 4, (result.stdout, result.stderr)
    assert "vars_file_required" in result.stderr


def test_template_render_invalid_lang_exits_structured_validation() -> None:
    result = runner.invoke(
        app,
        [
            "template",
            "render",
            "business_swot_card",
            "--vars",
            str(SWOT_VARS),
            "--lang",
            "fr",
        ],
    )
    assert result.exit_code == 4, (result.stdout, result.stderr)
    assert "template_render_failed" in result.stderr
    assert "traceback" not in result.stderr.lower()


def test_template_render_writes_raw_single_language_prompt(tmp_path: Path) -> None:
    out = tmp_path / "prompt.md"
    result = runner.invoke(
        app,
        [
            "template",
            "render",
            "business_swot_card",
            "--vars",
            str(SWOT_VARS),
            "--lang",
            "en",
            "--out",
            str(out),
        ],
    )
    assert result.exit_code == 0, (result.stdout, result.stderr)
    text = out.read_text(encoding="utf-8")
    assert "```" not in text
    assert "Acme Robotics" in text
