# SPDX-License-Identifier: Apache-2.0
"""Smoke tests for the root `i2w` help and version output."""

from typer.testing import CliRunner

from image2_workbench.cli import app

runner = CliRunner()


def test_root_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0, result.stdout
    for verb in [
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
    ]:
        assert verb in result.stdout, f"missing verb {verb!r} in --help output"


def test_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0, result.stdout
    assert "image2-workbench" in result.stdout
    assert "0.2.0" in result.stdout
