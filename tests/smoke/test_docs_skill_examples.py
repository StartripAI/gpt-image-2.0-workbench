# SPDX-License-Identifier: Apache-2.0
"""Smoke checks for docs and Skill command examples."""

from __future__ import annotations

import re
from pathlib import Path

from typer.testing import CliRunner

from image2_workbench.catalog.index import list_templates
from image2_workbench.cli import app

REPO_ROOT = Path(__file__).resolve().parents[2]

GETTING_STARTED = [
    REPO_ROOT / "docs" / "getting-started.en.md",
    REPO_ROOT / "docs" / "getting-started.zh.md",
]
DOCS_AND_SKILL = [
    *GETTING_STARTED,
    REPO_ROOT / "docs" / "cost-modeling.md",
    REPO_ROOT / "docs" / "gallery" / "index.md",
    REPO_ROOT / "skills" / "gpt-image" / "SKILL.md",
]
TOP_LEVEL_COMMANDS = [
    "catalog",
    "template",
    "render",
    "batch",
    "eval",
    "cost",
    "doctor",
    "preflight",
    "ledger",
    "gallery",
    "version",
]

runner = CliRunner()


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_getting_started_lists_current_top_level_commands() -> None:
    for path in GETTING_STARTED:
        text = _read(path)
        assert "11" in text
        for command in TOP_LEVEL_COMMANDS:
            assert f"`{command}`" in text, f"{path} is missing {command!r}"
        assert "eight verbs" not in text
        assert "8 个" not in text


def test_docs_do_not_reference_removed_or_stale_command_shapes() -> None:
    stale_patterns = [
        "template list --lang",
        "--prompt prompt.md",
        "out/swot.png.json",
        "--accept-experimental",
        "cost budget --size",
        "`--batch`",
        "not yet wired",
        "landing in V1.5",
        "business/swot",
        "anime/storyboard-4panel",
        "product/bg-swap",
        "--reference",
        "--preserve",
    ]
    for path in DOCS_AND_SKILL:
        text = _read(path)
        for pattern in stale_patterns:
            assert pattern not in text, f"{path} still contains {pattern!r}"


def test_skill_template_render_examples_use_real_template_ids() -> None:
    skill_text = _read(REPO_ROOT / "skills" / "gpt-image" / "SKILL.md")
    rendered_ids = re.findall(r"i2w template render\s+([a-z0-9_]+)", skill_text)
    template_ids = {entry.id for entry in list_templates()}

    assert {"business_swot_card", "uiux_web_dashboard", "anime_comic_8panel"} <= set(
        rendered_ids
    )
    assert rendered_ids
    assert set(rendered_ids) <= template_ids


def test_documented_offline_commands_match_cli_shape(tmp_path: Path) -> None:
    list_result = runner.invoke(app, ["template", "list", "--domain", "business"])
    assert list_result.exit_code == 0, list_result.stdout
    assert "business_swot_card" in list_result.stdout

    prompt_file = tmp_path / "swot_prompt.md"
    render_result = runner.invoke(
        app,
        [
            "template",
            "render",
            "business_swot_card",
            "--lang",
            "en",
            "--vars",
            str(
                REPO_ROOT
                / "templates"
                / "business"
                / "_vars_examples"
                / "swot_acme.yml"
            ),
            "--out",
            str(prompt_file),
        ],
    )
    assert render_result.exit_code == 0, render_result.stdout
    assert prompt_file.exists()

    preflight_result = runner.invoke(
        app,
        [
            "preflight",
            str(prompt_file),
            "--no-moderation-api",
            "--template-id",
            "business_swot_card",
        ],
    )
    assert preflight_result.exit_code == 0, preflight_result.stdout

    plan_file = tmp_path / "budget.yml"
    plan_file.write_text(
        "- size: 1024x1024\n  quality: medium\n  n: 200\n",
        encoding="utf-8",
    )
    budget_result = runner.invoke(
        app,
        ["cost", "budget", "--plan", str(plan_file), "--max-usd", "12.00"],
    )
    assert budget_result.exit_code == 0, budget_result.stdout
    assert "total=$10.6000" in budget_result.stdout

    gallery_result = runner.invoke(
        app,
        [
            "gallery",
            "build",
            "--domain",
            "anime",
            "--out-dir",
            str(tmp_path / "gallery"),
        ],
    )
    assert gallery_result.exit_code == 0, gallery_result.stdout
    assert (tmp_path / "gallery" / "anime.md").exists()


def test_cli_help_exposes_current_render_and_cost_options() -> None:
    template_help = runner.invoke(app, ["template", "list", "--help"])
    assert template_help.exit_code == 0, template_help.stdout
    assert "--domain" in template_help.stdout
    assert "--lang" not in template_help.stdout

    render_help = runner.invoke(app, ["render", "generate", "--help"])
    assert render_help.exit_code == 0, render_help.stdout
    assert "--prompt-file" in render_help.stdout
    assert "--prompt " not in render_help.stdout

    budget_help = runner.invoke(app, ["cost", "budget", "--help"])
    assert budget_help.exit_code == 0, budget_help.stdout
    assert "--plan" in budget_help.stdout
    assert "--size" not in budget_help.stdout
