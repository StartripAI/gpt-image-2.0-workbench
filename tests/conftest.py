# SPDX-License-Identifier: Apache-2.0
"""Test bootstrap: sys.path + Rich/Typer ANSI suppression for CI stability.

CI runners (and some shells) report a TTY-ish context to Rich, which then
emits ANSI color sequences that break naive substring asserts on stdout/
stderr. We force NO_COLOR and TERM=dumb at import time so every Rich
console instantiated by `image2_workbench` during tests stays plain. We
also expose a `strip_ansi` helper for tests that still want defence in
depth (or that capture output from a subprocess that ignores env vars).
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

# Disable color BEFORE any module under test imports rich/typer.
os.environ.setdefault("NO_COLOR", "1")
os.environ.setdefault("TERM", "dumb")

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# Standard 7-bit and 8-bit ANSI CSI / OSC escape stripper.
_ANSI_RE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def strip_ansi(text: str) -> str:
    """Strip ANSI escape sequences from ``text`` for stable assertions."""
    return _ANSI_RE.sub("", text)
