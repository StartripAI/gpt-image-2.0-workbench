# SPDX-License-Identifier: Apache-2.0
"""Smoke tests for the V1.5 ``i2w cost`` CLI surface."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from image2_workbench.commands.cost import cost_app

# We invoke the cost subapp directly so these tests don't depend on
# whichever cli.py registration X4 is wiring up in parallel.

runner = CliRunner()


def test_estimate_basic_outputs_track() -> None:
    result = runner.invoke(cost_app, ["estimate", "--size", "1024x1024", "--quality", "medium"])
    assert result.exit_code == 0, result.stdout
    assert "track=" in result.stdout


def test_estimate_token_estimate_mentions_tokens() -> None:
    result = runner.invoke(
        cost_app,
        [
            "estimate",
            "--token-estimate",
            "--size",
            "1024x1024",
            "--quality",
            "high",
            "--prompt",
            "a polished editorial chart",
        ],
    )
    assert result.exit_code == 0, result.stdout
    assert "token" in result.stdout.lower()
    assert "track=" in result.stdout


def test_compare_six_rows() -> None:
    result = runner.invoke(
        cost_app,
        [
            "compare",
            "--size",
            "1024x1024,1536x1024",
            "--quality",
            "low,medium,high",
        ],
    )
    assert result.exit_code == 0, result.stdout
    # 2 sizes x 3 qualities = 6 cells. Each cell prints "$" twice
    # (per_image and total). Counting "$" is a robust way to assert
    # the matrix shape regardless of Rich's box-drawing chars.
    dollar_count = result.stdout.count("$")
    assert dollar_count >= 12, (
        f"expected >=12 '$' tokens in 2x3 matrix; got {dollar_count}\n"
        f"stdout:\n{result.stdout}"
    )


def test_compare_default_three_by_three() -> None:
    result = runner.invoke(cost_app, ["compare"])
    assert result.exit_code == 0, result.stdout
    # 3 sizes x 3 qualities = 9 cells.
    assert result.stdout.count("$") >= 18


def test_budget_under_limit_exits_zero(tmp_path: Path) -> None:
    plan = tmp_path / "plan.yml"
    plan.write_text(
        "- size: 1024x1024\n  quality: low\n  n: 1\n",
        encoding="utf-8",
    )
    result = runner.invoke(
        cost_app,
        ["budget", "--plan", str(plan), "--max-usd", "1.0"],
    )
    assert result.exit_code == 0, result.stdout
    assert "OK" in result.stdout


def test_budget_over_limit_exits_validation(tmp_path: Path) -> None:
    plan = tmp_path / "plan.yml"
    # 1024x1024 low costs $0.006 per image — so $0.001 ceiling busts.
    plan.write_text(
        "- size: 1024x1024\n  quality: low\n  n: 1\n",
        encoding="utf-8",
    )
    result = runner.invoke(
        cost_app,
        ["budget", "--plan", str(plan), "--max-usd", "0.001"],
    )
    # Whether or not X1's errors module is loaded, validation maps to 4.
    assert result.exit_code == 4, (result.exit_code, result.stdout, result.stderr)


def test_budget_missing_plan_fails(tmp_path: Path) -> None:
    missing = tmp_path / "does_not_exist.yml"
    result = runner.invoke(
        cost_app,
        ["budget", "--plan", str(missing)],
    )
    assert result.exit_code == 4, (result.exit_code, result.stdout, result.stderr)


def test_budget_malformed_plan_rejected(tmp_path: Path) -> None:
    plan = tmp_path / "p.yml"
    plan.write_text("not a list\n", encoding="utf-8")
    result = runner.invoke(
        cost_app,
        ["budget", "--plan", str(plan)],
    )
    assert result.exit_code == 4


@pytest.mark.parametrize(
    "argv",
    [
        ["estimate", "--size", "1024x1024", "--quality", "low", "-n", "5"],
        ["estimate", "--size", "1536x1024", "--quality", "high", "-n", "3"],
    ],
)
def test_estimate_various_combinations(argv: list[str]) -> None:
    result = runner.invoke(cost_app, argv)
    assert result.exit_code == 0, result.stdout
    assert "total=$" in result.stdout
