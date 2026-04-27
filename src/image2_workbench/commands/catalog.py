# SPDX-License-Identifier: Apache-2.0
"""`i2w catalog` — browse and search the template/corpus catalog."""

from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from ..catalog.index import list_templates, search_templates

catalog_app = typer.Typer(
    no_args_is_help=True,
    help="Browse and search the template/corpus catalog.",
)


def _render_entries(console: Console, entries: list, header: str) -> None:
    if not entries:
        console.print(f"{header}: no entries found", markup=False)
        return
    table = Table(title=header)
    table.add_column("id")
    table.add_column("domain")
    table.add_column("artifact")
    table.add_column("grader")
    table.add_column("languages")
    for e in entries:
        table.add_row(
            e.id,
            e.domain,
            e.artifact_type,
            e.grader_profile or "-",
            ",".join(e.language_targets),
        )
    console.print(table)


@catalog_app.command("list")
def list_(
    domain: Annotated[
        str | None,
        typer.Option(help="Filter by domain: business, academic, uiux, anime"),
    ] = None,
) -> None:
    """List entries in the catalog, optionally filtered by domain."""
    console = Console()
    entries = list_templates(domain=domain)
    title = f"Catalog ({domain or 'all domains'}) — {len(entries)} entries"
    _render_entries(console, entries, title)


@catalog_app.command("search")
def search(
    query: Annotated[str, typer.Argument(help="Free-text query")],
    domain: Annotated[
        str | None,
        typer.Option(help="Restrict search to a single domain"),
    ] = None,
) -> None:
    """Search the catalog by free-text query."""
    console = Console()
    entries = search_templates(query, domain=domain)
    title = f"Search '{query}' ({domain or 'all domains'}) — {len(entries)} hits"
    _render_entries(console, entries, title)
