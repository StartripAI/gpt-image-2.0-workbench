# SPDX-License-Identifier: Apache-2.0
"""Smoke tests for the L1 Skill bundle (skills/gpt-image)."""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_DIR = REPO_ROOT / "skills" / "gpt-image"


def test_skill_md_exists_and_well_formed():
    skill_md = SKILL_DIR / "SKILL.md"
    assert skill_md.exists(), f"SKILL.md not found at {skill_md}"
    text = skill_md.read_text(encoding="utf-8")
    assert text.startswith("---"), "SKILL.md must start with YAML frontmatter delimiter"
    assert "name: gpt-image" in text, "frontmatter must declare name: gpt-image"

    # Frontmatter is everything between the first and second '---'.
    parts = text.split("---", 2)
    assert len(parts) >= 3, "SKILL.md must have a closing '---' for frontmatter"
    front = parts[1]
    assert "description:" in front, "frontmatter must have a description field"
    assert len(front) > 200, (
        f"frontmatter must be > 200 chars (got {len(front)})"
    )

    # At least one fenced code block somewhere in the body.
    assert "```" in text, "SKILL.md must contain at least one fenced code block"


def test_skill_shim_pep723_header():
    shim = SKILL_DIR / "scripts" / "run_skill.py"
    assert shim.exists(), f"shim not found at {shim}"
    source = shim.read_text(encoding="utf-8")
    first = source.splitlines()[0]
    assert first.startswith("# /// script"), (
        f"first line must be PEP 723 marker, got: {first!r}"
    )

    tree = ast.parse(source)
    assert any(
        isinstance(n, ast.FunctionDef) and n.name == "main" for n in tree.body
    ), "shim must define a top-level `def main`"

    # Ensure an `if __name__ == "__main__":` guard exists.
    has_main_guard = False
    for node in tree.body:
        if isinstance(node, ast.If):
            test = node.test
            if (
                isinstance(test, ast.Compare)
                and isinstance(test.left, ast.Name)
                and test.left.id == "__name__"
            ):
                has_main_guard = True
                break
    assert has_main_guard, 'shim must include an `if __name__ == "__main__":` block'


def test_shim_returns_127_when_cli_missing():
    shim = SKILL_DIR / "scripts" / "run_skill.py"
    # Spawn a fresh python process with a PATH that contains no `i2w`.
    env = {"PATH": "/nonexistent", "SYSTEMROOT": "/", "PYTHONIOENCODING": "utf-8"}
    result = subprocess.run(
        [sys.executable, str(shim), "version"],
        capture_output=True,
        text=True,
        env=env,
    )
    # When i2w is not on PATH the shim should exit non-zero (specifically 127).
    assert result.returncode != 0, (
        f"shim should fail when i2w missing; got rc=0, stdout={result.stdout!r}"
    )
    assert result.returncode == 127, (
        f"expected exit code 127 when i2w missing, got {result.returncode}"
    )
