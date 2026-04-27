# SPDX-License-Identifier: Apache-2.0
"""image2-workbench CLI entry point (`i2w`)."""

import typer

from . import __version__
from .commands.batch import batch_app
from .commands.catalog import catalog_app
from .commands.cost import cost_app
from .commands.doctor import doctor_app
from .commands.eval_cmd import eval_app
from .commands.gallery import gallery_app
from .commands.ledger import ledger_app
from .commands.preflight import preflight_command
from .commands.render import render_app
from .commands.template import template_app

app = typer.Typer(
    name="i2w",
    help="image2-workbench: gpt-image-2 production workbench (Skill + CLI + bilingual templates)",
    no_args_is_help=True,
    add_completion=False,
)

app.add_typer(catalog_app, name="catalog")
app.add_typer(template_app, name="template")
app.add_typer(render_app, name="render")
app.add_typer(batch_app, name="batch")
app.add_typer(eval_app, name="eval")
app.add_typer(cost_app, name="cost")
app.add_typer(doctor_app, name="doctor")
app.command(
    "preflight",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)(preflight_command)
app.add_typer(ledger_app, name="ledger")
app.add_typer(gallery_app, name="gallery")


@app.command("version")
def version() -> None:
    """Print image2-workbench version."""
    typer.echo(f"image2-workbench {__version__}")


if __name__ == "__main__":
    app()
