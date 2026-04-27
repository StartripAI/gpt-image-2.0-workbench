# SPDX-License-Identifier: Apache-2.0
"""`i2w version` — print the package version.

The version verb is wired directly on the root `app` in `cli.py`; this module
exists so collaborators have a predictable place to extend the verb later
(e.g. with build-info or commit-sha).
"""

import typer

from .. import __version__


def print_version() -> None:
    """Print `image2-workbench {version}` to stdout."""
    typer.echo(f"image2-workbench {__version__}")
