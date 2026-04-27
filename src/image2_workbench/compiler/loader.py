# SPDX-License-Identifier: Apache-2.0
"""YAML loaders for templates and variable bundles."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .schema import TemplateSpec


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


__all__ = ["load_template", "load_vars"]
