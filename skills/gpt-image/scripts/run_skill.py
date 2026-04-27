# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""image2-workbench Skill shim.

Forwards Skill invocations to the `i2w` CLI installed via the
`image2-workbench` package. The Skill itself contains no logic; if the
CLI isn't on PATH, prints install instructions.
"""

from __future__ import annotations

import shutil
import subprocess
import sys


def main(argv: list[str]) -> int:
    if not shutil.which("i2w"):
        print(
            "image2-workbench CLI ('i2w') not found on PATH.\n"
            "Install it with one of:\n"
            "  pip install image2-workbench\n"
            "  pip install -e .   (from a checkout)\n",
            file=sys.stderr,
        )
        return 127
    return subprocess.call(["i2w", *argv])


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
