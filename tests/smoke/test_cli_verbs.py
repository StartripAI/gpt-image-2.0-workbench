# SPDX-License-Identifier: Apache-2.0
"""Smoke tests for each top-level `i2w` verb's --help output."""

import pytest
from typer.testing import CliRunner

from image2_workbench.cli import app

runner = CliRunner()

VERB_SUBVERBS = {
    "catalog": ("list", "search"),
    "template": ("list", "render"),
    "render": ("generate", "edit"),
    "batch": ("sweep",),
    "eval": ("run", "report"),
    "cost": ("estimate",),
    "doctor": ("capabilities",),
}


@pytest.mark.parametrize("verb,subverbs", list(VERB_SUBVERBS.items()))
def test_verb_help_lists_subverbs(verb: str, subverbs: tuple[str, ...]) -> None:
    result = runner.invoke(app, [verb, "--help"])
    assert result.exit_code == 0, result.stdout
    for sub in subverbs:
        assert sub in result.stdout, f"verb {verb!r} help missing sub-verb {sub!r}"


def test_version_verb_help() -> None:
    result = runner.invoke(app, ["version", "--help"])
    assert result.exit_code == 0, result.stdout
    assert "version" in result.stdout.lower()


@pytest.mark.parametrize(
    "argv,expected_substring",
    [
        (["catalog", "search", "swot"], "Search"),
        (["catalog", "list"], "Catalog"),
        (["template", "list"], "business_swot_card"),
        (
            ["render", "generate", "--prompt-file", "p.md", "--quality", "high", "-n", "2"],
            "[unimplemented]",
        ),
        (
            ["render", "edit", "--prompt-file", "p.md", "-i", "a.png", "-i", "b.png"],
            "[unimplemented]",
        ),
        (["batch", "sweep", "--template", "t/x", "--vars", "v.yml"], "[unimplemented]"),
        (["eval", "report", "--format", "json"], "V1 does not persist"),
        (["cost", "estimate", "--size", "1536x1024", "--quality", "high", "-n", "3"], "track="),
    ],
)
def test_verb_parses_args(argv: list[str], expected_substring: str) -> None:
    result = runner.invoke(app, argv)
    assert result.exit_code == 0, (argv, result.stdout, result.stderr)
    assert expected_substring in result.stdout, (argv, result.stdout)
