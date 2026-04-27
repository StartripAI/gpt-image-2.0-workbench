# SPDX-License-Identifier: Apache-2.0
"""`i2w template` — list and render bilingual templates."""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from ..catalog.index import list_templates
from ..compiler.exporters import export_markdown
from ..compiler.loader import load_template, load_vars
from ..compiler.renderer import render
from ..errors import cli_dispatch, validation_error

template_app = typer.Typer(
    no_args_is_help=True,
    help="List and render templates.",
)


@template_app.command("list")
def list_(
    domain: Annotated[
        str | None,
        typer.Option(help="Filter by domain: business, academic, uiux, anime"),
    ] = None,
) -> None:
    """List available templates, optionally filtered by domain."""
    console = Console()
    entries = list_templates(domain=domain)
    if not entries:
        console.print("No templates found", markup=False)
        return
    for e in entries:
        languages = ",".join(e.language_targets) or "-"
        console.print(f"{e.domain:<10} {e.id:<40} [{languages}]", markup=False)


def _resolve_template_path(template_id: str) -> Path:
    for entry in list_templates():
        if entry.id == template_id:
            return entry.path
    raise validation_error(
        "unknown_template",
        f"unknown template id: {template_id}",
        context={"template_id": template_id},
    )


@template_app.command("render")
def render_cmd(
    template_id: Annotated[str, typer.Argument(help="Template id (e.g. business_swot_card)")],
    lang: Annotated[str, typer.Option("--lang", help="zh-CN or en")] = "en",
    vars: Annotated[
        Path | None,
        typer.Option("--vars", help="Path to YAML vars file"),
    ] = None,
    out: Annotated[
        Path | None,
        typer.Option("--out", help="Output markdown path"),
    ] = None,
) -> None:
    """Render a template into a final prompt markdown file."""
    console = Console()

    def _run() -> None:
        if vars is None:
            raise validation_error(
                "vars_file_required",
                "template render requires --vars; no built-in defaults are implied",
                context={"template_id": template_id},
            )
        if not vars.exists():
            raise validation_error(
                "vars_file_missing",
                f"vars file not found: {vars}",
                context={"vars": str(vars)},
            )
        if not vars.is_file():
            raise validation_error(
                "vars_file_not_file",
                f"vars path is not a file: {vars}",
                context={"vars": str(vars)},
            )

        template_path = _resolve_template_path(template_id)
        try:
            spec = load_template(template_path)
            vars_data = load_vars(vars)
            rendered = render(spec, vars_data, lang=lang)
        except Exception as exc:  # noqa: BLE001
            raise validation_error(
                "template_render_failed",
                f"failed to render template {template_id}: {exc}",
                context={"template_id": template_id, "lang": lang},
                cause=repr(exc),
            ) from exc

        if out is None:
            console.print(rendered, markup=False)
            return
        export_markdown(rendered, out)
        console.print(f"Wrote {out}", markup=False)

    raise SystemExit(cli_dispatch(_run))
