# SPDX-License-Identifier: Apache-2.0
"""Exporters: write rendered prompts as markdown / json bundles / gallery sections."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .schema import TemplateSpec


def _hash_prompt(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def export_markdown(rendered: str, out: Path) -> None:
    """Write the rendered markdown prompt to disk (UTF-8, trailing newline)."""
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    body = rendered if rendered.endswith("\n") else rendered + "\n"
    out.write_text(body, encoding="utf-8")


def export_json(
    template: TemplateSpec,
    rendered: dict[str, str],
    out: Path,
    vars_: dict[str, Any] | None = None,
) -> None:
    """Write a json bundle: id, language renderings, vars, and per-lang hashes."""
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    bundle = {
        "id": template.id,
        "domain": template.domain,
        "artifact": {
            "type": template.artifact.type,
            "aspect": template.artifact.aspect,
            "size": template.artifact.size,
        },
        "api_mode": template.api_mode,
        "moderation": template.moderation,
        "language_targets": list(template.language_targets),
        "renderings": dict(rendered),
        "hashes": {lang: _hash_prompt(text) for lang, text in rendered.items()},
        "vars": vars_ or {},
    }
    out.write_text(
        json.dumps(bundle, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def export_gallery_section(
    domain: str,
    templates: list[tuple[TemplateSpec, dict[str, str]]],
) -> str:
    """Produce markdown for ``docs/gallery/<domain>.md`` (consumed by agent-10)."""
    lines: list[str] = []
    lines.append(f"# {domain.capitalize()} Gallery")
    lines.append("")
    lines.append(
        f"Bilingual prompt previews for the `{domain}` domain. "
        f"Generated from `templates/{domain}/*.yml`."
    )
    lines.append("")
    if not templates:
        lines.append("_No templates yet._")
        lines.append("")
        return "\n".join(lines)

    for template, renderings in templates:
        lines.append(f"## `{template.id}`")
        lines.append("")
        if template.description:
            lines.append(f"> {template.description}")
            lines.append("")
        lines.append(
            f"- artifact: **{template.artifact.type}** "
            f"({template.artifact.aspect}, {template.artifact.size})"
        )
        lines.append(f"- api_mode: `{template.api_mode}`")
        lines.append(f"- grader: `{template.grader_profile}`")
        lines.append("")
        for lang in template.language_targets:
            if lang not in renderings:
                continue
            heading = "Chinese (zh-CN)" if lang == "zh-CN" else "English (en)"
            lines.append(f"### {heading}")
            lines.append("")
            lines.append("```text")
            lines.append(renderings[lang].rstrip("\n"))
            lines.append("```")
            lines.append("")
    return "\n".join(lines)


__all__ = ["export_gallery_section", "export_json", "export_markdown"]
