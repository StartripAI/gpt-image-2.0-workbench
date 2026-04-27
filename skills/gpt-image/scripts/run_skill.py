# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
# SPDX-License-Identifier: Apache-2.0
"""image2-workbench Skill shim.

Forwards Skill invocations to the `i2w` CLI installed from a local
source checkout. The Skill itself contains no logic; if the CLI isn't
on PATH, prints install instructions.
"""

from __future__ import annotations

import shutil
import subprocess
import sys


def main(argv: list[str]) -> int:
    if not shutil.which("i2w"):
        print(
            "image2-workbench CLI ('i2w') not found on PATH.\n"
            "Install it from the source checkout:\n"
            "  pip install -e \".[dev]\"\n",
            file=sys.stderr,
        )
        return 127
    return subprocess.call(["i2w", *argv])


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
