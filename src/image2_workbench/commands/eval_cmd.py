# SPDX-License-Identifier: Apache-2.0
"""`i2w eval` — run evaluation rubrics and produce reports."""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from ..evals.report import report_json, report_markdown
from ..evals.runner import run_rubric_file

eval_app = typer.Typer(
    no_args_is_help=True,
    help="Run evaluation rubrics against the workbench.",
)


@eval_app.command("run")
def run(
    rubric_file: Annotated[
        Path,
        typer.Argument(help="Path to a YAML rubric file under tests/golden/"),
    ],
    format_: Annotated[
        str,
        typer.Option("--format", help="markdown | json"),
    ] = "markdown",
) -> None:
    """Execute an evaluation rubric against the current build."""
    console = Console()
    if not rubric_file.exists():
        raise typer.BadParameter(f"rubric file not found: {rubric_file}")
    outcomes = run_rubric_file(rubric_file)
    rendered = report_json(outcomes) if format_ == "json" else report_markdown(outcomes)
    console.print(rendered, markup=False)


@eval_app.command("report")
def report(
    format_: Annotated[
        str,
        typer.Option("--format", help="markdown | json"),
    ] = "markdown",
) -> None:
    """Render a report from the latest evaluation results.

    V1: this is a thin wrapper that prompts users to use `eval run` instead;
    persistent eval state is V2.
    """
    console = Console()
    console.print(
        "V1 does not persist eval results. Use `i2w eval run <rubric_file>` "
        f"--format {format_} to run and report in one step.",
        markup=False,
    )
