# SPDX-License-Identifier: Apache-2.0
"""`i2w doctor` — probe runtime capabilities of the configured account/org/model."""

import typer
from rich.console import Console

from ..runtimes.capabilities import probe

doctor_app = typer.Typer(
    no_args_is_help=True,
    help="Probe runtime capabilities of your account/org/model.",
)


@doctor_app.command("capabilities")
def capabilities() -> None:
    """Probe what the current account/org/model supports.

    Reports thinking, transparent background, 4K, and partial-image streaming.
    Never crashes when OPENAI_API_KEY is unset; prints a graceful note instead.
    """
    console = Console()
    result = probe()
    console.print("OpenAI gpt-image-2 capability probe", markup=False)
    console.print(f"  has_api_key:                       {result.has_api_key}", markup=False)
    console.print(
        f"  org_verified:                      {result.org_verified}",
        markup=False,
    )
    console.print(
        f"  supports_thinking:                 {result.supports_thinking}",
        markup=False,
    )
    console.print(
        f"  supports_transparent_background:   {result.supports_transparent_background}",
        markup=False,
    )
    console.print(
        f"  max_resolution_seen:               {result.max_resolution_seen}",
        markup=False,
    )
    console.print(
        f"  streaming_partial_images:          {result.streaming_partial_images}",
        markup=False,
    )
    if result.notes:
        console.print("Notes:", markup=False)
        for note in result.notes:
            console.print(f"  - {note}", markup=False)
