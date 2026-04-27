# SPDX-License-Identifier: Apache-2.0
"""YAML loaders for templates and variable bundles."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .schema import TemplateSpec

# Directory name (relative to a template file's parent) that holds demo-vars
# YAML bundles for that domain. Centralised here so the resolver and any
# future tooling stay in sync.
DEMO_VARS_DIRNAME = "_vars_examples"


def load_template(path: Path) -> TemplateSpec:
    """Read a template YAML file and parse it into a TemplateSpec."""
    path = Path(path)
    with path.open("r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)
    if not isinstance(raw, dict):
        raise ValueError(f"template {path} must be a YAML mapping at the top level")
    return TemplateSpec.model_validate(raw)


def load_vars(path: Path) -> dict[str, Any]:
    """Read a vars YAML file and return a plain dict."""
    path = Path(path)
    with path.open("r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}
    if not isinstance(raw, dict):
        raise ValueError(f"vars file {path} must be a YAML mapping at the top level")
    return raw


def _is_skippable(name: str) -> bool:
    """True for filenames we should never treat as a demo-vars candidate."""
    return name.startswith(".") or name == ".gitkeep" or name == DEMO_VARS_DIRNAME


def resolve_demo_vars(
    template_path: Path,
    *,
    override: dict[str, str] | None = None,
) -> Path | None:
    """Locate the demo-vars YAML for ``template_path`` using convention-with-fallback.

    Resolution order:

    1. **Override**: if ``override`` is supplied and contains the key
       ``f"{template_path.parent.name}/{template_path.stem}"``, return the
       templates-root-relative path it maps to (resolved against
       ``template_path``'s grandparent — i.e. the templates root). This is
       the legacy escape hatch for V1 templates whose demo files don't
       follow the new convention.
    2. **Convention**: ``<template_stem>.yml`` inside the sibling
       ``_vars_examples/`` directory.
    3. **Convention with ``_demo`` suffix**: ``<template_stem>_demo.yml``.
    4. **Single-demo legacy fallback**: the first ``*.yml`` file in
       ``_vars_examples/`` (sorted by name) — useful for templates with
       exactly one demo whose filename predates the convention.

    Dotfiles, ``.gitkeep``, and the ``_vars_examples`` directory itself are
    always skipped. Returns ``None`` when nothing matches.
    """
    template_path = Path(template_path)

    if override is not None:
        rel_key = f"{template_path.parent.name}/{template_path.stem}"
        mapped = override.get(rel_key)
        if mapped is not None:
            # Override values are relative to the templates root, which is
            # the grandparent of the template file (templates/<domain>/x.yml).
            templates_root = template_path.parent.parent
            candidate = templates_root / mapped
            return candidate if candidate.is_file() else None

    vars_dir = template_path.parent / DEMO_VARS_DIRNAME
    if not vars_dir.is_dir():
        return None

    stem = template_path.stem

    # Priority 2: <stem>.yml
    convention = vars_dir / f"{stem}.yml"
    if convention.is_file() and not _is_skippable(convention.name):
        return convention

    # Priority 3: <stem>_demo.yml
    demo_suffix = vars_dir / f"{stem}_demo.yml"
    if demo_suffix.is_file() and not _is_skippable(demo_suffix.name):
        return demo_suffix

    # Priority 4: first *.yml in directory (legacy single-demo case).
    # iterdir is intentional (vs rglob) so an accidental
    # _vars_examples/_vars_examples nesting can't trigger recursion.
    candidates = sorted(
        p
        for p in vars_dir.iterdir()
        if p.is_file() and p.suffix == ".yml" and not _is_skippable(p.name)
    )
    if candidates:
        return candidates[0]

    return None


__all__ = [
    "DEMO_VARS_DIRNAME",
    "load_template",
    "load_vars",
    "resolve_demo_vars",
]
